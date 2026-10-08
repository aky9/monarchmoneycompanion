# Monarch Money Companion

Scripts for working with your [Monarch](https://www.monarch.com) data from Python.

The API client is the community-maintained
[`monarchmoneycommunity`](https://github.com/bradleyseanf/monarchmoneycommunity)
library ([PyPI](https://pypi.org/project/monarchmoneycommunity/)), a maintained fork
of the original `hammem/monarchmoney`, which is no longer updated. It talks to
Monarch's current API at `api.monarch.com`. See its README for the full list of
available methods.

Note: Monarch has no official public API. These libraries use the same private API
as Monarch's web app, which can change without notice. When something breaks,
first upgrade the library: `pip install -U monarchmoneycommunity`.

## Setup

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## Connect

```bash
export MONARCH_EMAIL=you@example.com
export MONARCH_PASSWORD=...
# optional: export MONARCH_MFA_SECRET=...   (TOTP setup key, skips the MFA prompt)
python connect.py
```

This logs in, saves the session to `.mm/mm_session.pickle` (gitignored), and lists
your accounts. Later runs reuse the saved session; pass `--fresh` to log in again.

If you sign in to Monarch with Google, set a password first in your
[security settings](https://app.monarch.com/settings/security).

If Monarch blocks password login with a CAPTCHA, the script asks for your browser's
Cookie header instead. Log in at app.monarch.com, open dev tools → Network, copy the
`Cookie` request header from any request to `api.monarch.com`, and paste it in. It
must include `session_id` and `csrftoken`. You can also set it as `MONARCH_COOKIES`.

## Other scripts

- `main.py`: example that pulls accounts, budgets, transactions and cash flow
  into JSON files.
