"""
Form Studio AI Chat Service.

Provides context-aware AI chat focused exclusively on JSON form schemas
and DynUI component configuration. Reuses existing RAG and LLM infrastructure.
"""

import json
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict

from core.llm_client_v2 import LLMClientV2
from core.cost_manager import CostManager
from rag.domain_aware_retriever import DomainAwareRetriever

logger = logging.getLogger(__name__)


@dataclass
class ChatMessage:
    role: str  # "user" | "assistant"
    content: str


@dataclass
class ChatResponse:
    reply: str
    updated_schema: Optional[Dict[str, Any]] = None
    schema_diff: Optional[Dict[str, Any]] = None
    rag_sources: List[str] = field(default_factory=list)
    ui_hints: Optional[Dict[str, Any]] = None


FORM_CHAT_SYSTEM_PROMPT = """Ti si AI asistent specijalizovan ISKLJUČIVO za JSON form šeme i DynUI komponente.

## Tvoja uloga
- Pomažeš korisniku da fino podesi JSON šemu forme
- Razumeš DynUI komponentni sistem, tokene i layout standarde
- Predlažeš promene kroz konkretan JSON format
- Možeš da "vidiš" raspored forme kroz strukturni prikaz ispod

## Striktna ograničenja
- NIKAD ne odgovaraj na pitanja koja nisu vezana za formu, JSON šemu ili DynUI
- Uvek koristi DynUI design tokene (var(--dyn-*)), NIKAD hardkodirane vrednosti
- Koristi SAMO validne field tipove: text, number, email, tel, date, dropdown, radio, checkbox, textarea
- Layout colSpan vrednosti: full (12col), half (6col), third (4col), quarter (3col)

## Format odgovora
Kada predlažeš promenu šeme, odgovori u JSON formatu:
{{
  "explanation": "Kratak opis promene na srpskom",
  "updated_schema": {{ ... kompletna ažurirana šema ... }},
  "changes": [
    {{"field": "fieldId", "property": "layout.colSpan", "from": "half", "to": "third"}}
  ]
}}

Ako korisnik pita za objašnjenje (ne menja šemu), odgovori normalno tekstom.

## RAG Kontekst
Ispod je dostupna dokumentacija iz DynUI RAG sistema. Koristi je za tačne informacije:
{rag_context}

## Trenutna JSON Šema
{current_schema}

## Preview Stanje
Layout: {preview_layout}
Kompleksnost: {preview_complexity}
Broj polja: {field_count}

## Strukturni Prikaz Forme (kako forma vizuelno izgleda)
{layout_map}
"""


class FormChatService:
    """
    AI Chat 100% fokusiran na JSON form context.
    Reuse-uje postojeći RAG (DomainAwareRetriever) + LLM (LLMClientV2).
    """

    def __init__(
        self,
        llm_client: Optional[LLMClientV2] = None,
        cost_manager: Optional[CostManager] = None,
        retriever: Optional[DomainAwareRetriever] = None,
    ):
        cm = cost_manager or CostManager()
        self.llm_client = llm_client or LLMClientV2(cm)
        self.retriever = retriever or DomainAwareRetriever()

    def _build_layout_map(self, schema: Dict[str, Any], inferred_sections: Optional[List[Dict[str, Any]]] = None) -> str:
        """Build a detailed text-based layout map showing how the form visually appears."""
        # Use inferred sections from the preview engine if available (prioritize what the user SEES)
        if inferred_sections and isinstance(inferred_sections, list):
            sections = inferred_sections
        else:
            # Fallback to schema structure
            sections = schema.get("sections", [])
            if not sections:
                form_data = schema.get("form", {})
                if isinstance(form_data, dict):
                    sections = form_data.get("sections", [])
                
            if not sections:
                # Try flat fields at various levels
                fields = schema.get("fields", [])
                if not fields and isinstance(schema.get("form"), dict):
                    fields = schema.get("form", {}).get("fields", [])
                
                if fields:
                    sections = [{"title": "Form", "fields": fields}]

        if not sections:
            return "Nema sekcija ili polja u šemi."

        lines = []
        # Support both numeric and named spans
        span_map = {
            "full": 12, "12": 12, 12: 12,
            "half": 6, "6": 6, 6: 6,
            "third": 4, "4": 4, 4: 4,
            "quarter": 3, "3": 3, 3: 3
        }

        for section in sections:
            if not section: continue
            title = section.get("title", "Untitled")
            lines.append(f"┌── SEKCIJA: {title} ──┐")

            row_cols = 0
            row_fields = []

            for field in section.get("fields", []):
                fid = field.get("id", "?")
                ftype = field.get("type", "text")
                label = field.get("label", fid)
                
                # In inferred sections, layout is often nested differently (from mapper.py)
                layout = field.get("layout", {})
                span_name = layout.get("span", layout.get("colSpan", field.get("colSpan", field.get("span", "full"))))
                
                cols = span_map.get(str(span_name).lower(), span_map.get(span_name, 12))
                req = "*" if field.get("required") else ""

                entry = f"[{fid}:{ftype} ({span_name})]{req}"

                if row_cols + cols > 12:
                    # Flush current row (max 12 columns per row in grid)
                    if row_fields:
                        lines.append(f"│  {' | '.join(row_fields)}")
                    row_fields = [entry]
                    row_cols = cols
                else:
                    row_fields.append(entry)
                    row_cols += cols

            if row_fields:
                lines.append(f"│  {' | '.join(row_fields)}")

            lines.append(f"└{'─' * 40}┘")

        return "\n".join(lines)

    async def chat(
        self,
        message: str,
        current_schema: Dict[str, Any],
        chat_history: List[Dict[str, str]],
        preview_state: Optional[Dict[str, Any]] = None,
    ) -> ChatResponse:
        """
        Process a user chat message in the context of the current JSON schema.
        Returns AI reply + optional schema updates.
        """
        preview_state = preview_state or {}

        # 1. RAG retrieval — Tier 2 (tokens) + Tier 3 (components)
        rag_docs: List[Dict[str, Any]] = []
        try:
            tier2_docs = self.retriever.retrieve_tier(2, message, top_k=3)
            tier3_docs = self.retriever.retrieve_tier(3, message, top_k=3)
            rag_docs = tier2_docs + tier3_docs
        except Exception as e:
            logger.warning(f"RAG retrieval failed (non-fatal): {e}")

        rag_context_str = "\n".join(
            f"[{d.get('metadata', {}).get('type', 'doc')}] {d.get('content', '')[:500]}"
            for d in rag_docs
        ) or "Nema dostupnog RAG konteksta."

        rag_sources = [
            d.get("source", d.get("metadata", {}).get("source", "unknown"))
            for d in rag_docs
        ]

        # 2. Build layout map — a structural view of the form for the AI
        inferred = preview_state.get("inferredSections")
        layout_map = self._build_layout_map(current_schema, inferred_sections=inferred)

        # 3. Build system prompt with full context
        schema_str = json.dumps(current_schema, indent=2, ensure_ascii=False)
        system_prompt = FORM_CHAT_SYSTEM_PROMPT.format(
            rag_context=rag_context_str,
            current_schema=schema_str,
            preview_layout=preview_state.get("layout", "auto"),
            preview_complexity=preview_state.get("complexity", "unknown"),
            field_count=preview_state.get("fieldCount", "?"),
            layout_map=layout_map,
        )

        # 3. Compose messages (keep last 10 history messages for context window)
        messages = [{"role": "system", "content": system_prompt}]
        for msg in chat_history[-10:]:
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": message})

        # 4. LLM call — use fast model for responsive chat UX
        try:
            response = await self.llm_client.complete(
                messages=messages,
                model="gpt-4o-mini",
                temperature=0.3,
                max_tokens=4000,
                bypass_cache=True,
                tier="form_chat",
            )
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            return ChatResponse(
                reply=f"Greška pri pozivu AI modela: {str(e)}",
                rag_sources=rag_sources,
            )

        # 5. Extract content from LLM response
        raw_content = ""
        if hasattr(response, 'content'):
            raw_content = response.content or ""
        elif isinstance(response, dict):
            raw_content = response.get("content", "")
        content = raw_content.strip()

        # 6. Parse response — handle markdown-wrapped JSON (```json...```)
        updated_schema = None
        schema_diff = None

        # Strip markdown code fences if present
        json_str = content
        if "```json" in json_str:
            start = json_str.index("```json") + 7
            end = json_str.index("```", start) if "```" in json_str[start:] else len(json_str)
            json_str = json_str[start:end].strip()
        elif "```" in json_str and json_str.strip().startswith("```"):
            lines = json_str.strip().split("\n")
            json_str = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:]).strip()

        try:
            parsed = json.loads(json_str)
            if isinstance(parsed, dict) and "updated_schema" in parsed:
                updated_schema = parsed["updated_schema"]
                schema_diff = {
                    "changes": parsed.get("changes", []),
                    "explanation": parsed.get("explanation", ""),
                }
                reply = parsed.get("explanation", "Šema je ažurirana.")
            else:
                reply = content
        except (json.JSONDecodeError, ValueError):
            reply = content

        return ChatResponse(
            reply=reply,
            updated_schema=updated_schema,
            schema_diff=schema_diff,
            rag_sources=rag_sources,
        )

    def generate_enriched_prompt(
        self,
        current_schema: Dict[str, Any],
        chat_history: List[Dict[str, str]],
        preview_state: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Summarize all chat-refined details into enriched instructions
        that the orchestrator will use during project generation.
        """
        preview_state = preview_state or {}
        key_decisions: List[str] = []
        architectural_hints: List[str] = []
        user_preferences: List[str] = []

        # Analyze interaction history for "Architectural Intent"
        for msg in chat_history:
            content = msg["content"].strip()
            if not content: continue
            
            if msg["role"] == "user":
                lower_content = content.lower()
                # 1. Capture direct layout/structure decisions
                if any(kw in lower_content for kw in ["layout", "kolona", "third", "half", "quarter", "full", "grid", "pomeri", "stavi"]):
                    key_decisions.append(f"PROSTORNI ZAHTEV: {content}")
                # 2. Capture business logic / validation
                elif any(kw in lower_content for kw in ["validaci", "required", "obavez", "pattern", "format", "email", "regex"]):
                    key_decisions.append(f"POSLOVNA LOGIKA: {content}")
                # 3. Capture specific UX requests
                elif any(kw in lower_content for kw in ["boja", "dugme", "stil", "naslov", "opis", "placeholder"]):
                    architectural_hints.append(f"UX PREFERENCIJA: {content}")
                else:
                    user_preferences.append(content)
            
            elif msg["role"] == "assistant":
                # Only capture assistant reasoning if it contains "Zašto" or architectural advice
                if "preporučujem" in content.lower() or "bolje je" in content.lower():
                    architectural_hints.append(f"AI PREPORUKA (Prihvaćena): {content[:200]}...")

        schema_str = json.dumps(current_schema, indent=2, ensure_ascii=False)
        metadata = current_schema.get("metadata", {})
        title = metadata.get('title', metadata.get('name', 'Nova Forma'))

        enriched_prompt = f"""# DETALJNE INSTRUKCIJE ZA GENERISANJE PROJEKTA: {title}

Ovaj prompt je rezultat interaktivne chat sesije u Form Studiju. 
Agente, koristi ove instrukcije kao PRIORITET nad generičkim templejtima.

## 1. KONTEKST FORME
- Naziv: {title}
- Ciljni Layout: {preview_state.get('layout', 'standard')}
- Očekivana Kompleksnost: {preview_state.get('complexity', 'medium')}
- Broj definisanih polja: {preview_state.get('fieldCount', '?')}

## 2. KLJUČNE ODLUKE I ITERACIJE IZ CHAT-A
{chr(10).join(f'- {d}' for d in key_decisions) if key_decisions else '- Koristiti default raspored iz JSON šeme.'}

## 3. ARHITEKTONSKE I UX SMERNICE
- Koristiti ISKLJUČIVO DynUI design tokene (var(--dyn-color-*, var(--dyn-spacing-*, itd.).
{chr(10).join(f'- {h}' for h in architectural_hints) if architectural_hints else '- Pratiti standardne DynUI pattern-e.'}
{chr(10).join(f'- {p}' for p in user_preferences) if user_preferences else ''}

## 4. TEHNIČKA SPECIFIKACIJA (JSON ŠEMA)
Ovaj JSON je FINALNI izvor istine za strukturu, tipove i validacije:
```json
{schema_str}
```

## 5. ZADATAK ZA INSTRUKCIJE AGENTA (Architect/Implementation)
1. Analiziraj `colSpan` vrednosti u `layout` objektu svakog polja. 
2. Ako je `colSpan` 'half', postavi dva polja u isti red.
3. Obavezno implementiraj sve `validation` objekte (npr. custom poruke, regex).
4. Ako polje ima `showWhen` logiku, generiši odgovarajući React state i uslovni render.
5. Osiguraj da submit akcija ispravno prikuplja podatke iz svih polja.
"""

        summary = (
            f"Enriched prompt generisan na osnovu {len(chat_history)} poruka. "
            f"Snimljeno {len(key_decisions)} konkretnih odluka za layout i logiku. "
            f"Spreman za prelazak u fazu Architect agenta."
        )

        return {
            "enriched_prompt": enriched_prompt,
            "summary": summary,
            "key_decisions": key_decisions + architectural_hints,
        }
