# RAG Ingestion Guide: Hybrid Intelligence Strategy

Ovaj dokument služi kao zvanično uputstvo za popunjavanje baze znanja (RAG) unutar AI Code Orchestrator-a, sa posebnim fokusom na integraciju `DynUI` ekosistema.

## 1. Zašto radimo na ovaj način? (Racional)

Umesto da u memoriju (RAG) učitamo sav izvorni kod projekta, koristimo **Hibridni pristup**:

1.  **RAG kao "Mape i Putokazi" (Discovery Layer)**: Agenti koriste RAG da bi brzo saznali *šta postoji*, *kako se koristi* i *koja su pravila*. To su "lagani" podaci (samo DOCS, Stories, Rules).
2.  **Fizički pristup kao "Izvor Istine" (Implementation Layer)**: Kada Agent iz RAG-a sazna da treba da koristi npr. `DynamicButton`, on tada koristi direktan pristup fajl sistemu da pročita *trenutni* `.tsx` fajl i vidi precizne TypeScript tipove.

**Prednosti**:
- **Brzina**: Manje podataka u memoriji znači bržu pretragu.
- **Preciznost**: Agent uvek piše kod na osnovu najnovijeg stanja na disku, a ne na osnovu zastarelog indeksa u bazi.
- **Ušteda**: Troši se drastično manje tokena.

---

## 2. Hijerarhija Znanja (Tiers)

Znanje organizujemo u 4 nivoa (Tiers) kako bi agenti znali šta je prioritet:

- **Tier 1 (Pravila)**: "Sveto pismo". Ovde su instrukcije kojih agent mora da se drži bez pogovora (npr. Standardi kodiranja).
- **Tier 2 (Stilovi)**: Design Tokeni (boje, spacing). Sve što definiše vizuelni identitet.
- **Tier 3 (Komponente)**: Dokumentacija o komponentama, Storybook primeri i testovi. Služi za otkrivanje funkcionalnosti.
- **Tier 4 (Backend)**: API struktura i logika upravljanja svojstvima iz baze.

---

## 3. Korak-po-korak: Korišćenje Admin Tool-a

Sve radnje se obavljaju u tabu **"Manage Knowledge"** (Universal Ingestion Panel).

### Korak 1: Definisanje Izvora (Source)
1.  Izaberi **Source Type** (najčešće `Directory` za ceo set komponenti ili `File` za specifična pravila).
2.  Unesi **Target Path** (preporučuje se **relativna putanja**, npr. `../dyn-ui-main-v01/docs`).

### Korak 2: Podešavanje Metapodataka (Metadata)
1.  Izaberi odgovarajući **Tier** (1, 2, 3 ili 4).
2.  Unesi **Category** (npr. `core-rules`, `ui-components`, `backend-api`).
3.  Dodaj **Tags** (opciono, za još finiju pretragu).

```markdown
### Korak 3: Kontrola i Validacija (KLJUČNI KORAK)
1.  U polje **Filter** unesi glob obrazac (npr. `DOCS.md, *.stories.tsx, *.types.ts`). Ovo je tvoja zaštita da u RAG ne uđe "đubre".
2.  Klikni na **"Validate"**.
3.  **Pregledaj rezultat**: Sistem će ti ispisati koliko fajlova je pronađeno. Ako vidiš prevelik broj (npr. 1000+), tvoj filter je previše širok!
```

### Korak 4: Izvršavanje (Ingest)
1.  Tek kada validacija potvrdi tačan broj fajlova, klikni na **"Ingest Content"**.
2.  Statusna traka će te obavestiti o napretku.

---

## 4. Plan za DynUI (Pristup po Tiersovima)

| Faza | Tier | Sadržaj | Filter |
| :--- | :--- | :--- | :--- |
```markdown
| **01** | Tier 1 | Globalna pravila i standardi | `README.md, rules/*.md` |
| **02** | Tier 3 | Komponente (Docs, Stories, Tests) | `components/**/DOCS.md, components/**/*.stories.tsx, components/**/*.types.ts` |
| **03** | Tier 4 | Backend Logic (Prisma, API Controllers) | `backend/src/api/**/*.ts` |
```

---

> [!IMPORTANT]
> **Pravilo 1-1-1**: Svaka važna promena u pravilima zahteva novi Ingest u Tier 1 kako bi svi Agenti odmah bili svesni nove instrukcije.
