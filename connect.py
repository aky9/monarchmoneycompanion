"""
Connect to Monarch (api.monarch.com) and verify the session works.

Credentials are read from environment variables so nothing sensitive lives in code:
    MONARCH_EMAIL        account email
    MONARCH_PASSWORD     account password
    MONARCH_MFA_SECRET   (optional) TOTP secret key, to skip the MFA prompt

If the variables are missing you'll be prompted. After the first successful login
the session token is saved to .mm/mm_session.pickle (gitignored) and reused.
Delete that file, or pass --fresh, to force a new login.
"""

import argparse
import asyncio
import getpass
import os

from monarchmoney import MonarchMoney, RequireMFAException
from monarchmoney.monarchmoney import MonarchMoneyEndpoints

SESSION_FILE = ".mm/mm_session.pickle"


async def connect(fresh: bool = False) -> MonarchMoney:
    mm = MonarchMoney(session_file=SESSION_FILE)

    if not fresh and os.path.exists(SESSION_FILE):
        mm.load_session(SESSION_FILE)
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
