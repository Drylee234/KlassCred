# KlassCred

> A teacher verification and hiring platform — LinkedIn for Teachers.

KlassCred connects verified teachers to verified employers through a structured, multi-stage credentialing pipeline. Built as an AIB Ship 2026 MVP.

---

## What it does

Teachers go through a full screening process before becoming discoverable:

- Profile, work history, and reference submission
- Identity verification
- Proctored subject exam
- AI-generated teaching scenario + video demonstration
- AI and human review
- Composite rating score

Employers (schools or parents) are also verified, then search and hire from the credentialed teacher pool.

---

## Stack

- **Backend** — Flask, SQLAlchemy, Marshmallow
- **Database** — PostgreSQL (Supabase)
- **Video** — Cloudinary
- **Background jobs** — Celery with Redis
- **Auth** — JWT + bcrypt
- **Hosting** — [Pxxl](https://pxxlspace.cv)

---

## Status

Active development — AIB Ship 2026 MVP.

Live at **[klasscred.pxxlspace.cv](https://klasscred.pxxlspace.cv)**

## Background video reviews

Video confirmation queues AI review work and returns while the submission is
marked `ai_reviewing`. Run both the web and worker processes from the Procfile,
and configure `REDIS_URL` (or `CELERY_BROKER_URL`) to point to a Redis-compatible
broker. Apply database migrations with `flask --app app db upgrade` during
deployment (the Procfile release process runs this command automatically on
platforms that support release processes). The worker retries Gemini deadline
errors up to two times before marking the submission as failed.
