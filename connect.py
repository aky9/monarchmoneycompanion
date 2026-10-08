"""
Connect to Monarch (api.monarch.com) and verify the session works.

Uses the community-maintained `monarchmoneycommunity` library (pip install -r
requirements.txt). Credentials are read from environment variables:
    MONARCH_EMAIL        account email
    MONARCH_PASSWORD     account password
    MONARCH_MFA_SECRET   (optional) TOTP secret key, to skip the MFA prompt
    MONARCH_COOKIES      (optional) browser Cookie header, used if Monarch
                         blocks password login with a CAPTCHA

If the variables are missing you'll be prompted. After the first successful login
the session is saved to .mm/mm_session.pickle (gitignored) and reused.
Delete that file, or pass --fresh, to force a new login.
"""

import argparse
import asyncio
import getpass
import os

from monarchmoney import (
    CaptchaRequiredException,
    MonarchMoney,
    MonarchMoneyEndpoints,
    RequireMFAException,
)

SESSION_FILE = ".mm/mm_session.pickle"


async def connect(fresh: bool = False) -> MonarchMoney:
    mm = MonarchMoney(session_file=SESSION_FILE)

    if not fresh and os.path.exists(SESSION_FILE):
        mm.load_session(SESSION_FILE)
        return mm

    if os.environ.get("MONARCH_COOKIES"):
        await mm.login_with_cookies(os.environ["MONARCH_COOKIES"])
        return mm

    email = os.environ.get("MONARCH_EMAIL") or input("Email: ")
    password = os.environ.get("MONARCH_PASSWORD") or getpass.getpass("Password: ")
    mfa_secret = os.environ.get("MONARCH_MFA_SECRET")

    try:
        await mm.login(
            email,
            password,
            use_saved_session=False,
            save_session=True,
            mfa_secret_key=mfa_secret,
        )
    except CaptchaRequiredException:
        # Log in at app.monarch.com, then copy the request's Cookie header from
        # your browser's dev tools (Network tab). It must include session_id
        # and csrftoken.
        print("Monarch blocked password login with a CAPTCHA.")
        await mm.login_with_cookies(getpass.getpass("Browser Cookie header: "))
    except RequireMFAException:
        await mm.multi_factor_authenticate(email, password, input("MFA code: "))
        mm.save_session(SESSION_FILE)

    return mm


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--fresh", action="store_true", help="ignore any saved session")
    args = parser.parse_args()

    print(f"API endpoint: {MonarchMoneyEndpoints.getGraphQL()}")
    mm = await connect(fresh=args.fresh)

    # A cheap authenticated call to prove the connection works.
    accounts = (await mm.get_accounts()).get("accounts", [])
    print(f"Connected. {len(accounts)} accounts found:")
    for a in accounts:
        print(f"  {a['displayName']:<40} {a['currentBalance']:>14,.2f}")


if __name__ == "__main__":
    asyncio.run(main())
