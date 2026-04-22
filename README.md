# 🛡️ ContractGuard AI

> **AI-powered contract risk reviewer** — upload any PDF or DOCX contract and receive an instant risk score, red flags, and clause-by-clause breakdown.

![ContractGuard AI Screenshot](https://placehold.co/1280x720/4361ee/ffffff?text=ContractGuard+AI+Screenshot)

---

## ✨ Features

- 📄 **Upload PDF or DOCX** — drag-and-drop or click-to-browse, up to 10 MB
- 🤖 **GPT-4o Powered Analysis** — expert legal reasoning on every clause
- 📊 **Risk Scoring** — each clause rated Low / Medium / High with a 0–100% numeric score
- 🚩 **Red Flag Detection** — surfaces unfair, unusual, or dangerous clauses automatically
- 📝 **Plain-English Explanations** — complex legalese translated into clear language
- 💡 **Actionable Recommendations** — specific negotiation advice per clause
- 📋 **Executive Summary** — concise overall risk assessment
- 📥 **PDF Report Export** — downloadable professional report with colour coding
- 🔐 **Secure Auth** — JWT-based authentication with bcrypt password hashing
- 💳 **Stripe Integration** — pay-per-use ($3/contract) and subscription billing
- ⚡ **Async Analysis** — upload returns immediately; results arrive via polling

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | FastAPI (Python 3.11), async/await |
| **Database** | PostgreSQL 15 + SQLAlchemy (async) + Alembic |
| **AI** | OpenAI GPT-4o (structured JSON output) |
| **PDF parsing** | pdfplumber (PDF), python-docx (DOCX) |
| **Auth** | python-jose (JWT) + passlib (bcrypt) |
| **Payments** | Stripe |
| **Report generation** | ReportLab |
| **Frontend** | React 18 + Vite + TypeScript + TailwindCSS |
| **HTTP client** | Axios |
| **Routing** | React Router v6 |
| **Containerisation** | Docker + Docker Compose |
| **CI** | GitHub Actions (ruff + pytest + tsc) |

---

## 🚀 Local Development

### Prerequisites

- Python 3.11+
- Node.js 20+
- PostgreSQL 15 (or Docker)

### Option A — Docker Compose (recommended)

```bash
# 1. Clone the repo
git clone https://github.com/cristianofoc/contractguard-ai.git
cd contractguard-ai

# 2. Copy the example env file and fill in your keys
cp backend/.env.example backend/.env

# 3. Start all services (DB, backend, frontend)
docker-compose up --build

# 4. Run database migrations
docker-compose exec backend alembic upgrade head
```

Open:
- **Frontend**: http://localhost:5173
- **API docs**: http://localhost:8000/api/docs

---

### Option B — Manual setup

#### Backend

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Edit .env with your DATABASE_URL, OPENAI_API_KEY, etc.

# Run database migrations
alembic upgrade head

# Start the API server
uvicorn app.main:app --reload --port 8000
```

#### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start dev server (proxies /api to localhost:8000)
npm run dev
```

---

## 🔑 Environment Variables

Copy `backend/.env.example` to `backend/.env` and fill in the following:

| Variable | Description | Example |
|---|---|---|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://user:pass@localhost/contractguard` |
| `SECRET_KEY` | JWT signing secret (generate with `openssl rand -hex 32`) | `abc123...` |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token TTL in minutes | `30` |
| `OPENAI_API_KEY` | OpenAI API key | `sk-...` |
| `STRIPE_SECRET_KEY` | Stripe secret key | `sk_test_...` |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook signing secret | `whsec_...` |
| `STORAGE_BUCKET` | File storage bucket name | `contractguard-contracts` |
| `SUPABASE_URL` | Supabase project URL (optional) | `https://xxx.supabase.co` |
| `SUPABASE_KEY` | Supabase API key (optional) | `eyJ...` |
| `FREE_ANALYSES_LIMIT` | Number of free analyses per user | `1` |
| `PAY_PER_USE_PRICE_CENTS` | Price per analysis in cents | `300` |

---

## 📡 API Reference

### Authentication (`/api/v1/auth`)

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/register` | Register with email + password → returns JWT |
| `POST` | `/login` | Login → returns JWT |
| `GET` | `/me` | Get current user profile |

### Contracts (`/api/v1/contracts`)

All endpoints require `Authorization: Bearer <token>`.

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/upload` | Upload PDF/DOCX (multipart) → creates analysis, returns ID |
| `GET` | `/` | List user's analyses (paginated) |
| `GET` | `/{analysis_id}` | Get full analysis result |
| `DELETE` | `/{analysis_id}` | Delete an analysis |

### Health

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Returns `{"status": "ok"}` |

Interactive docs available at **`/api/docs`** (Swagger UI).

---

## 🗄 Database Schema

### `users`
| Column | Type | Notes |
|---|---|---|
| `id` | UUID | Primary key |
| `email` | string | Unique |
| `hashed_password` | string | bcrypt |
| `is_active` | boolean | Default `true` |
| `free_analyses_used` | integer | Default `0` |
| `stripe_customer_id` | string | Nullable |
| `created_at` | timestamp | Auto |
| `updated_at` | timestamp | Auto |

### `contract_analyses`
| Column | Type | Notes |
|---|---|---|
| `id` | UUID | Primary key |
| `user_id` | UUID | FK → users |
| `filename` | string | |
| `file_url` | string | Nullable (storage URL) |
| `status` | enum | `pending` \| `processing` \| `completed` \| `failed` |
| `overall_risk_score` | float | 0.0–1.0, nullable |
| `overall_risk_level` | enum | `low` \| `medium` \| `high`, nullable |
| `summary` | text | Nullable |
| `clauses` | JSONB | Array of clause objects |
| `created_at` | timestamp | Auto |
| `updated_at` | timestamp | Auto |

---

## 🗺 Roadmap

- [ ] File storage via Supabase Storage / AWS S3
- [ ] Stripe subscription management portal
- [ ] Compare two contracts side-by-side
- [ ] Custom clause library / watchlist
- [ ] Team / multi-user workspaces
- [ ] API key access for developers
- [ ] Mobile-friendly PWA
- [ ] Support for more file types (JPEG scans via OCR)
- [ ] Integration with DocuSign / Adobe Sign

---

## 🧪 Running Tests

```bash
cd backend
pytest tests/ -v
```

### Linting

```bash
cd backend
ruff check app tests

cd frontend
npm run typecheck
```

---

## 📦 Project Structure

```
contractguard-ai/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entrypoint
│   │   ├── config.py            # Settings (pydantic-settings)
│   │   ├── database.py          # Async SQLAlchemy engine
│   │   ├── models/              # ORM models (User, ContractAnalysis)
│   │   ├── schemas/             # Pydantic v2 schemas
│   │   ├── api/
│   │   │   ├── routes/          # auth, contracts, health endpoints
│   │   │   └── dependencies.py  # get_current_user, get_db
│   │   ├── services/
│   │   │   ├── ai_engine.py     # GPT-4o contract analyzer
│   │   │   ├── pdf_parser.py    # PDF/DOCX text extraction
│   │   │   ├── report_generator.py  # ReportLab PDF reports
│   │   │   └── stripe_service.py    # Stripe integration
│   │   └── utils/
│   │       └── security.py      # JWT + bcrypt
│   ├── alembic/                 # DB migrations
│   ├── tests/                   # pytest test suite
│   ├── requirements.txt
│   ├── .env.example
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/          # Navbar, UploadZone, RiskScore, ClauseCard
│   │   ├── pages/               # Home, Dashboard, Analysis, Login
│   │   ├── services/api.ts      # Axios API client
│   │   ├── App.tsx              # Router setup
│   │   └── main.tsx
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.ts
├── docker-compose.yml
├── .github/workflows/ci.yml
└── README.md
```

---

## 📄 License

MIT © 2024 ContractGuard AI