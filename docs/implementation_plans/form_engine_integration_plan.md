# Generalizacija Form Engine-a za DynUI

Analizirao sam `form-engine` aplikaciju. Njen trenutni dizajn baziran na JSON-u je izvanredan jer sadrži **dynamic rendering**, **ValidationEngine** (sa podrškom za specifične validacije poput JMBG/PIB) i **LogicEngine** (za uslovnu vidljivost i cross-field logiku).

Trenutno, AI Code Orchestrator generiše formu tako što "hardkoduje" svako polje i svaki state (`useState`) u [.tsx](file:///c:/Users/mgasic/Documents/AIProjects/dyn-ui-main-v01/apps/form-engine/src/App.tsx) fajl. Ovo je neefikasno za velike forme i gubi dinamiku iz JSON-a (poput uslovne vidljivosti koja se trenutno ne prevodi savršeno u React kod).

## Predlog: Migracija [FormEngine](file:///c:/Users/mgasic/Documents/AIProjects/dyn-ui-main-v01/apps/form-engine/src/FormEngine.tsx#35-133) u interno upravljani paket `@form-studio/form-engine`

Umesto da prebacujemo [FormEngine](file:///c:/Users/mgasic/Documents/AIProjects/dyn-ui-main-v01/apps/form-engine/src/FormEngine.tsx#35-133) u samu `@dyn-ui/react` biblioteku, zadržaćemo apsolutnu kontrolu nad njim unutar Orkestratora i RAG konteksta.

Kreiramo novi, lokalni paket unutar našeg form workspace-a (monorepo): `outputs/forms-workspace/packages/form-engine`.
Ova biblioteka će se oslanjati na `@dyn-ui/react` za komponente, ali će logika ([ValidationEngine](file:///c:/Users/mgasic/Documents/AIProjects/dyn-ui-main-v01/apps/form-engine/src/core/ValidationEngine.ts#29-278), [LogicEngine](file:///c:/Users/mgasic/Documents/AIProjects/dyn-ui-main-v01/apps/form-engine/src/core/LogicEngine.ts#33-213), `<DynFormEngine />`) ostati kod nas.

Postojeće izgenerisane React aplikacije (`example-form`, `kreditni-zahtev`, itd.) ćemo obrisati. Nove forme će se generisati od nule procesiranjem postojećih JSON šablona, a one će samo importovati ovaj lokalni paket i proslediti mu JSON šablon dobijen iz Form Studia.

### Koraci implementacije:

1.  **Inicijalizacija Paketa u Monorepou**
    -   AI Orchestrator-ov [monorepo_initializer.py](file:///c:/Users/mgasic/Documents/AIProjects/ai-code-orchestrator/core/form_engine/monorepo_initializer.py) će prigrliti kreiranje paketa `packages/form-engine`.
    -   Podešavanje [package.json](file:///c:/Users/mgasic/Documents/AIProjects/ai-code-orchestrator/ui/package.json) da izveze osnovnu `<FormEngine />` komponentu.

2.  **Kopiranje i Prilagođavanje Core Engine klasa**
    -   AI Orkestrator će sadržati (u `ai-code-orchestrator/templates/form-engine/` folderu) naš prilagođeni engine.
    -   Tu spadaju [ValidationEngine.ts](file:///c:/Users/mgasic/Documents/AIProjects/dyn-ui-main-v01/apps/form-engine/src/core/ValidationEngine.ts), [LogicEngine.ts](file:///c:/Users/mgasic/Documents/AIProjects/dyn-ui-main-v01/apps/form-engine/src/core/LogicEngine.ts), [LookupService.ts](file:///c:/Users/mgasic/Documents/AIProjects/dyn-ui-main-v01/apps/form-engine/src/core/LookupService.ts) i [FormEngine.tsx](file:///c:/Users/mgasic/Documents/AIProjects/dyn-ui-main-v01/apps/form-engine/src/FormEngine.tsx).
    -   Generalizacija [FieldRenderer](file:///c:/Users/mgasic/Documents/AIProjects/dyn-ui-main-v01/apps/form-engine/src/FieldRenderer.tsx#40-208)-a da mapira JSON `type` vrednosti u sve dostupne DynUI komponente.

3.  **Refaktorisanje AI Orchestrator-a (Backend Generisanje koda)**
    -   Umesto da [code_generator.py](file:///c:/Users/mgasic/Documents/AIProjects/ai-code-orchestrator/core/form_engine/code_generator.py) generiše `useState` kuke i stotine HTML linija za polja, on sada generiše izuzetno prost kod za specifičnu aplikaciju:
        ```tsx
        import React from 'react';
        import { FormEngine } from '@form-studio/form-engine';
        import formSchema from './schema.json';

        export function Form() {
          return <FormEngine schema={formSchema} onSubmit={(data) => console.log(data)} />
        }
        ```

## Zašto je ovo ogroman pomak?
*   **RAG & Fleksibilnost:** Ostajemo apsolutni gospodari nad Engine kodom unutar orkestratora! Ako AI treba da doradi kompleksnu validaciju, radi to u našem template-u, a ne u eksternoj biblioteci.
*   **Ažuriranje & Održivost:** Iako sada krećemo od nule (test faza), u produkciji će ažuriranjem `packages/form-engine` SVE generisane forme automatski dobiti ispravku.
*   **Brzina Generisanja:** AI Orchestrator će postati višestruko brži jer prestaje da naivno "štampa" React i umesto toga instancira moćan, već gotov Engine kojem samo daje JSON.

Započinjemo sa realizacijom!
