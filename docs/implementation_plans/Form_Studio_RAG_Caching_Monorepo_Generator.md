# Form Studio: RAG Caching + Monorepo Generator

Cilj: Eliminisati ponovljene tokene za generisanje identičnih/sličnih projektnih struktura i konsolidovati sve generisane forme u jedan zajednički monorepo.

## Pozadina

Trenutno svaki klik na "Approve & Generate" kreira novi **potpuno izolovan** React/Vite projekat (sa sopstvenim [package.json](file:///c:/Users/mgasic/Documents/AIProjects/dyn-ui-main-v01/package.json), [tsconfig.json](file:///c:/Users/mgasic/Documents/AIProjects/dyn-ui-main-v01/tsconfig.json), `vite.config.ts`, itd). Svaki od ovih fajlova je identičan za sve forme — jedino što se razlikuje je samа [.tsx](file:///c:/Users/mgasic/Documents/AIProjects/ai-code-orchestrator/ui/src/App.tsx) komponenta sa formom.

Dva problema:
1. **AI tokeni se troše na regenerisanje istih strukturnih fajlova** (package.json, vite config...) iznova i iznova.
2. **Svaki generisani projekat je odvojen svet** — teško je upravljati, testirati i deployovati više formi paralelno.

## Predložena Arhitektura

### Komponenta 1: Monorepo Skeleton (static, jednom kreiran)

> **`apps/` je inicijalno PRAZAN.** Svaka generacija novog JSON šablona dodaje novi `apps/<form-name>/` unutar njega.

```
forms-workspace/          ← Jednom inicijalizovan, ostaje trajno
├── package.json          ← Turborepo + pnpm workspaces
├── turbo.json
├── apps/                 ← Prazno na startu! Raste sa svakim jsonom
│   ├── registration/     ← Generiše se pritiskom na Approve & Generate
│   │   └── src/
│   │       ├── Form.tsx       ← UI forma (regeneriše se)
│   │       ├── api.ts         ← API pozivi za init/submit (regeneriše se)
│   │       ├── calculations.ts ← Računske operacije (regeneriše se)
│   │       └── App.tsx
│   └── osiguranje/            ← Drugi JSON, drugi app
│       └── src/
│           ├── Form.tsx
│           ├── api.ts         ← POST/PUT na osiguravajući API
│           └── calculations.ts ← Kalkulacija premije
└── packages/
    └── shared-ui/        ← Deljeni DynUI themes, ThemeProvider
```

**Svaki generisani `apps/<form>/` sadrži:**
- `Form.tsx` — DynUI forma sa vidljivošću polja i validacijom
- `api.ts` — Inicijalizacija forme (GET za popunjavanje dropdown-a), submit handler (POST/PUT), error handling
- `calculations.ts` — Sve poreske, premijske ili druge kalkulacije specifične za tu formu
- `schema.ts` — Zod output schema za validaciju pre slanja API-ju


### Komponenta 2: Dvoslojni RAG Cache

> **Logika (api.ts, calculations.ts) i UI (Form.tsx) se keširaju odvojeno.** Cilj je da UI shell može biti ponuđen u više varijanti, a logika živi za sebe.

**Sloj 1: JSON Schema Cache**
- Svaki odobren JSON template (fingerprint = SHA256 nad field typovima + layoutom) se čuva u ChromaDB.
- Sledeća forma sličnog oblika (npr. ista polja, drugačije labele) dobija predlog: *"Pronašao sam sličan template. Koristiti kao bazu?"*
- Čuvamo i originalni JSON i sve njegove verzije tokom vremena.

**Sloj 2: UI Varijante Cache**
- Za isti JSON template keširamo **više UI rešenja** koja su bila generisana (Standard, Tabs, Stepper).
- Korisnik može birati između keširovanih varijanti bez ponovnog generisanja:
  ```
  osiguranje.json → Form.tabs.tsx (cached)
                  → Form.stepper.tsx (cached)
                  → Form.standard.tsx (cached)
  ```
- Svaka varijanta je odvojena od `api.ts` i `calculations.ts` koji ostaju nepromenjeni.


---

## Predložene Izmene

### Komponenta A: Monorepo Skeleton Generator

#### [MODIFY] [project_generator.py](file:///c:\Users\mgasic\Documents\AIProjects\ai-code-orchestrator\core\form_engine\project_generator.py)
- Provera da li `forms-workspace/` postoji; ako da, koristi se (skip kreacije skeleton-a)
- [generate_project_base()](file:///c:/Users/mgasic/Documents/AIProjects/ai-code-orchestrator/core/form_engine/project_generator.py#128-155) sada kreira **samo** `apps/<form-name>/src/` unutar monorepa
- Template [package.json](file:///c:/Users/mgasic/Documents/AIProjects/dyn-ui-main-v01/package.json) za svaku app sadrži samo ime projekta + ref na `packages/shared-ui`

#### [NEW] [monorepo_initializer.py](file:///c:\Users\mgasic\Documents\AIProjects\ai-code-orchestrator\core\form_engine\monorepo_initializer.py)
- `FormMonorepoInitializer.ensure_workspace()` - Jednom kreira Turborepo skeleton
- Generiše [turbo.json](file:///c:/Users/mgasic/Documents/AIProjects/dyn-ui-main-v01/turbo.json), root [package.json](file:///c:/Users/mgasic/Documents/AIProjects/dyn-ui-main-v01/package.json), i `packages/shared-ui/`
- Detektuje da li je workspace već inicijalizovan (`.forms-workspace-manifest.json`)

---

### Komponenta B: RAG Caching za Generated Code

#### [NEW] [form_cache.py](file:///c:\Users\mgasic\Documents\AIProjects\ai-code-orchestrator\core\form_engine\form_cache.py)
```python
class FormProjectCache:
    def compute_fingerprint(template) -> str
        # SHA256 nad: field IDs + types + layout
    
    def lookup(fingerprint) -> str | None
        # Traži u ChromaDB po fingerprint-u
    
    def store(fingerprint, generated_code, template)
        # Čuva fingerprint + tsx kod u ChromaDB
```

#### [MODIFY] [orchestrator.py](file:///c:\Users\mgasic\Documents\AIProjects\ai-code-orchestrator\core\form_engine\orchestrator.py)
```
generate_ui_project():
  1. Compute fingerprint
  2. Cache lookup → HIT → kopiraj iz cache (0 AI tokena)
                 → MISS → generiši normalno, pa store u cache
```

---

### Komponenta C: API + UI Promena

#### [MODIFY] [form_routes.py](file:///c:\Users\mgasic\Documents\AIProjects\ai-code-orchestrator\api\form_routes.py)
- Dodati `cache_hit: bool` i `tokens_saved: int` u response za `/forms/generate`

#### [MODIFY] [FormStudioTab.tsx](file:///c:\Users\mgasic\Documents\AIProjects\ai-code-orchestrator\ui\src\components\FormStudioTab.tsx)
- Vizualni indikator "⚡ Cache Hit (0 tokens)" umesto normalnog "Generated" statusa

---

## Verifikacioni Plan

### Automatski testovi
- Generisati isti JSON template dva puta i proveriti da je `cache_hit: true` na drugom pozivu
- Proveriti da se [.tsx](file:///c:/Users/mgasic/Documents/AIProjects/ai-code-orchestrator/ui/src/App.tsx) fajlovi u monorep-u razlikuju samo za sadržaj komponente
- Proveriti da monorepo skeleton nije dupliran

### Manuelna Verifikacija
- Otvoriti `forms-workspace/` i pokrenuti `pnpm dev` za neku od formi
- Proveriti disk space uštede (svaki projekat troši ~1MB umesto ~10MB)
