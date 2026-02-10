# Walkthrough: Phase 16.1 - Autonomous Self-Healing

## Goal

To implement an **"Auto-Fixer" (Repair Agent)** that can autonomously investigate and patch code errors during the verification phase.

## Changes Implemented

### 1. `RepairAgent` ("The Fixer")

- **File:** `core/agents/specialist_agents/repair_agent.py`
- **Logic:**
  1.  **Investigates:** Uses `RetrievalAgent` to find the root cause file/line.
  2.  **Plans:** Generates a fix plan (JSON) using the LLM.
  3.  **Applies:** Overwrites the file with the corrected content.

### 2. Orchestrator Integration

- **File:** `core/lifecycle_orchestrator.py`
- **Logic:**
  - Added `auto_fix` boolean to `execute_request` and `execute_task`.
  - In `execute_task`, if `verification_loop` fails and `auto_fix=True`:
    - Trigger `RepairAgent.auto_fix(error_log)`.
    - If fix succeeds, **re-run verification** immediately.

### 3. API & UI Updates

- **Backend:** `POST /run` now accepts `auto_fix: boolean`.
- **Frontend:** Added a **"Auto-Fix"** toggle (Wrench Icon) in the chat toolbar.

## Verification Results

### Automated Test: `tests/verify_phase16_autofix.py`

We simulated a `SyntaxError` in a dummy file `broken_math.py`.

**Error Log:**

```text
File "broken_math.py", line 4
    return a + b +
                 ^
SyntaxError: invalid syntax
```

**Agent Action:**

- **Investigation:** Identified line 4 in `broken_math.py` as the culprit.
- **Fix Plan:** Remove the trailing `+`.
- **Result:**

```python
def add_numbers(a, b):
    # Fixed syntax error
    return a + b
```

- **Status:** **SUCCESS** (Verified by script)

## Next Steps

- Proceed to **Phase 16.2: Multi-Modal Capabilities (Vision)**.
