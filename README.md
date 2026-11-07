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
- **Google sign-in** — Authlib (OpenID Connect)
- **Hosting** — [Render]([https://pxxlspace.cv](https://render.com/))

---

## Status

Active development — AIB Ship 2026 MVP.

Live at **[klasscred-8m7e.onrender.com](https://klasscred-8m7e.onrender.com/)**

## Admin dashboard

The platform overview is available at `/app/admin/`. Admin access is granted
only to existing accounts whose email addresses are listed in the server's
comma-separated `ADMIN_EMAILS` environment variable. Do not add this setting to
public client-side configuration. For example, set it to `admin@example.com`
to grant that account access; remove the address to revoke access.

Admins can search accounts, verify or unverify teachers and employers, deactivate
or reactivate accounts, and reassign or cancel open video-review assignments.
Deactivation is reversible and invalidates the account's existing login tokens.
After deploying the account-management update, run
`flask --app app db upgrade` to apply the database migration.

## Google sign-in

Create a Google OAuth client ID for a Web application and configure
`GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` on the server. Set
`GOOGLE_REDIRECT_URI` to the exact registered callback URL
`https://<your-app-host>/app/auth/google/callback` (use the corresponding
localhost URL for local development). Set `SECRET_KEY` to a persistent,
random server-side value because Flask uses its signed session to protect the
OAuth state. For HTTPS deployments, set `SESSION_COOKIE_SECURE=true`.

Google sign-in verifies the Google email and links it to an existing account
with that verified email. New users complete the existing role-specific profile
before an account is created. Apply the database migration with
`flask --app app db upgrade`.

## Background video reviews

Video confirmation queues AI review work and returns while the submission is
marked `ai_reviewing`. Run both the web and worker processes from the Procfile,
and configure `REDIS_URL` (or `CELERY_BROKER_URL`) to point to a Redis-compatible
broker. Apply database migrations with `flask --app app db upgrade` during
deployment (the Procfile release process runs this command automatically on
platforms that support release processes). The worker retries Gemini deadline
errors up to two times before marking the submission as failed.
