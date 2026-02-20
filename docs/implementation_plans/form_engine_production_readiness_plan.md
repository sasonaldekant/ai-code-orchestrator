# Projekat: Form Studio Production Readiness (Faza Utezanje)

## 1. Analiza Trenutnog Stanja: Nepoklapanje Preview-a i Generisanog Koda

### 1.1 Šta je problem sa Preview-om?
U okviru **Form Studio** taba (playground-u gde se vrši pregled), [FormStudioTab.tsx](file:///c:/Users/mgasic/Documents/AIProjects/ai-code-orchestrator/ui/src/components/FormStudioTab.tsx) trenutno koristi pojednostavljenu, *hardkodovanu logiku* za layout (`grid-cols-1 md:grid-cols-2`), gde svaki element zauzima 1 kolonu (pa stanu po 2 na ekranu), dok samo `textarea` dobija `md:col-span-2`. 
S druge strane, generisani **Form Engine** kôd (koji se exportuje u Vite) koristi pravu `12-column` CSS/DynBox grid implementaciju gde svako polje ima `colSpan` (`full`, `half`, `third`, `quarter`) kojeg na backendu donosi **AI Architect Agent**. 
**Rezultat:** Ono što vidite u preview-u NIJE ono što na kraju dobijete jer preview uopšte ne mapira `colSpan` koji donese AI, niti koristi 12-column sistem, dok je spacing (gap-4 vs gap="sm") neujednačen.

### 1.2 Šta je problem sa AI Agentom (Layout Architect)?
Prompt u `specialists.py:FormArchitectSpecialist` jeste podučen da koristi `full`, `half`, `third`, `quarter`, ali nema strogi uslov da procenjuje dužinu komponente na osnovu validacija.
**Rešenje:** Moramo proširiti prompt jasnim instrukcijama:
- *Uvek probaj da smestiš minimum 2 (ili 3) elementa u horizontalni red (`half` ili `third`)* osim ako polje eksplicitno ne zahteva širinu (adrese, dug tekst). 
- *Koristi parametre polja poput `maxLength` ili semantička pravila*: Ako je polje JMBG, Telefon, PIB, Poštanski broj -> koristi `quarter` ili `third`.

## 2. Revizija RAG-a i Dokumentacije

Trenutno posedujemo sledeći kontekst u RAG direktorijumu:
- [AI_CONTEXT.md](file:///c:/Users/mgasic/Documents/AIProjects/ai-code-orchestrator/rag/AI_CONTEXT.md) (veoma dobro definisana DynBox pravila za agente)
- [domain_docs/backend.md](file:///c:/Users/mgasic/Documents/AIProjects/ai-code-orchestrator/rag/domain_docs/backend.md), [devops.md](file:///c:/Users/mgasic/Documents/AIProjects/ai-code-orchestrator/rag/domain_docs/devops.md), [frontend.md](file:///c:/Users/mgasic/Documents/AIProjects/ai-code-orchestrator/rag/domain_docs/frontend.md) (svi su `1-line` placeholderi koji nisu korisni).

**Problem:** Zato agent ne pronalazi RAG! Placeholderi nemaju sadržaj sa kojim Semantička pretraga (Embeddings) može da upari (match) user upit. Takođe obavezno pregledati da li agent koristi prave markdown putanje.

## 3. Plan Rešavanja i Finalizacije (Utezanje)

### Korak 1: Izjednačavanje Playground-a i FormEngine-a (UI/UX Utezanje)
- 🔴 Prepraviću [PreviewFieldRenderer](file:///c:/Users/mgasic/Documents/AIProjects/ai-code-orchestrator/ui/src/components/FormStudioTab.tsx#199-232) i nadležnu `div` strukturu unutar [FormStudioTab.tsx](file:///c:/Users/mgasic/Documents/AIProjects/ai-code-orchestrator/ui/src/components/FormStudioTab.tsx) da umesto grid-cols-2 kreira *pravu 12-column CSS Grid mrežu* (slično kao `<DynBox display="grid" gridTemplateColumns="repeat(12, 1fr)" gap="sm">`).
- 🔴 Prilagodiću margine i paddinge u playgroundu (`gap-4` u Tailwind će postati standardna CSS varijabla `--dyn-spacing-sm` odnosno `gap-sm`).
- 🔴 UI Preview će **obavezno** čitati `preview.fieldMeta.layout.span` ili generisani `layout` koji prilaže AI Architect. Znači AI layout se testira na licu mesta!

### Korak 2: Prompt Engineering za AI Layout (Form Architect)
- 🔴 Editovati [specialists.py](file:///c:/Users/mgasic/Documents/AIProjects/ai-code-orchestrator/core/form_engine/specialists.py) prompt tako da zahteva procenu na osnovu maxlength i formata (JMBG/PIB/Phone = max third, obavezno horizontalno pakovanje sa minimum 2-3 inputa u redu ukoliko ima mesta). U defaultu ne gurati 100% širinu.

### Korak 3: Čišćenje i Konsolidacija Koda (Legacy i RAG)
- 🔴 Ukloniću staru verziju `apps/form-engine` iz probnog Workspace-a `dyn-ui-main-v01` pošto ga sada formalno hostujemo u `outputs/forms-workspace/packages/form-engine`. 
- 🔴 RAG dokumentacija će se proširiti sa tačnim putanjama do naših patterna i prekopiraćemo DynUI pravila iz `AI_CONTEXT.md` u sve ostale fallback dokumente ako treba.

Molim te pregledaj plan. Ukoliko ti se sviđa, odmah uskačem u **Korak 1** i prepisujem playground komponentu da prati 100% generisanu logiku!
