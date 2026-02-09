# Analiza trenutnog stanja projekta i predlog daljih koraka

## Uvod

U ovom dokumentu analiziran je trenutni kod u repozitorijumu **mgasic/ai‑code‑orchestrator** i upoređen sa funkcionalnim i tehničkim zahtevima definisanim u priloženoj dokumentaciji (verzija 2.0.0, 3.0 i „Enhanced RAG“).  Dokumentacija za verziju 2.0.0 proširuje skeletni v0.1.0 na pluggable RAG sistem, višemodelski router, upravljanje troškovima i paralelnu egzekuciju【663633728689534†L24-L34】【663633728689534†L118-L137】, dok „AI Code Orchestrator v03” uvodi domenski agnostičan pristup sa DSL‑om za konfiguraciju znanja.

## Pregled opisanih funkcionalnosti

Najvažniji zahtevi iz dokumentacije su:

* **Pluggable RAG subsystem** – retriver treba da se prebaci sa prostog pretraživanja na vektorsku bazu, npr. Chroma, Faiss ili Weaviate【663633728689534†L120-L124】【663633728689534†L200-L207】.  Dokumentacija napominje da se vektorske baze lako pokreću lokalno i nude skalabilnost.
* **Višemodelski router i selekcija modela** – `ModelRouter` bira odgovarajući model i provajdera za svaku fazu koristeći YAML konfiguraciju.  Različite faze (analiza, arhitektura, implementacija, testiranje, QA) mapiraju se na modele kao što su Claude Sonnet, GPT‑4o i Gemini 2.5 Pro【663633728689534†L149-L176】.
* **Optimizacija tokena i minimalno slanje konteksta** – kontekst se skraćuje, šalje se samo diff, komunikacija između agenata se zasniva na strukturi JSON【663633728689534†L182-L193】.
* **Upravljanje troškovima i budžeti** – `CostManager` prati potrošnju tokena i troškove, primenjuje limite po zadatku, satu i danu te emituje upozorenja kod 80 % budžeta【663633728689534†L134-L137】【663633728689534†L218-L233】.
* **Paralelna egzekucija i konsenzus** – v2.0.0 uvodi asinhronu paralelizaciju faza koje se mogu izvoditi uporedo i mehanizam proizvođač–recenzent u kome jedan model predlaže, a drugi potvrđuje dizajn ili kod【663633728689534†L24-L34】.
* **Domenska ekstenzija** – v03 uvodi YAML‑baziranu DSL za definisanje izvora znanja i strategija RAG‑a po domenu, čime se olakšava rad sa različitim domenima bez promene koda.

## Trenutno stanje repozitorijuma

U repozitorijumu se nalazi osnovna implementacija (v0.1.0) koja obuhvata kostur orkestratora i osnovne agente.  Analiza ključnih fajlova pokazuje:

* **Orchestrator** – `core/orchestrator.py` definiše klasu `Orchestrator` koja instancira `CostManager`, `ModelRouter`, `LLMClient`, `OutputValidator`, `TracingService` i `RAGRetriever`【339330685721275†L34-L43】.  Metod `run_pipeline` sekvencijalno poziva faze analize, arhitekture, implementacije i testiranja, beleži događaje i smešta rezultate u direktorijum `outputs`【339330685721275†L125-L184】.  Pararelizacija i konsenzus nisu implementirani; faze se izvode jedna za drugom, a generisani kod se ne recenzira.
* **Retriver** – `core/retriever.py` učitava JSON dokumente iz direktorijuma `rag/domain_indices` i pretražuje ih preko prostog poklapanja ključnih reči【688617387704873†L0-L7】【688617387704873†L40-L66】.  Kôd sugeriše da se za produkciju može zameniti vektorskom bazom, ali integracija nije dodata.
* **Model router i LLM klijent** – u repozitorijumu postoji osnovna konfiguracija `config/model_mapping.yaml`, ali `ModelRouter` implementacija je minimalna; ne podržava izbor različitih provajdera ni konsenzus.
* **Upravljanje troškovima** – `CostManager` prati potrošene tokene, ali ne evidentira dnevne ili satne budžete niti emituje upozorenja; budžeti su hard‑kodirani za testove.
* **Domenski DSL** – YAML DSL definisan u v03 i u priloženim dokumentima nije prisutan; nema skripti za ingestiranje domenih znanja, chunkovanje ili treniranje vektorske baze.
* **CLI i API** – README objašnjava korišćenje CLI‑a za pokretanje agent pipeline‑a, ali API Gateway sa autentikacijom i rate limiting‑om iz v2.0.0 nije implementiran.

### Razlike u odnosu na dokumentaciju

1. **RAG sistem** – Trenutni retriver ne koristi vektorske baze; vektorizacija, metapodataka i napredni algoritmi pretrage iz „Enhanced RAG” nisu prisutni.  Dokumentacija navodi da vektorska baza treba da bude pluggable i da se može lako zameniti【663633728689534†L120-L124】【663633728689534†L200-L207】.
2. **Model routing i konsenzus** – Kôd sadrži `ModelRouter`, ali u praksi se koristi jedan zadani model.  U dokumentaciji se insistira na višemodelskom izboru i konsenzus mehanizmu kojim se nekoliko modela takmiči i glasaju【663633728689534†L149-L176】.
3. **Token optimizacija** – Ne postoje tehnike za skraćivanje konteksta, slanje diffa niti strukturalna komunikacija između agenata【663633728689534†L182-L193】.
4. **Budžeti i izveštavanje** – `CostManager` treba da implementira dnevni, satni i po‑task budžet i da prekine izvršavanje kada se limit prekorači【663633728689534†L218-L233】.  Trenutna verzija ne prekida rad pri prelasku budžeta niti šalje upozorenja.
5. **Paralelna egzekucija i recenzija** – Faze se izvršavaju sekvencijalno; nema asinhronog pokretanja niti petlje proizvođač–recenzent.
6. **Domenska konfiguracija** – Nije implementiran YAML‑bazirani DSL za opis domena; ne postoje alati za ingestiranje različitih izvora znanja (kôd, wiki, baze) ni za granularno chunkovanje.
7. **Dokumentacija i testovi** – Iako je priložena dokumentacija opsežna, repozitorijum ne sadrži automatizovane testove ni primere upotrebe za nove funkcionalnosti.

## Preporučeni sledeći koraci

Da bi projekat dostigao zahteve definisane u priloženoj dokumentaciji, predlažu se sledeće aktivnosti:

1. **Implementirati pluggable RAG** – Izabrati vektorsku bazu (ChromaDB/Faiss) i napisati modul za ingestiranje dokumenata iz domena.  Modul treba da podrži pametno chunkovanje (moguće iz „ADVANCED_RAG”) i upisivanje metapodataka (npr. tip izvora, pozicija u kodu).  Nakon ingestiranja, `RAGRetriever` bi birao kontekst preko semantičkog pretraživanja umesto ključnih reči.
2. **Proširiti `ModelRouter`** – Napraviti YAML konfiguraciju koja mapira faze i specijaliste na različite modele i provajdere.  Uvesti mehanizam za konsenzus gde se generišu više predloga (npr. Sonnet, GPT‑4o i Gemini), porede se rezultati i bira najbolji.
3. **Optimizacija tokena** – Implementirati režime kontekst‑skraćenja (retain‑k, diff‑slanje) i strukturisanu komunikaciju baziranu na JSON‑porukama da bi se smanjio broj tokena i troškovi【663633728689534†L182-L193】.
4. **Upravljanje troškovima** – Dopuniti `CostManager` budžetima (task, sat, dan), automatskim upozorenjima pri 80 % potrošnje i mehanizmom prekida kada se limit dostigne【663633728689534†L134-L137】【663633728689534†L218-L233】.  Dodati funkciju za izvoz izveštaja.
5. **Asinhrona i paralelna egzekucija** – Refaktorisati `run_pipeline` da faze koje nemaju zavisnosti (npr. backend i frontend implementacija) pokreće paralelno korišćenjem `asyncio.gather`.  Implementirati petlju proizvođač–recenzent gde drugačiji model proverava rezultat i pruža feedback.
6. **Domenski DSL i ingestija** – Implementirati YAML DSL definisanu u v03 za opis izvora znanja, chunking strategije, filtere i parametre RAG‑a.  Napraviti CLI alat za ingestiju koji generiše vektorski indeks prema navedenim pravilima.
7. **API i autentikacija** – Dodati FastAPI gateway sa autentikacijom, rate‑limitingom i end‑point‑ovima za pokretanje faza, upravljanje budžetima i preuzimanje izveštaja, kako je opisano u arhitekturi v2.0.0.
8. **Testiranje i dokumentacija** – Uvesti jedinicne testove za nove module, integracione testove za pipeline i primere upotrebe.  Ažurirati README da odražava nove mogućnosti, uključujući instalaciju lokalnih vektorskih baza i konfiguraciju modela.

## Zaključak

Repozitorijum trenutno predstavlja minimalnu verziju orkestratora namenjenu demonstraciji koncepta, dok priložena dokumentacija opisuje mnogo napredniji i sveobuhvatniji sistem.  Da bi se postigla funkcionalna usklađenost, potrebno je uvesti pluggable RAG, višemodelsku orkestraciju, optimizaciju tokena, mehanizme konsenzusa i recenzije, kao i upravljanje troškovima i budžetima.  Ove nadogradnje će omogućiti da **AI Code Orchestrator** isporučuje visokokvalitetan kod u različitim domenima uz efikasno korišćenje resursa i jasnu kontrolu troškova.