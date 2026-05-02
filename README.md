# RepoInsight

Full-stack app to analyze a public GitHub repository URL and show repository insights.

## Run Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

## Run Frontend

```bash
cd frontend
npm install
npm run dev
```

Backend runs at `http://localhost:8000`, frontend at `http://localhost:5173`.
