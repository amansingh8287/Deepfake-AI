# Backend

Run the API locally:

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The backend automatically creates the SQLite database and exposes OpenAPI docs at `/docs`.

