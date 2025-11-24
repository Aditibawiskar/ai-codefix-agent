# AI Code-Fix Agent 🧠⚙️
An AI-powered backend service that automatically detects code issues, generates fixes, creates diffs, validates patches, and simulates applying them — built with **FastAPI, Python, LLMs, and Docker**.

This project includes:
- Code fix generation using LLM (HuggingFace or mock)
- Diff generation (`unified diff` format)
- Patch validation (`validate_patch`)
- Patch application using real `git apply`
- Automated code checks (flake8, black, pytest)
- Complete REST API with FastAPI
- Dockerized production-ready container
- Integration test suite

---

## 🚀 Features

### ✔️ AI-Powered Code Fixing
Send code → Model processes → Returns:
- Cleaned/fixed code
- Explanation
- Test stub
- Unified diff patch

### ✔️ Patch Validation
`POST /validate_patch` checks if a patch is:
- Valid diff format
- Syntactically correct
- Safe to apply

### ✔️ Patch Application
`POST /apply_patch`:
- Creates a temp folder
- Writes sample file
- Applies patch using `git apply`
- Returns check results

### ✔️ Clean Codebase
Includes:
- **flake8** style enforcement
- **black** auto-formatting
- **isort** import sorting
- **pytest** full test suite
- **pre-commit hooks** (optional)

---

## 📦 Project Structure
