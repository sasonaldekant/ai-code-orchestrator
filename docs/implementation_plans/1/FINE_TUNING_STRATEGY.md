# Phase 21: Autonomous Fine-Tuning Strategy

## 1. Executive Summary

Electronic systems effectively have "amnesia" between sessions. RAG (Retrieval Augmented Generation) solves short-term memory, but **Fine-Tuning** builds long-term muscle memory.

**Goal:** Create a standardized pipeline where the **AI Code Orchestrator** analyses its own source code to "teach" a smaller, faster, cheaper local model (e.g., Llama-3-8B or Mistral) how to write code in the project's specific style.

## 2. The Distillation Pipeline

We will implement a **Teacher-Student** architecture.

```mermaid
graph TD
    Codebase[Source Code] --> AST[AST Parser]
    AST --> Chunks[Code Chunks]
    Chunks --> Teacher[Teacher Model (GPT-4o)]
    Teacher -- Generates Instructions --> Dataset[Instruction Dataset (JSONL)]
    Dataset --> Trainer[Unsloth/PEFT Trainer]
    Trainer --> Student[Student Model (Llama-3-8B)]
    Student --> Inference[Local Inference]
```

## 3. Component Architecture

### 3.1 Dataset Generator (`core/learning/dataset_generator.py`)

Responsible for creating high-quality `(instruction, input, output)` triplets.

- **Extraction**: Uses AST to identify Classes and Functions.
- **Generation**: Prompts the Teacher (GPT-4o) to explain the code or write a refactoring request for it.
- **Format**: Alpaca or ShareGPT format.

**Example Training Sample:**

```json
{
  "instruction": "Refactor the following function to use the new CostManager API.",
  "input": "def call_llm(...): ... # Old code",
  "output": "def call_llm(...): ... # New code using CostManager"
}
```

### 3.2 Training Manager (`core/learning/trainer.py`)

A wrapper around modern fine-tuning libraries (Unsloth is preferred for speed, or pure PEFT/HuggingFace).

- **Technique**: LoRA (Low-Rank Adaptation) / QLoRA.
- **Target Modules**: `q_proj`, `k_proj`, `v_proj`, `o_proj`.
- **Hardware**: Checks for CUDA. Falls back to "Mock Training" if no GPU is detected (ensuring the pipeline code is valid even on CPU machines).

### 3.3 Model Router Integration

Once trained, the new model adapter must be registered in the `ModelRouter`.

- **New Route**: "specialist_local"
- **Usage**: Low-latency tasks like "Auto-Fix" or "Autocomplete".

## 4. Implementation Steps

1.  **Dataset Generation**: Build the tool to extract code and synthesize synthetic training data.
2.  **Training Harness**: Create the script that runs the training loop.
3.  **Integration**: Update `LifecycleOrchestrator` to optionally use the local fine-tuned model.

## 5. Requirements

- `unsloth` (Linux/WSL only usually) or `peft`, `transformers`, `bitsandbytes`.
- _Note_: Since we are on Windows, we will design the `Trainer` to be modular. It can verify dependencies and gracefully degrade or guide the user to Use WSL.

## 6. Verification

We will verify that:

1.  We can generate 10 valid training samples from the current codebase.
2.  The training script initializes the model and tokenizer correctly (even if we don't run full epochs).
