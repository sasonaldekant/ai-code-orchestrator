from pathlib import Path
from rag.ingest import ingest_dir
from rag.query import ask

def test_rag_ingest_and_query(tmp_path: Path):
    src = tmp_path / "docs"
    src.mkdir()
    (src / "a.md").write_text("alpha beta gamma", encoding="utf-8")
    store = tmp_path / "store.json"
    ingest_dir(str(src), str(store))
    res = ask(str(store), "alpha", k=1)
    assert len(res) == 1 and res[0][0] == "a"
