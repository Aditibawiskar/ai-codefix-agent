# 🚀 AI Code-Fix Agent (Full Stack)

**An intelligent, autonomous code remediation agent that analyzes Python code, detects bugs, and generates unified diff patches using Open Source LLMs.**

![Application Screenshot](./frontend/public/screenshot.png)

This project is a **Full Stack Application** built to simulate a "Human-in-the-Loop" automated debugging workflow. It connects a **FastAPI** backend to a **React/TypeScript** frontend, using **Hugging Face Inference APIs** to provide real-time code fixes.

---

## 🌟 Key Features

### 🧠 Advanced AI Logic
- **Dynamic Model Switching:** Automatically switches between **Qwen 2.5 (7B)** for complex logic and **Gemma 2 (2B)** for fast syntax fixes.
- **Robust Fallback Mechanism:** Handles API timeouts and rate limits by downgrading to lighter models or gracefully failing.
- **Sanitization Layer:** Custom regex parsers to strip Markdown/garbage text from LLM outputs, ensuring strict JSON compliance.

### 🖥️ Full Stack Architecture
- **Frontend:** React.js, TypeScript, Vite, TailwindCSS (Modern, responsive UI).
- **Backend:** FastAPI, Pydantic, Uvicorn (High-performance Async API).
- **Integration:** REST API communication with strict CORS and error handling policies.

### 🛡️ System-Level Automation
- **Unified Diff Generation:** Generates standard `git apply` compatible patches.
- **Sandboxed Application:** Creates temporary directories to safely test and validate patches before suggesting them.
- **Automated Validation:** Runs `flake8` and custom syntax checks on generated code.

---

## 🏗️ Tech Stack

| Component | Technology |
| :--- | :--- |
| **Frontend** | React 18, TypeScript, Vite, TailwindCSS |
| **Backend** | Python 3.11, FastAPI, Uvicorn |
| **AI / LLM** | Hugging Face API (Qwen-2.5-7B, Gemma-2-2B) |
| **DevOps** | Docker, Docker Compose, Git |
| **Testing** | Pytest, Flake8, Black |

---

## ⚡ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/ai-codefix-agent.git
cd ai-codefix-agent
```

### 2. Backend Setup
```bash

# Create virtual environment
python -m venv .venv

# Activate it (Windows)
.venv\Scripts\activate
# Activate it (Mac/Linux)
# source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo "HF_TOKEN=your_huggingface_token" > .env
echo "HF_MODEL=google/gemma-2-2b-it" >> .env
```

### 3. Frontend Setup
```bash

cd frontend
npm install
```

## 🏃‍♂️ Running the App
### Option A: Using Docker (Recommended)
```bash
docker-compose up --build
```

### Option B: Manual Mode
**Terminal 1** (Backend):
```bash
# Make sure .venv is activated
uvicorn app.main:app --reload
```

**Terminal 2** (Frontend):
```bash
cd frontend
npm run dev
Access the app at http://localhost:5173
```

### 🧠 How It Works (Architecture)
1. Input: User pastes buggy code into the React UI.

2. Analysis: FastAPI backend sends a specialized prompt to the Hugging Face Router.

3. Processing:

- The LLM identifies the error (Logic vs Syntax).

- It generates a Unified Diff (standard Git patch format).

- The backend strips Markdown and validates the JSON structure.

4. Verification: The backend attempts to apply the patch in a tempfile environment to ensure it is valid code.

5. Result: The UI displays the Fix, Explanation, and a "Diff View" for human review.


### 🧪 Testing
Run the integration test suite to verify API connectivity and LLM parsing:

```bash
pytest tests/

# OR run the quick connectivity check
python tests/test_api.py
```

Author: Aditi

License: MIT
