

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

## Microsoft SSO setup

1. **Register an app** in [Azure Portal](https://portal.azure.com) → **App registrations** → New registration
2. **Add redirect URI**: `http://localhost:5000/auth/microsoft/callback` (update for your deployed domain)
3. **Certificates & secrets** → create a client secret (copy the value)
4. **API permissions** → ensure `openid`, `email`, `profile` (Microsoft Graph delegated) are granted
5. Copy **Client ID**, **Secret**, and **Tenant ID** into `.env`:
   ```
   MICROSOFT_CLIENT_ID=your-client-id
   MICROSOFT_CLIENT_SECRET=your-client-secret
   MICROSOFT_TENANT_ID=your-tenant-id
   MICROSOFT_REDIRECT_URI=http://localhost:5000/auth/microsoft/callback
   SSO_ALLOWED_EMAIL_DOMAINS=uwa.edu.au,student.uwa.edu.au
   ```
6. Run `python scripts/add_microsoft_sub_column.py` once to migrate existing DBs
7. Restart and visit `/auth/login` — the "Sign in with UWA Microsoft account" button will appear