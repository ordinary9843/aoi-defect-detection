---
paths:
  - "**/*.py"
---

- Use Python 3.11; f-strings only for string formatting
- Backend entry point is `backend/main.py`; algorithm logic stays in `core/`
- Never hardcode file paths — use `os.path.join` or accept as arguments
- Dependencies: fastapi, uvicorn, torch, torchvision, opencv-python, scikit-learn, pillow, numpy
