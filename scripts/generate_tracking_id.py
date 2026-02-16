#!/usr/bin/env python3
"""Generate deterministic tracking IDs for LiveFlow ABM variants."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import date


def iso_week_today() -> str:
    year, week, _ = date.today().isocalendar()
    return f"{year}-W{week:02d}"


def slugify(value: str, max_len: int = 18) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return (cleaned[:max_len]).strip("-") or "na"


def build_tracking_id(
    campaign_name: str,
    persona: str,
    industry: str,
    channel: str,
    angle: str,
    offer: str,
    variant: str,
    week: str,
) -> tuple[str, str]:
    canonical = "|".join(
        [
            slugify(campaign_name, 32),
            week,
            slugify(persona, 20),
            slugify(industry, 20),
            slugify(channel, 20),
            slugify(angle, 24),
            slugify(offer, 24),
            slugify(variant, 8),
        ]
    )
    digest = hashlib.sha1(canonical.encode("utf-8")).hexdigest()[:8]
    tracking_id = (
        f"LFABM-{week.replace('-', '')}-"
        f"{slugify(persona, 6)}-"
        f"{slugify(industry, 6)}-"
        f"{slugify(channel, 5)}-"
        f"{slugify(variant, 4)}-{digest}"
    ).upper()
    return tracking_id, canonical


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign-name", required=True)
    parser.add_argument("--persona", required=True)
    parser.add_argument("--industry", required=True)
    parser.add_argument(
        "--channel",
        required=True,
        choices=["abm-email", "landing-page", "linkedin-ad", "google-search-ad"],
    )
    parser.add_argument("--angle", required=True)
    parser.add_argument("--offer", required=True)
    parser.add_argument("--variant", required=True)
    parser.add_argument("--week", default=iso_week_today())
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    tracking_id, canonical = build_tracking_id(
        campaign_name=args.campaign_name,
        persona=args.persona,
        industry=args.industry,
        channel=args.channel,
        angle=args.angle,
        offer=args.offer,
        variant=args.variant,
        week=args.week,
    )

    payload = {
        "tracking_id": tracking_id,
        "canonical_key": canonical,
        "week": args.week,
        "utm": {
            "utm_source": "abm",
            "utm_medium": args.channel,
            "utm_campaign": slugify(args.campaign_name, 32),
            "utm_content": tracking_id.lower(),
        },
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
