import subprocess, sys, json, os
from pathlib import Path

def test_orchestrator_offline(tmp_path: Path):
    os.environ["OFFLINE_LLM"] = "1"
    schema = Path("schemas/phase_schemas/requirements.json")
    proc = subprocess.run([sys.executable, "-m", "cli", "--phase", "analyst", "--schema", str(schema)], capture_output=True, text=True)
    assert proc.returncode == 0
    assert "OK:" in proc.stdout
