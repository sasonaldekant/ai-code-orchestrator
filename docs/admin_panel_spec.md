# AI Orchestrator Admin Panel - Implementation Plan

## 1. Executive Summary

Ovaj plan opisuje implementaciju **Admin Panel** sekcije u Nexus GUI, koja će omogućiti konfiguraciju i upravljanje Orchestrator-om bez direktnog editovanja YAML fajlova ili pisanja Python koda.

**Ključne oblasti:**

1. **RAG Ingestion Manager** - unos i validacija podataka za RAG
2. **Model Configuration** - vizuelno podešavanje modela po fazama
3. **Budget & Limits** - upravljanje troškovima i limitima
4. **Knowledge Base Explorer** - pregled i brisanje kolekcija

### DynUI Component Library Reference

> [!NOTE]
> Admin Panel koristi **DynUI** komponentnu biblioteku za konzistentan UI.
> 
> **Lokacija dokumentacije:** `c:\Users\mgasic\Documents\AIProjects\dyn-ui-main-v01\docs\rag-ready\`
> 
> **Ključni dokumenti:**
> - `03-COMPONENT_CATALOG.md` - Katalog svih 45 komponenti
> - `02-DESIGN_TOKENS.md` - Design tokeni (boje, spacing, veličine)
> - `05-CODE_EXAMPLES.md` - Primeri upotrebe
> 
> **Import pattern:** `import { ComponentName } from '@dyn-ui/react'`

---

## 2. Administrable Features (Based on Codebase Analysis)

### 2.1 RAG Knowledge Ingestion

**Izvor:** `api/app.py` → `/ingest` endpoint, `domain_knowledge/ingestion/`

| Feature                     | Backend Support            | GUI Potrebe                                |
| --------------------------- | -------------------------- | ------------------------------------------ |
| Database Schema Ingestion   | `DatabaseSchemaIngester`   | Path selector, Models dir, Collection name |
| Component Library Ingestion | `ComponentLibraryIngester` | Path selector, Collection name             |
| Generic File Ingestion      | Potrebna implementacija    | File upload, Format selector, Chunk size   |

**Validacija Inputa:**

- Provera da putanja postoji na file sistemu
- Validacija formata (C# za DB, TSX/JSX za komponente)
- Optimizacija chunk veličine za minimizaciju tokena:
  - Preporučeno: `chunk_chars: 800`, `chunk_overlap: 120` (iz `limits.yaml`)
- Preview pre ingesta (broj dokumenata, procenjena veličina)

---

### 2.2 Model Configuration

**Izvor:** `config/model_mapping_v2.yaml`

| Configurable Item      | Current Value     | GUI Control             |
| ---------------------- | ----------------- | ----------------------- |
| Default Model          | `gpt-4o-mini`     | Dropdown                |
| Phase→Model Mapping    | Per-phase config  | Table/Cards             |
| Consensus Mode         | `architect` phase | Toggle + Multi-select   |
| Temperature            | 0.0-1.0           | Slider                  |
| Max Tokens             | 1000-100000       | Input                   |
| Producer-Reviewer Loop | `reviewer` phase  | Toggle + Max Iterations |

**Primer GUI Kartice za Fazu:**

```
┌─────────────────────────────────────────────┐
│  📊 ARCHITECT PHASE                         │
├─────────────────────────────────────────────┤
│  Mode: [●] Consensus  [ ] Single Model      │
│                                             │
│  Primary:   [claude-3-5-sonnet ▼] Weight: 0.5│
│  Secondary: [gpt-4o ▼]           Weight: 0.3│
│  Tertiary:  [gemini-2.5-pro ▼]   Weight: 0.2│
│                                             │
│  Synthesis Model: [claude-3-5-sonnet ▼]     │
└─────────────────────────────────────────────┘
```

---

### 2.3 Budget & Limits

**Izvor:** `config/limits.yaml`, `config/model_mapping_v2.yaml` (cost_management)

| Setting           | Config Key                                       | GUI Control    |
| ----------------- | ------------------------------------------------ | -------------- |
| Max Input Tokens  | `budgets.max_input_tokens`                       | Input (6000)   |
| Max Output Tokens | `budgets.max_output_tokens`                      | Input (1000)   |
| Retrieval Top-K   | `retrieval.top_k`                                | Slider (1-20)  |
| Chunk Size        | `retrieval.chunk_chars`                          | Input (800)    |
| Chunk Overlap     | `retrieval.chunk_overlap`                        | Input (120)    |
| Per-Task Budget   | `cost_management.budgets.per_task`               | Input ($0.50)  |
| Per-Day Budget    | `cost_management.budgets.per_day`                | Input ($40.00) |
| Cache TTL         | `cost_management.optimization.cache_ttl_seconds` | Input (3600)   |

---

### 2.4 Knowledge Base Explorer

**Izvor:** `rag/vector_store.py` → `ChromaVectorStore`

| Feature           | Method                   | GUI                  |
| ----------------- | ------------------------ | -------------------- |
| List Collections  | Potreban novi endpoint   | Table                |
| Collection Stats  | `get_collection_stats()` | Cards                |
| Delete Collection | `delete_collection()`    | Button + Confirm     |
| Query Collection  | `search()`               | Search box + Results |

---

## 3. Backend API Extensions Required

### Novi Endpointi:

```python
# 1. Config Read/Write
GET  /admin/config/{config_name}     # Čita YAML kao JSON
POST /admin/config/{config_name}     # Zapisuje JSON kao YAML

# 2. Knowledge Base Management
GET  /admin/collections              # Lista svih kolekcija
GET  /admin/collections/{name}/stats # Statistike kolekcije
DELETE /admin/collections/{name}     # Briše kolekciju

# 3. Ingestion with Validation
POST /admin/ingest/validate          # Dry-run, vraća preview
POST /admin/ingest/execute           # Stvarna ingestion

# 4. File System Access (Local)
GET  /admin/browse?path=...          # Lista fajlova/foldera
```

---

## 4. Frontend Implementation Plan

### 4.1 Component Structure

```
ui/src/components/admin/
├── AdminLayout.tsx          # Left nav + content area
├── IngestionPanel.tsx       # RAG data ingestion
│   ├── PathSelector.tsx     # Browse folders
│   ├── IngestionPreview.tsx # Dry-run results
│   └── ChunkSettings.tsx    # Chunk config
├── ModelConfigPanel.tsx     # Phase/model mapping
│   └── PhaseCard.tsx        # Individual phase config
├── BudgetPanel.tsx          # Limits and budgets
└── KnowledgeExplorer.tsx    # Collections browser
    ├── CollectionCard.tsx
    └── SearchResults.tsx
```

### 4.2 UI Mockup - Admin Layout

```
┌────────────────────────────────────────────────────────────┐
│  ⚙️ Admin Settings                              [← Back]   │
├──────────────┬─────────────────────────────────────────────┤
│              │                                             │
│  📥 Ingestion│  ┌─────────────────────────────────────┐    │
│              │  │  RAG Knowledge Ingestion            │    │
│  🤖 Models   │  │                                     │    │
│              │  │  Type: [Database Schema ▼]          │    │
│  💰 Budgets  │  │                                     │    │
│              │  │  Path: [E:\Project\Data     ] [📁]  │    │
│  📚 Knowledge│  │  Models: [E:\Project\Models ] [📁]  │    │
│              │  │  Collection: [pos_database_schema]  │    │
│              │  │                                     │    │
│              │  │  ─── Chunk Settings ───             │    │
│              │  │  Size: [800] chars                  │    │
│              │  │  Overlap: [120] chars               │    │
│              │  │                                     │    │
│              │  │  [Validate] [Ingest Knowledge →]    │    │
│              │  └─────────────────────────────────────┘    │
│              │                                             │
│              │  ┌─────────────────────────────────────┐    │
│              │  │ Validation Result                   │    │
│              │  │ ✓ Path exists                       │    │
│              │  │ ✓ 15 entities found                 │    │
│              │  │ ✓ Est. 45 documents, ~36K tokens    │    │
│              │  └─────────────────────────────────────┘    │
└──────────────┴─────────────────────────────────────────────┘
```

---

## 5. Implementation Roadmap

### Phase 1: Backend API (1-2 sessions)

1. [ ] Create `api/admin_routes.py`
2. [ ] Implement `/admin/config/{name}` (GET/POST)
3. [ ] Implement `/admin/collections` endpoints
4. [ ] Implement `/admin/ingest/validate`
5. [ ] Implement `/admin/browse` (local file browser)

### Phase 2: Frontend Foundation (1-2 sessions)

1. [ ] Create `AdminLayout.tsx` with side navigation
2. [ ] Add "Settings" icon/link in Nexus sidebar
3. [ ] Routing between main GUI and Admin panel

### Phase 3: Ingestion Panel (1 session)

1. [ ] `IngestionPanel.tsx` with form
2. [ ] `PathSelector.tsx` using `/admin/browse`
3. [ ] Validation preview display
4. [ ] Execute ingestion with progress

### Phase 4: Model & Budget Panels (1-2 sessions)

1. [ ] `ModelConfigPanel.tsx` - read/edit `model_mapping_v2.yaml`
2. [ ] `BudgetPanel.tsx` - read/edit `limits.yaml`
3. [ ] Save confirmation and reload

### Phase 5: Knowledge Explorer (1 session)

1. [ ] `KnowledgeExplorer.tsx` - list collections
2. [ ] Stats display per collection
3. [ ] Delete with confirmation
4. [ ] Basic search/query

---

## 6. Validation & Optimization Logic

Za maksimalnu efikasnost tokena pri ingestion-u:

### Input Validation Rules:

1. **Path Validation**: Proveri da folder/fajl postoji pre slanja
2. **Format Detection**: Auto-detect tip na osnovu ekstenzije (.cs, .tsx)
3. **Size Estimation**: Pre ingesta, izračunaj:
   - Broj fajlova
   - Ukupan broj karaktera
   - Procenjeni broj dokumenata (chunks)
   - Procenjeni tokeni za embedding

### Optimization Recommendations UI:

```
┌─────────────────────────────────────────────┐
│ ⚡ Optimization Recommendations             │
├─────────────────────────────────────────────┤
│ • Current chunk size (800) is optimal       │
│ • Consider reducing overlap to 100 for      │
│   10% token savings                         │
│ • Large files detected: consider filtering  │
│   generated files (*.g.cs)                  │
└─────────────────────────────────────────────┘
```

---

## 7. Security Considerations

> [!WARNING]
>
> - File system access (`/admin/browse`) ograničiti na project root
> - Config write (`POST /admin/config`) validirati strukturu pre pisanja
> - U produkciji, Admin panel zahteva autentifikaciju

---

## 8. Next Steps

1. **User Review**: Potvrdi prioritete (koje panele prvo?)
2. **Backend First**: Implementirati API pre GUI
3. **Iterativno**: Svaki panel kao zasebna celina
