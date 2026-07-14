# AI Rolodex Agent

An AI-powered searchable rolodex. Paste a LinkedIn profile in, get back a
structured, semantically-searchable "why this person matters" entry — not
just a saved contact card.

This is **not** a contact manager. It's a knowledge base of professional
relationships, built so a team can ask *"who do we know who does X?"* and get
back the right people, ranked by relevance.

---

## How it works

```
LinkedIn profile text/export
        │
        ▼
  clean_profile_text()        strips nav chrome, ads, duplicate lines
        │
        ▼
  extract_profile()           Gemini API (Google GenAI SDK), structured JSON
        │                     output → identity, capabilities, and (the hard
        │                       part) *relevance*: why someone would search for them
        ▼
  build_embedding_text()      concatenates summary + relevance + skills
        │                     + capabilities
        ▼
  embed_text()                Gemini Embeddings (gemini-embedding-2) → 1536-dim vector
        │
        ▼
  find_duplicates()           exact URL match → fuzzy name match → cosine
        │                     similarity against existing embeddings
        ▼
  Postgres (pgvector)         one row per contact, JSONB list columns,
                               ivfflat index for semantic search
```

Search works two ways:
- **Structured filters** — role, company, industry, skills, technologies, tags.
- **Semantic search** — cosine similarity over the embedding column.
- **Natural language** ("who has healthcare experience?") is parsed by the LLM
  into a combination of both, then executed as a hybrid query.

---

## Tech stack

| Layer      | Choice                                                              |
|------------|----------------------------------------------------------------------|
| Frontend   | Next.js 15 (App Router), React 19, TypeScript, TailwindCSS           |
| Backend    | FastAPI, SQLAlchemy 2.0, Pydantic v2                                  |
| Database   | PostgreSQL 16 + pgvector                                             |
| AI         | Gemini API via Google GenAI SDK (structured JSON output + embeddings) |
| Deployment | Vercel (frontend) · Railway/Render (backend) · Supabase (database)   |

---

## Project structure

```
rolodex-agent/
├── backend/
│   ├── app/
│   │   ├── core/            # config, database engine/session
│   │   ├── models/           # SQLAlchemy models (Contact, SearchLog)
│   │   ├── schemas/          # Pydantic request/response contracts
│   │   ├── services/         # cleaning, extraction, embeddings, dedup, search, ingestion
│   │   ├── routers/           # /contacts, /search, /dashboard
│   │   └── main.py
│   ├── migrations/001_init.sql
│   ├── sample_data/
│   │   ├── linkedin_profiles/     # 5 raw sample profiles (messy paste format)
│   │   └── generated_entries/     # 5 example extraction outputs
│   ├── tests/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── app/                  # dashboard, /search, /contacts, /contacts/[id], /ingest
│   ├── components/           # ui/ (primitives), rolodex/ (feature components), layout/
│   ├── hooks/                # theme + toast providers
│   ├── lib/                  # api client, utils
│   ├── types/                # TS types mirroring backend schemas
│   ├── package.json
│   ├── Dockerfile
│   └── .env.example
└── docker-compose.yml         # full local stack: db + backend + frontend
```

### Design system

Dark-first, built around a physical rolodex/index-card metaphor rather than a
generic SaaS dashboard: cards carry a die-cut "index tab" with the contact's
initial, and the relevance summary is rendered as a highlighter-style
annotation — the one intentionally bold element on an otherwise quiet,
disciplined UI. Type pairs a characterful serif (Fraunces) for names/headings
with Inter for body text and IBM Plex Mono for tags, stats, and metadata.
Colors are a warm-ivory-on-ink-navy palette with an indigo "signal" accent and
an amber "tab" accent (see `frontend/app/globals.css` for the token values).

---

## HOW TO RUN LOCALLY

These steps assume no prior setup — just Docker, or Python + Node if you
prefer running things natively.

### Option A — Docker Compose (fastest)

1. **Install Docker Desktop** if you don't have it: https://www.docker.com/products/docker-desktop/
2. **Get a Gemini API key**: go to https://aistudio.google.com/apikey, sign
   in with a Google account, and click "Create API key".
3. **Clone/unzip the project** and open a terminal in its root folder.
4. **Configure Gemini (optional for boot, required for AI features):**
   ```bash
   cd backend
   cp .env.example .env
   ```
   Open `backend/.env` and paste your key into `GEMINI_API_KEY=`. You may skip
   this step if you only want to boot and inspect the stack: the database,
   frontend, API, health checks, and Swagger docs all run without a key, while
   AI ingestion/search endpoints return a clear 502 until one is configured.
5. **No frontend env file is needed for Docker Compose.** The frontend image
   gets `NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1` from the build arg
   in `docker-compose.yml`, because Next.js inlines public variables at build
   time. `frontend/.env` is only needed for the native `npm run dev` workflow.
6. **Start everything** from the project root (or `cd ..` if you completed
   step 4):
   ```bash
   docker compose up --build
   ```
   Compose waits for PostgreSQL and the backend readiness check before starting
   dependent services. On first boot it installs pgvector, runs
   `001_init.sql`, and then starts the API and standalone Next.js server.
7. **Open the services:**
   - App: http://localhost:3000
   - API docs: http://localhost:8000/docs
   - Readiness check: http://localhost:8000/health/ready
8. **Load the sample profiles** (optional but recommended for a first look):
   with the stack running, in a new terminal:
   ```bash
   cd backend
   python3 -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   python3 scripts/seed_sample_data.py
   ```
   This ingests the 5 sample LinkedIn profiles in `sample_data/linkedin_profiles/`
   through the real pipeline (Gemini extraction + embeddings), so you'll see
   real generated rolodex entries rather than the static fixture JSON.

Useful commands:
```bash
docker compose ps              # all three services should show healthy
docker compose logs -f         # follow application and database logs
docker compose down            # stop containers and preserve database data
docker compose down -v         # stop containers and wipe the local database
```

### Option B — Run natively (no Docker)

Use Python 3.12 and Node.js 20 for the versions pinned by this project.

1. **Install PostgreSQL 16** locally (e.g. `brew install postgresql@16` on
   macOS, or use your OS package manager).
2. **Enable pgvector.** The easiest path is Docker just for the database:
   ```bash
   docker run -d --name rolodex-db -p 5432:5432 \
     -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=rolodex \
     pgvector/pgvector:pg16
   ```
   If you're not using Docker at all, install the `pgvector` extension for
   your Postgres build (see https://github.com/pgvector/pgvector#installation),
   then run:
   ```sql
   CREATE EXTENSION vector;
   ```
3. **Run the migration:**
   ```bash
   psql postgresql://postgres:postgres@localhost:5432/rolodex -f backend/migrations/001_init.sql
   ```
4. **Set up the backend:**
   ```bash
   cd backend
   python3 -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   cp .env.example .env   # then paste your GEMINI_API_KEY into .env
   uvicorn app.main:app --reload --port 8000
   ```
   Visit http://localhost:8000/docs to confirm the API is up (interactive
   Swagger UI).
5. **Set up the frontend**, in a second terminal:
   ```bash
   cd frontend
   npm install
   cp .env.example .env
   npm run dev
   ```
6. **Open** http://localhost:3000 and paste in a LinkedIn profile (use the
   "Use a sample profile" button on the Add Contact page for a quick test).

### Running tests

```bash
cd backend
source .venv/bin/activate
pytest -v
```

The included tests cover input cleaning, the Gemini structured-output JSON
schema lockdown, fuzzy name-matching thresholds, schema validation, and API
route registration/health. They don't require a live Postgres or Gemini key.
Full end-to-end ingestion (`/contacts/ingest`) is exercised manually via the
UI or the example `curl` requests below, since it requires both a live
database and a real `GEMINI_API_KEY`.

---

## HOW TO DEPLOY FOR FREE

Frontend → **Vercel** · Backend → **Railway** (or **Render** if you'd rather)
· Database → **Supabase**. All three have usable free tiers.

### 1. Push the project to GitHub

```bash
git init
git add .
git commit -m "Initial commit: AI Rolodex Agent"
```
Create a new repository on https://github.com/new, then:
```bash
git remote add origin https://github.com/<your-username>/rolodex-agent.git
git branch -M main
git push -u origin main
```

### 2. Database — Supabase

1. Go to https://supabase.com, sign up, click **New project**.
2. Pick a name, a strong database password (save it), and a region close to
   you. Wait ~2 minutes for provisioning.
3. Once ready, go to **SQL Editor** → **New query**, paste in the full
   contents of `backend/migrations/001_init.sql`, and run it. Supabase
   Postgres ships with `pgvector` pre-installed, so `CREATE EXTENSION vector`
   will succeed immediately.
4. Go to **Project Settings → Database → Connection string**, copy the URI
   (mode: "Session", not "Transaction", for a simple deployment), and convert
   it to SQLAlchemy's driver form:
   ```
   postgresql+psycopg://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
   ```

### 3. Backend — Railway

1. Go to https://railway.app, sign up, and connect your GitHub account.
2. **New Project → Deploy from GitHub repo** → select your `rolodex-agent`
   repo.
3. Railway will detect multiple folders; set the **Root Directory** to
   `backend` in the service settings (Settings → Source → Root Directory).
4. Add environment variables under **Variables**:
   - `DATABASE_URL` = the Supabase connection string from step 2
   - `GEMINI_API_KEY` = your Gemini API key
   - `CORS_ORIGINS` = the Vercel URL you'll get in step 4 (you can add/update
     this after step 4 — Railway redeploys automatically on variable changes)
5. Railway auto-detects the `Dockerfile` and builds/deploys it. Once live,
   copy the generated public URL (Settings → Networking → **Generate Domain**),
   e.g. `https://rolodex-backend-production.up.railway.app`.
6. Confirm it's working: visit `https://<your-backend-url>/health` — you
   should see `{"status":"ok",...}`.

   *(If you'd rather use Render instead: New → Web Service → connect the repo
   → Root Directory `backend` → Render auto-detects the Dockerfile → add the
   same environment variables → deploy.)*

### 4. Frontend — Vercel

1. Go to https://vercel.com, sign up, click **Add New → Project**, and import
   your GitHub repo.
2. Set **Root Directory** to `frontend` in the import settings.
3. Add an environment variable:
   - `NEXT_PUBLIC_API_URL` = `https://<your-backend-url>/api/v1`

   This must be the **full absolute URL**, including `https://` and the
   `/api/v1` suffix - not just the bare domain (e.g. `your-backend.up.railway.app`
   on its own). A bare domain isn't rejected as invalid HTML/JS syntax, but
   `fetch()` silently treats it as a *relative* path and resolves it against
   the current page's own origin, producing nonsense URLs like
   `https://your-app.vercel.app/your-backend.up.railway.app/dashboard` and a
   confusing 404 - the frontend validates this at runtime and will show a
   clear error identifying the exact problem if it's misconfigured, rather
   than a silent wrong request.
4. Click **Deploy**. Vercel builds and gives you a URL like
   `https://rolodex-agent.vercel.app`.

### 5. Connect the two (update CORS)

Go back to Railway (or Render) → your backend service → **Variables** →
update `CORS_ORIGINS` to your real Vercel URL, e.g.
`https://rolodex-agent.vercel.app`. Redeploy (Railway does this automatically
on variable save).

### 6. Load sample data on the deployed app (optional)

From your machine, with the backend `.env` pointed at the same
`DATABASE_URL` and `GEMINI_API_KEY` you used in Railway:
```bash
cd backend
python3 scripts/seed_sample_data.py --api-url https://<your-backend-url>/api/v1
```

### 7. Test the deployed application

1. Open your Vercel URL.
2. Go to **Add contact**, click "Use a sample profile", click **Generate contact**.
3. You should land on a new contact page with extracted skills, capabilities,
   and a relevance summary within a few seconds.
4. Go to **Search**, type "who has payments infrastructure experience?", and
   confirm it returns the contact you just added.

If a request fails, check: (a) the Vercel env var points at your Railway URL
with the exact `/api/v1` suffix, (b) `CORS_ORIGINS` on Railway includes your
Vercel URL (a trailing slash is fine - it's normalized away automatically),
(c) the Railway logs for `GEMINI_API_KEY` or database connection errors. If
you also need Vercel *preview* deployments (which get their own unique URLs)
to work, set `CORS_ORIGIN_REGEX` to a pattern matching your project, e.g.
`https://rolodex-agent.*\.vercel\.app` - this is checked in addition to, not
instead of, `CORS_ORIGINS`.

---

## API reference — example requests & responses

Interactive docs (Swagger UI) are always available at `/docs` on the running
backend (e.g. http://localhost:8000/docs).

### Ingest a profile

```bash
curl -X POST http://localhost:8000/api/v1/contacts/ingest \
  -H "Content-Type: application/json" \
  -d '{
        "source_type": "text",
        "linkedin_url": "https://www.linkedin.com/in/priya-shenoy-example",
        "raw_text": "Priya Shenoy\nSenior Backend Engineer @ Finlynk...(full pasted profile text)"
      }'
```

Response (new contact):
```json
{
  "status": "created",
  "contact": {
    "id": "b2f1c2b0-...",
    "full_name": "Priya Shenoy",
    "current_title": "Senior Backend Engineer",
    "current_company": "Finlynk",
    "relevance_summary": "Priya is the person to talk to when a payments or ledger system needs to be provably correct...",
    "relevance_tags": ["FinTech specialist", "Payments infrastructure", "Distributed systems"],
    "...": "see backend/sample_data/generated_entries/01_priya_shenoy.json for the full shape"
  },
  "duplicates": []
}
```

Response (likely duplicate found instead of creating):
```json
{
  "status": "possible_duplicate",
  "contact": null,
  "duplicates": [
    {
      "contact": { "id": "...", "full_name": "Priya Shenoy", "...": "..." },
      "match_reasons": ["Exact LinkedIn URL match"],
      "similarity_score": 1.0
    }
  ]
}
```

### Natural-language search

```bash
curl -X POST http://localhost:8000/api/v1/search/natural-language \
  -H "Content-Type: application/json" \
  -d '{"query": "who has healthcare experience?"}'
```

```json
{
  "query": "who has healthcare experience?",
  "interpreted_filters": {
    "industry": "Healthcare",
    "skills": [],
    "technologies": [],
    "tags": ["Healthcare domain expertise"]
  },
  "results": [
    { "contact": { "full_name": "Sofia Ibarra", "...": "..." }, "score": 0.87, "matched_on": ["semantic"] }
  ],
  "total": 1
}
```

### Dashboard stats

```bash
curl http://localhost:8000/api/v1/dashboard
```

### Full endpoint list

| Method | Path                              | Purpose                                   |
|--------|-----------------------------------|--------------------------------------------|
| POST   | `/api/v1/contacts/ingest`         | Extract + create (returns duplicates if found) |
| POST   | `/api/v1/contacts/ingest/force`   | Same, but skips duplicate detection        |
| GET    | `/api/v1/contacts`                | List contacts (paginated)                  |
| GET    | `/api/v1/contacts/{id}`           | Get one contact                            |
| PATCH  | `/api/v1/contacts/{id}`           | Update notes / relevance tags              |
| DELETE | `/api/v1/contacts/{id}`           | Delete a contact                           |
| POST   | `/api/v1/contacts/merge`          | Merge a duplicate into an existing contact |
| POST   | `/api/v1/search`                  | Structured + optional semantic search      |
| POST   | `/api/v1/search/natural-language` | AI search box (LLM-parsed filters)         |
| GET    | `/api/v1/dashboard`               | Aggregate stats for the homepage           |
| GET    | `/health`                         | Health check                               |

---

## DEMO WALKTHROUGH

1. **Open the dashboard** — you'll see total contacts, top skills/industries,
   and a search box front and center.
2. **Click "Add contact"** in the sidebar (or go to `/ingest`).
3. **Click "Use a sample profile"** to autofill Priya Shenoy's LinkedIn text,
   or paste your own.
4. **Click "Generate contact."** The pipeline cleans the text, sends it to
   Gemini for structured extraction, generates an embedding, and checks for
   duplicates — you're redirected to the new contact's page in a few seconds.
5. **Look at the contact page**: the "Why they matter" callout is the
   relevance summary; skills/technologies/domains/capabilities are broken out
   separately in the sidebar; experience renders as a timeline.
6. **Go to Search** and type something like *"who has built payments
   infrastructure?"* — the AI search box converts this into filters (shown
   above the results) plus a semantic query, and returns matching contacts.
7. **View matching contacts** as index cards, each with its top relevance tag
   shown as a highlighter-style callout.
8. **Open a contact and add a note** ("Met at Hackathon", "Referral", etc.) in
   the Connection Notes section — this is saved via `PATCH /contacts/{id}`.
9. **Add a second, similar contact** (e.g. paste the same profile again, or a
   near-duplicate) — you'll see the duplicate-detection modal instead of a
   silent second entry, with the option to merge.
10. **Repeat the search** from step 6 — the new/merged contact now shows up,
    demonstrating that semantic search picks up newly ingested profiles
    immediately.

---

## Known limitations / honest notes

- **Fetching a LinkedIn URL directly is not implemented.** LinkedIn requires
  an authenticated session to view full profile data, so `source_type: "url"`
  intentionally raises a clear error rather than silently scraping or
  hallucinating a profile. Paste the profile's text or an exported copy
  instead (the UI's ingest form is built around pasting text, with the URL
  field kept only for reference/dedup purposes).
- **`sample_data/generated_entries/*.json`** are static fixtures matching the
  exact `ContactRead` response shape, included so the repo is inspectable
  without an API key. Running `scripts/seed_sample_data.py` against a live
  backend generates real entries via Gemini instead.
- **ivfflat index quality** depends on having enough rows for its `lists`
  parameter to be well-tuned (set to 100 in the migration, reasonable up to a
  few thousand contacts). For a much larger rolodex, consider `hnsw` instead
  (supported by pgvector 0.5+) or re-tuning `lists` to roughly
  `sqrt(row_count)`.
- **Gemini model deprecations are handled by config, not code.** `GEMINI_TEXT_MODEL`
  and `GEMINI_EMBEDDING_MODEL` are the only place model names appear. On
  startup (if `GEMINI_API_KEY` is set), the app calls Gemini's `models.get`
  for both and refuses to start with a clear error if either has been
  deprecated/renamed - check the startup logs, not a mid-request stack
  trace, if a deployment fails after a Google model change. See
  https://ai.google.dev/gemini-api/docs/models for the current model list
  and https://ai.google.dev/gemini-api/docs/deprecations for shutdown dates.
