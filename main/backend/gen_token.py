#!/usr/bin/env python3
"""
CC Platform - Admin Token Generator
===================================
Generates the daily token using HMAC-SHA256.
Token rotates every 24 hours. Valid for ±1 day.

Usage:
  python gen_token.py                          # today's token
  python gen_token.py --secret <your-secret>   # custom secret
  python gen_token.py --window 2               # show today + tomorrow
"""

import argparse
import hmac
import hashlib
import base64
import time

DEFAULT_SECRET = "cc-platform-default-secret"
DAY_SECONDS = 24 * 60 * 60  # 1 day in seconds


def compute_token(secret: str, day_window: int) -> str:
    """Compute HMAC-SHA256 token for a day window."""
    mac = hmac.new(
        secret.encode("utf-8"),
        str(day_window).encode("utf-8"),
        hashlib.sha256,
    )
    return base64.urlsafe_b64encode(mac.digest()).rstrip(b"=").decode("ascii")


def main():
    parser = argparse.ArgumentParser(
        description="CC Platform daily token generator (HMAC-SHA256)"
    )
    parser.add_argument(
        "--secret", "-s",
        default=DEFAULT_SECRET,
        help=f"Shared secret key (default: {DEFAULT_SECRET})",
    )
    parser.add_argument(
        "--window", "-w",
        type=int,
        default=1,
        help="Number of future day windows to show (default: 1 = today only)",
    )
    args = parser.parse_args()

    today_window = int(time.time()) // DAY_SECONDS

    print(f"Secret:  {args.secret}")
    print(f"Window:  1 day")
    print(f"Current: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)

    for i in range(args.window):
        w = today_window + i
        token = compute_token(args.secret, w)
        expires = time.strftime(
            "%Y-%m-%d %H:%M:%S",
            time.localtime((w + 1) * DAY_SECONDS),
        )
        label = ">>> TODAY    " if i == 0 else f"   +{i} day     "
        print(f"  {label} | day_window={w} | expires ~{expires}")
        print(f"  Token: {token}")
        print()

    token = compute_token(args.secret, today_window)
    print("-" * 50)
    print("Login (POST JSON body):")
    print(f'  curl -X POST "http://localhost:5070/login" \\')
    print(f'    -H "Content-Type: application/json" \\')
    print(f'    -d \'{{"username":"root","password":"root"}}\'')
    print()
    print("Data request (Authorization header):")
    print(f'  curl -H "Authorization: {token}" "http://localhost:5070/data?target=field"')
    print(f'  curl -H "Authorization: {token}" "http://localhost:5070/data?target=news"')


if __name__ == "__main__":
    main()
