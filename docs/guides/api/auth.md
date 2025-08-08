# Authentication API

## GET /me
Returns the authenticated user's profile.

**Response**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "name": "Example User",
  "avatar_url": "https://example.com/avatar.png",
  "created_at": "2025-01-01T00:00:00Z",
  "last_login_at": "2025-01-02T00:00:00Z"
}
```

## GET /auth/github/login
Starts the GitHub OAuth flow. Redirects the browser to GitHub.

## GET /auth/github/callback
Handles the OAuth callback, creates a session cookie and redirects to `/`.

## POST /auth/logout
Clears the session cookie and CSRF token.

## POST /auth/magic-link
(Disabled by default) Request a magic link to be emailed to the user.

## GET /auth/magic-link/verify
(Disabled by default) Verify a magic link token and create a session.

### Environment Variables
* `AUTH_GITHUB_CLIENT_ID`
* `AUTH_GITHUB_CLIENT_SECRET`
* `AUTH_COOKIE_NAME`
* `AUTH_COOKIE_DOMAIN`
* `AUTH_SIGNING_SECRET`
* `FF_AUTH_MAGIC_LINK`
