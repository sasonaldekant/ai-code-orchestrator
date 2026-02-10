# AI Code Orchestrator - Simulation Testing Guide

This guide details how to test the Orchestrator's robust features, including **Happy Paths** (success) and **Failure Modes** (recovery), using the Simulation Mode.

## 🟢 Scenario 1: The Happy Path (Success)

**Objective:** Verify that the system can take a requirement, plan it, implement it, verify it, and write the file without errors.

### 1. Run Simulation

```bash
python scripts/demo_simulation.py
```

_Select option 1: "Standard CSV Analysis"_

### 2. Expected Output

- **Analyst:** Generates requirements for CSV parsing.
- **Architect:** Designs `CsvAnalyzer` class.
- **Implementation:** Generates valid Python code using `pandas`.
- **Verifier:** Runs generated tests; all pass (`Exit code: 0`).
- **Orchestrator:** Writes `analyzer.py` to disk.
- **Result:** `✅ Simulation Complete!`

---

## 🔴 Scenario 2: Hallucination Detection (Guardrails)

**Objective:** Provoke the agent to import a non-existent library and verify that the Guardrail system catches it _before_ execution.

### 1. Trigger Prompt

"Create a script that uses the `pndas` library (misspelled) to read a file."
_(In Simulation Mode, select option 2: "Force Hallucination")_

### 2. Expected Behavior

1.  **Implementation Agent** generates code with `import pndas`.
2.  **GuardrailMonitor** scans the code.
3.  **Event Bus** broadcasts: `⚠️ [Guardrails] Safety Violation: Import 'pndas' is suspicious or not installed.`
4.  **Orchestrator** rejects the code and requests a retry.
5.  **Implementation Agent** (Mock) retries with correct `import pandas`.
6.  **Result:** Task succeeds after self-correction.

---

## 🟠 Scenario 3: Bad Code & Verification Loop

**Objective:** Provoke the agent to write syntactically incorrect code and verify that the Test/Fix loop repairs it.

### 1. Trigger Prompt

"Write a script with a syntax error."
_(In Simulation Mode, select option 3: "Force Syntax Error")_

### 2. Expected Behavior

1.  **Implementation Agent** returns code with a missing parenthesis.
2.  **Verifier** attempts to run tests.
3.  **CodeExecutor** fails: `Exit code: 1 (SyntaxError)`.
4.  **Verifier** sends feedback: "SyntaxError on line X".
5.  **Implementation Agent** receives feedback and generates fixed code.
6.  **Verifier** runs tests again -> Pass.
7.  **Result:** Task succeeds after 1 retry.

---

## 🔵 Scenario 4: Security Violation

**Objective:** Attempt to inject a hardcoded secret and see if it's blocked.

### 1. Trigger Prompt

"Connect to AWS using this secret key: AKIA..."
_(In Simulation Mode, select option 4: "Force Security Violation")_

### 2. Expected Behavior

1.  **Implementation Agent** generates code with `AWS_KEY = "AKIA..."`.
2.  **GuardrailMonitor** detects high-entropy string/secret pattern.
3.  **Event Bus** broadcasts: `❌ [Guardrails] Critical Violation: Potential hardcoded secret detected.`
4.  **Orchestrator** aborts the task immediately to prevent leakage.
5.  **Result:** `❌ Task failed: Critical guardrail violation.`

---

## 🛠️ How to Customize Simulations

To add your own scenarios, edit `core/simulation/mock_llm.py`:

```python
def _mock_implementation_response(self, prompt):
    if "force_error" in prompt:
         return MockResponse(content="def bad_code( x") # Syntax error
    # ... regular response
```
