# Backend Report — UWA Marketplace

## Stack

| Package | Version | Role |
|---|---|---|
| Flask | ≥ 3.0 | Web framework |
| Flask-SQLAlchemy | ≥ 3.1 | ORM / database layer |
| Flask-Login | ≥ 0.6 | Session-based authentication |
| Flask-WTF | ≥ 1.2 | Form handling and CSRF protection |
| Werkzeug | ≥ 3.0 | Password hashing, file utilities |
| email-validator | ≥ 2.0 | Email field validation |

The database is SQLite (`marketplace.db`), stored at the project root. No external database server is required.

---

## Application Structure

```
app/
├── __init__.py          # Application factory
├── models.py            # SQLAlchemy models
├── forms.py             # WTForms form classes
└── routes/
    ├── auth.py          # /auth — login, register, password reset
    ├── listings.py      # /listings — browse, create, edit, search
    └── profile.py       # /user — profile view, settings
config.py                # Configuration class
run.py                   # Entry point
```

---

## Application Factory — `app/__init__.py`

The app uses the **application factory pattern** via `create_app()`. This function:

1. Creates the Flask app instance and loads configuration from `Config`
2. Initialises extensions: `SQLAlchemy`, `LoginManager`, `CSRFProtect`
3. Imports and registers the three route blueprints
4. Defines a root route (`/`) that redirects to the listings index

Using a factory rather than a module-level app instance makes the app easier to test and configure per environment.

---

## Configuration — `config.py`

A single `Config` class centralises all settings:

- `SECRET_KEY` — read from the `SECRET_KEY` environment variable; falls back to a hardcoded dev string
- `SQLALCHEMY_DATABASE_URI` — SQLite file at the project root
- `MAX_CONTENT_LENGTH` — 2 MB upload size cap enforced by Flask before the route handler runs
- `UPLOAD_FOLDER` — absolute path to `app/static/uploads/`

---

## Data Layer — `app/models.py`

Three SQLAlchemy models form the schema.

### `User`

| Column | Type | Notes |
|---|---|---|
| `id` | Integer PK | |
| `username` | String(64) | Unique |
| `email` | String(120) | Unique |
| `password_hash` | String(256) | `pbkdf2:sha256` via Werkzeug |
| `member_since` | DateTime | Defaults to `utcnow` |
| `bio` | Text | Optional, defaults to `''` |
| `avatar_url` | String(256) | Nullable |

`User` implements `flask_login.UserMixin`, which provides the `is_authenticated`, `is_active`, `is_anonymous`, and `get_id()` methods required by Flask-Login.

### `Listing`

| Column | Type | Notes |
|---|---|---|
| `id` | Integer PK | |
| `title` | String(120) | |
| `description` | Text | |
| `price` | Float | AUD |
| `category` | String(64) | One of five fixed choices |
| `image_url` | String(256) | Nullable; relative static path |
| `is_active` | Boolean | `True` = for sale, `False` = sold |
| `show_history` | Boolean | Whether edit history is public |
| `created_at` | DateTime | Defaults to `utcnow` |
| `seller_id` | Integer FK → `user.id` | |

### `ListingEdit`

Audit log — one row is written per changed field whenever a listing is edited.

| Column | Type | Notes |
|---|---|---|
| `id` | Integer PK | |
| `listing_id` | Integer FK → `listing.id` | |
| `edited_at` | DateTime | Defaults to `utcnow` |
| `field_name` | String(64) | e.g. `'title'`, `'price'` |
| `old_value` | Text | String-cast previous value |
| `new_value` | Text | String-cast updated value |

**Relationships:**

- `User` → `Listing`: one-to-many via `listings` backref on `seller`
- `Listing` → `ListingEdit`: one-to-many via `edits`, ordered by `edited_at` descending

The `@login_manager.user_loader` callback at module level lets Flask-Login reload the user from the session using `User.query.get(int(user_id))`.

---

## Forms — `app/forms.py`

All forms inherit from `FlaskForm` (Flask-WTF), which automatically adds CSRF token validation.

| Form | Used by | Notable validators |
|---|---|---|
| `LoginForm` | `auth.login` | `Email()`, `DataRequired()` |
| `RegisterForm` | `auth.register` | Unique email/username checked against DB in custom `validate_*` methods |
| `EditProfileForm` | `profile.edit` | `Length(max=300)` on bio |
| `ListingForm` | `listings.new` | `NumberRange(min=0)` on price; `FileAllowed` restricts to image types |
| `EditListingForm` | `listings.edit` | Same as above plus `show_history` `BooleanField` |
| `ChangeEmailForm` | `profile.settings_email` | Unique email check; requires `current_password` |
| `ChangePasswordForm` | `profile.settings_password` | `EqualTo` confirm; requires `current_password` |
| `DeleteAccountForm` | `profile.settings_delete` | Requires `current_password` confirmation |
| `ForgotPasswordForm` | `auth.forgot_password` | `Email()` |
| `ResetPasswordForm` | `auth.reset_password` | `Length(min=8)`, `EqualTo` confirm |

The three settings forms (`ChangeEmailForm`, `ChangePasswordForm`, `DeleteAccountForm`) are instantiated with distinct `prefix` arguments (`'email'`, `'password'`, `'delete'`) so all three can coexist on a single settings page without field name collisions.

---

## Routes

### Auth Blueprint — `app/routes/auth.py` (`/auth`)

| Method | Path | Description |
|---|---|---|
| GET/POST | `/auth/login` | Verifies email + password hash; redirects to `next` param or listings index |
| GET/POST | `/auth/register` | Creates a new `User`, logs them in immediately |
| GET/POST | `/auth/forgot-password` | Looks up user by email; stores email in `session['reset_email']` |
| GET/POST | `/auth/reset-password` | Reads `session['reset_email']`; updates `password_hash`; clears session key |
| GET | `/auth/logout` | Calls `logout_user()`; redirects to login |

Password reset is **session-based**: no email token is sent. The user must navigate the two pages in sequence within the same browser session.

### Listings Blueprint — `app/routes/listings.py` (`/listings`)

| Method | Path | Description |
|---|---|---|
| GET | `/listings/` | Browse active listings; supports `?q=` search via `ILIKE` |
| GET | `/listings/api/search` | JSON endpoint; same query, returns up to 20 results |
| GET | `/listings/<id>` | Detail view for a single listing |
| GET/POST | `/listings/new` | Create a listing (login required) |
| GET/POST | `/listings/<id>/edit` | Edit a listing; ownership checked; field changes logged to `ListingEdit` |
| POST | `/listings/<id>/close` | Mark listing as sold (`is_active = False`); ownership checked |

**Image uploads** (`_save_image`): the file extension is validated against an allowlist, the file is renamed to a `uuid.uuid4().hex` string to prevent collisions and path traversal, then saved to `UPLOAD_FOLDER`. The returned value is a Flask `url_for('static', ...)` path.

**Edit tracking**: the edit route iterates over `['title', 'description', 'price', 'category']`, compares old and new values, and writes a `ListingEdit` row for each changed field. Image changes and the `show_history` toggle are applied but not logged in the audit history.

### Profile Blueprint — `app/routes/profile.py` (`/user`)

| Method | Path | Description |
|---|---|---|
| GET | `/user/<id>` | Public profile; listing filter via `?filter=active\|sold\|all` |
| GET | `/user/me` | Redirects to the logged-in user's profile |
| GET/POST | `/user/me/edit` | Edit username and bio |
| GET | `/user/me/settings` | Settings page (renders all three settings forms) |
| POST | `/user/me/settings/email` | Change email; verifies current password |
| POST | `/user/me/settings/password` | Change password; verifies current password |
| POST | `/user/me/settings/delete` | Delete account and all listings; verifies current password |

Account deletion deletes all of the user's listings with a bulk `Listing.query.filter_by(seller_id=user.id).delete()` before removing the user row, avoiding foreign key orphans.

---

## Security Notes

- **CSRF**: all forms are protected by Flask-WTF's `CSRFProtect`, which validates the hidden token on every POST.
- **Password storage**: `werkzeug.security.generate_password_hash` with `pbkdf2:sha256`; never stored in plaintext.
- **File uploads**: extension allowlist + UUID rename; `MAX_CONTENT_LENGTH` caps payload size at 2 MB.
- **Authorisation**: ownership of listings is checked before edit or close actions. Settings mutations require the current password.
- **Login protection**: sensitive routes use `@login_required`; `LoginManager.login_view` redirects unauthenticated requests to `/auth/login`.
- **Secret key**: should be set via the `SECRET_KEY` environment variable in production; the hardcoded fallback is for development only.
