
# StockFlow

Inventory Management System built using Python, FastAPI, SQLite, HTML, CSS and JavaScript.

## Features

- User registration and login
- Organization-based data isolation
- Add, view and update products
- Unique SKU validation per organization
- Inventory dashboard
- Low-stock tracking
- JWT authentication

## Technology Stack

- Backend: Python, FastAPI
- Database: SQLite
- Frontend: HTML, CSS, JavaScript
- Authentication: JWT

## Run Locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Initialize database:

```bash
python -m app.init_db
```

Start backend:

```bash
python -m uvicorn app.main:app --reload
```

Start frontend in another terminal:

```bash
python -m http.server 5500 --directory app/frontend
```

Open http://127.0.0.1:5500

API documentation: http://127.0.0.1:8000/docs
