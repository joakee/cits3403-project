
# CITS3403/CITS5505

# Agile Web Development: Project

### The University of Western Australia
###### Semester 1, 2026

---
### Authors:
- Tobias Collier (23728469)
- Colin Melville (23170781)
- James Oakey (22709404)
- Harjaap Singh (24291609)

---

## UWA Marketplace

A student-to-student marketplace web application built with Flask. Users can register, browse and post listings, chat in real-time, manage a storefront, and report content — all within a university-verified ecosystem.

Tech stack: **Flask**, **SQLAlchemy**, **SQLite**, **SocketIO**, **Bootstrap 5**, **Jinja2**

---

## Prerequisites

- **Python 3.12 or later**
- `uv` (recommended) or `pip` + `venv`

---

## Quick start

### 1. Clone and enter the project

```bash
cd cits3403-project
```

### 2. Create a virtual environment and install dependencies

**With uv (recommended — uses `uv.lock`):**

```bash
uv sync
source .venv/bin/activate
```

**With pip:**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure environment variables

Copy the template below into a `.env` file at the project root:

```
SECRET_KEY=dev-secret-change-in-prod
```

That single variable is enough for local development. Email sending (Brevo/Sendinblue SMTP) and Microsoft SSO are optional — the app runs without them.

### 4. (Optional) Seed the database

```bash
python seed_db.py
```

This creates sample users, listings, and conversations. All seeded accounts use the password **`password123`**:

| Role | Email |
|---|---|
| Admin | `admin@admin.com` |
| Regular user | `alice@example.com` |
| Store account | `techbazaar@store.com` |
| Moderator | (login as admin and promote a user) |

To add images to seeded listings, run `python seed_images.py` afterwards.

### 5. Run the application

```bash
python run.py
```

The app starts at **http://localhost:5001** with SocketIO and debug mode enabled.

---

## Running tests

The test suite uses `pytest` with an in-memory SQLite database:

```bash
pytest
```

Selenium browser tests (`test_selenium.py`, `test_selenium_chat.py`) require Playwright browsers. Install them once:

```bash
playwright install
```

---

## Environment variables reference

All values are read from `.env` at the project root.

| Variable | Required | Default | Purpose |
|---|---|---|---|
| `SECRET_KEY` | Yes | — | Flask session signing key |
| `BREVO_EMAIL` | No | — | SMTP username for email (Brevo) |
| `BREVO_PASSWORD` | No | — | SMTP password for email (Brevo) |
| `MAIL_DEFAULT_SENDER` | No | — | From-address on outgoing emails |
| `MICROSOFT_CLIENT_ID` | No | — | Azure AD app registration client ID |
| `MICROSOFT_CLIENT_SECRET` | No | — | Azure AD app registration secret |
| `MICROSOFT_TENANT_ID` | No | `common` | Azure AD tenant |
| `MICROSOFT_REDIRECT_URI` | No | `http://localhost:5000/auth/microsoft/callback` | OAuth callback URL |
| `SSO_ALLOWED_EMAIL_DOMAINS` | No | `uwa.edu.au,student.uwa.edu.au` | Comma-separated email domain allowlist for SSO |

---

## Microsoft SSO (optional)

1. Register an app in the [Azure Portal](https://portal.azure.com) → **App registrations** → New registration.
2. Add the redirect URI: `http://localhost:5000/auth/microsoft/callback`.
3. Under **Certificates & secrets**, create a client secret and copy the value.
4. Under **API permissions**, grant `openid`, `email`, and `profile` (Microsoft Graph, delegated).
5. Add to `.env`:

```
MICROSOFT_CLIENT_ID=your-client-id
MICROSOFT_CLIENT_SECRET=your-client-secret
MICROSOFT_TENANT_ID=your-tenant-id
MICROSOFT_REDIRECT_URI=http://localhost:5000/auth/microsoft/callback
SSO_ALLOWED_EMAIL_DOMAINS=uwa.edu.au,student.uwa.edu.au
```

6. Run `python scripts/add_microsoft_sub_column.py` if you are using an existing database created before the SSO column was added.
7. Restart the app. A "Sign in with UWA Microsoft account" button will appear on the login page.

---

## Project structure (abridged)

```
cits3403-project/
├── run.py                  Entry point
├── config.py               Flask configuration
├── pyproject.toml          Dependencies (uv)
├── requirements.txt        Dependencies (pip)
├── seed_db.py              DB seed script
├── app/
│   ├── __init__.py         Application factory
│   ├── models.py           SQLAlchemy models
│   ├── forms.py            WTForms definitions
│   ├── routes/             Blueprint modules (auth, chat, listings, etc.)
│   ├── templates/          Jinja2 templates
│   └── static/             CSS, JS, fonts, uploads
├── tests/                  Pytest test suite
└── scripts/                Utility scripts
```
