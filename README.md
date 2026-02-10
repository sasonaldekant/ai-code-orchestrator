# AI Code Orchestrator v4.0 (Bleeding Edge)

**The first "Cognitive" AI Software Engineer.**

Unlike standard coding assistants that just complete text, the **AI Code Orchestrator v4.0** is an autonomous agent that **sees** your app, **fixes** its own bugs, **remembers** your preferences, and **learns** from its mistakes.

---

## 🚀 Key Features (v4.0)

### 🧠 Cognitive Memory ("The Cortex")

The system is no longer stateless. It has:

- **Episodic Memory:** Remembers your specific coding rules (e.g., "Always use Tailwind", "No classes").
- **Self-Correction:** If it fixes a bug, it saves the solution in its **Experience DB** to avoid repeating the mistake.

### 🛠 Autonomous Self-Healing (Auto-Fixer)

When code verification fails, the orchestrator doesn't just error out. It:

1. **Investigates** the error using a specialized `RepairAgent`.
2. **Patches** the code automatically.
3. **Re-verifies** until the tests pass.

### 👁 Multi-Modal Vision

Drag & drop screenshots, mockups, or diagrams into the Nexus GUI. The agent can "see" what you mean and generate code that matches the visual design.

### 🔌 IDE Bridge

Connect your favorite editor (VS Code, Cursor, JetBrains) directly to the brain.

- Right-click code -> "AI Fix This"
- Right-click code -> "AI Explain This"

---

## 📚 Documentation

- **[User Guide v4.0](docs/USER_GUIDE_v4.md)** - Full usage instructions.
- **[Technical Documentation](docs/AI%20Code%20Orchestrator%20-%20Technical%20Documentation.md)** - Architecture deep dive.
- **[IDE Integration](docs/IDE_INTEGRATION_GUIDE.md)** - How to build plugins.

---

## ⚡ Quickstart

### 1. Installation

```bash
git clone https://github.com/mgasic/ai-code-orchestrator.git
cd ai-code-orchestrator
pip install -r requirements.txt
cd ui && npm install
```

### 2. Configuration

Copy `.env.example` to `.env` and add your API keys (OpenAI, Anthropic, or Google).

### 3. Run

**Option A: Nexus GUI (Recommended)**

```bash
# Terminal 1
python manage.py start-api

# Terminal 2
cd ui && npm run dev
```

Access at `http://localhost:5173`.

**Option B: CLI**

```bash
python manage.py run "Build a Tetris game in Python" --auto-fix
```

---

## 🏗 Architecture

The system is built on a **System Cortex** that dynamically routes your intent to the right tool:

```
[User Request] -> [Semantic Router] -> [Registry] -> [Agent/Tool]
                                           ^
                                           |
                                    [Cognitive Memory]
```

## License

MIT
