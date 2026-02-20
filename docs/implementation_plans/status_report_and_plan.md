# Trenutni Status i Plan Implementacije

## 1. Analiza problema sa generisanim `kreditni-zahtev` (i ostalim projektima)
Prijavljene greške su uglavnom proizašle iz nedostatka Type deklaracija, sintaksnih problema u TypeScript-u koji je generisan iz Python skripte i nepravilnog povezivanja zavisnosti (dependencies) unutar monorepo workspace-a (pnpm). 

**Rešeni problemi (Bugfix):**
- **Konstanta `None`:** Python je inicirao dodeljivanje default i prop vrednosti kao `None` bez konverzije u string, boolean ili null. Ovo je izazvalo TypeScript compile errore. Dodali smo check za `None` u `CodeGenerator`.
- **Zavisnosti (`@dyn-ui/react`, `react`, `zod`):** Nisu bili ispravno povezivani kroz Monorepo `workspace:*` ili ih uopšte nije bilo u `package.json` (kao npr `zod`). Ovo je rešeno na nivou `monorepo_initializer` i `project_generator`.
- **Imports u `Form.tsx` & `main.tsx`:** Postojao je mismatch importovanih funkcija u aplikaciji: funkcija za kalkulacije (`applyBusinessLogic`) je u Forms.tsx bila pozivana kao `applyCalculations`. Uz to, ekstenzija import-a u glavnom fajlu `main.tsx` je brisala putanju. Popravljeno u alatima generacije.

**Odgovori na pitanja o praznim folderima:**
U prethodno definisanom struktuiranju (`ProjectGenerator.py`), predviđeno je bilo kreiranje nekoliko praznih foldera. Oni služe kao temelj za organizaciju koda kada kompleksnost aplikacije poraste, a sledeće je zamišljeno da se tu nađe:
- **`src/api/`**: Predviđeno za konfiguraciju Axios klijenata, TypeScript interfejse API odgovora i React Query Hookove (npr. dinamicke `lookup` pull calls).
- **`src/components/`**: Ovde se isključivo prave kompozicije od postojećih `@dyn-ui/react` komponenti ukoliko jedan element ne pokriva specifičan zahtev. Radimo isključivo sa DynUI komponentama i nijedna druga biblioteka ili custom HTML komponenta ne dolazi u obzir. Ukoliko nešto krucijalno nedostaje, zahtev se prosleđuje DynUI timu na implementaciju.
- **`src/utils/`**: Helperi (formatiranje valuta na osnovu lokacije npr. za "kreditni-zahtev", validatori serijalizacije, i pomoćne pure logičke funkcije). 

Trenutno stoje prazni jer sistem još uvek bazirano samo na JSON template-u ne uočava preterano kompleksnu logiku koja bi zahtevala taj nivo skalabilnosti pa pakuje kod u par čistih korentnih fajlova (poput `calculations.ts` i `api.ts`).

---

## 2. Naredni koraci (Plan za dalji razvoj)
Uspešno smo otklonili uzroke compile i runtime errors u trenutnoj verziji generatora formi. Na osnovu postavljenog režima posla ("Planning Mode"), definisali smo sledeći akcioni plan.

- [ ] **Korak 1: Testiranje i uspostavljanje novog projekta (`korisni-ka-registracija`)**
  Projekat je generisan kroz nedavne skripte. Neophodno je startovati projekat unutar `outputs/forms-workspace/apps/korisni-ka-registracija` naredbom `pnpm dev` kako bi se vizuelno procenio lokalni render projekta i proverilo njegovo funkcionisanje bez Type grešaka.
  
- [ ] **Korak 2: Dodavanje naprednijih mehanizama Logike i Validacije u kodni Generator**
  Zod schema generator u ovom trenuku generiše bazične provere. Možemo ga proširiti validacijom `min`, `max`, obaveznosti uslovnih polja i kreiranjem test helper `utils` funkcija.

- [ ] **Korak 3: Stabilizacija VS Code CLI procesa / Orchestratora**
  Pregled načina na koji orkestrator servira ZIP fajl nakon izvršenja skripte sa popravljenim generatorom. Pravljenje komandi ispraćenim u extenziji.

Ovaj plan je predat korisniku na odobravanje.
