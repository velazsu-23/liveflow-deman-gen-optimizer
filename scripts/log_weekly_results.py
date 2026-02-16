#!/usr/bin/env python3
"""Upsert weekly demand gen results and print a decision summary."""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path
from typing import Dict, List


ABM_CHANNELS = {"abm-email", "landing-page"}
AD_CHANNELS = {"linkedin-ad", "google-search-ad"}


FIELDNAMES = [
    "week",
    "tracking_id",
    "persona",
    "industry",
    "channel",
    "angle",
    "offer",
    "variant",
    "accounts_targeted",
    "replies",
    "meetings",
    "impressions",
    "clicks",
    "sqls",
    "opps",
    "pipeline_usd",
    "wins",
    "spend_usd",
    "reply_rate",
    "meeting_rate",
    "opps_per_100_accounts",
    "pipeline_per_100_accounts",
    "ctr",
    "sql_rate",
    "cpc",
    "cost_per_sql",
    "cost_per_opp",
    "decision",
]


def safe_rate(num: float, den: float) -> float:
    return 0.0 if den <= 0 else num / den


def to_float(value: str) -> float:
    try:
        return float(value)
    except Exception:
        return 0.0


def format_float(value: float, digits: int = 4) -> str:
    if math.isnan(value) or math.isinf(value):
        return "0"
    return f"{value:.{digits}f}"


def decide(channel: str, opps_per_100: float, meeting_rate: float, sql_rate: float, cost_per_sql: float, opps: float, sqls: float) -> str:
    if channel in ABM_CHANNELS:
        if opps_per_100 >= 10.0 and meeting_rate >= 0.05:
            return "SCALE"
        if opps_per_100 < 4.0 or meeting_rate < 0.02:
            return "PAUSE"
        return "ITERATE"

    if channel in AD_CHANNELS:
        if sql_rate >= 0.04 and cost_per_sql > 0 and cost_per_sql <= 900.0 and opps >= 2.0:
            return "SCALE"
        if sql_rate < 0.015 or (cost_per_sql > 1800.0 and sqls >= 3.0):
            return "PAUSE"
        return "ITERATE"

    return "ITERATE"


def read_rows(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        return list(reader)


def write_rows(path: Path, rows: List[Dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def parse_common_fields(args: argparse.Namespace) -> Dict[str, str]:
    accounts = float(args.accounts_targeted)
    replies = float(args.replies)
    meetings = float(args.meetings)
    impressions = float(args.impressions)
    clicks = float(args.clicks)
    sqls = float(args.sqls)
    opps = float(args.opps)
    pipeline = float(args.pipeline_usd)
    spend = float(args.spend_usd)

    reply_rate = safe_rate(replies, accounts)
    meeting_rate = safe_rate(meetings, accounts)
    opps_per_100 = safe_rate(opps, accounts) * 100.0
    pipeline_per_100 = safe_rate(pipeline, accounts) * 100.0
    ctr = safe_rate(clicks, impressions)
    sql_rate = safe_rate(sqls, clicks)
    cpc = safe_rate(spend, clicks)
    cost_per_sql = safe_rate(spend, sqls)
    cost_per_opp = safe_rate(spend, opps)
    decision = decide(args.channel, opps_per_100, meeting_rate, sql_rate, cost_per_sql, opps, sqls)

    return {
        "week": args.week,
        "tracking_id": args.tracking_id,
        "persona": args.persona,
        "industry": args.industry,
        "channel": args.channel,
        "angle": args.angle,
        "offer": args.offer,
        "variant": args.variant,
        "accounts_targeted": str(int(accounts)),
        "replies": str(int(replies)),
        "meetings": str(int(meetings)),
        "impressions": str(int(impressions)),
        "clicks": str(int(clicks)),
        "sqls": str(int(sqls)),
        "opps": str(int(opps)),
        "pipeline_usd": format_float(pipeline, 2),
        "wins": str(int(args.wins)),
        "spend_usd": format_float(spend, 2),
        "reply_rate": format_float(reply_rate),
        "meeting_rate": format_float(meeting_rate),
        "opps_per_100_accounts": format_float(opps_per_100, 2),
        "pipeline_per_100_accounts": format_float(pipeline_per_100, 2),
        "ctr": format_float(ctr),
        "sql_rate": format_float(sql_rate),
        "cpc": format_float(cpc, 2),
        "cost_per_sql": format_float(cost_per_sql, 2),
        "cost_per_opp": format_float(cost_per_opp, 2),
        "decision": decision,
    }


def command_upsert(args: argparse.Namespace) -> int:
    path = Path(args.csv_path)
    rows = read_rows(path)
    record = parse_common_fields(args)

    key = (record["week"], record["tracking_id"])
    replaced = False
    for idx, row in enumerate(rows):
        if (row.get("week", ""), row.get("tracking_id", "")) == key:
            rows[idx] = record
            replaced = True
            break
    if not replaced:
        rows.append(record)

    rows.sort(key=lambda r: (r["week"], r["tracking_id"]))
    write_rows(path, rows)

    action = "updated" if replaced else "inserted"
    print(f"{action}: week={record['week']} tracking_id={record['tracking_id']} decision={record['decision']}")
    return 0


def command_summary(args: argparse.Namespace) -> int:
    path = Path(args.csv_path)
    rows = read_rows(path)
    if args.week:
        rows = [r for r in rows if r.get("week") == args.week]

    if not rows:
        print("no rows found")
        return 0

    decision_rank = {"SCALE": 0, "ITERATE": 1, "PAUSE": 2}
    rows.sort(
        key=lambda r: (
            decision_rank.get(r.get("decision", "ITERATE"), 3),
            -to_float(r.get("pipeline_usd", "0")),
            -to_float(r.get("sql_rate", "0")),
            -to_float(r.get("meeting_rate", "0")),
        )
    )

    print("week,tracking_id,channel,persona,industry,variant,opps,pipeline_usd,meeting_rate,sql_rate,ctr,cost_per_sql,decision")
    for r in rows:
        print(
            ",".join(
                [
                    r.get("week", ""),
                    r.get("tracking_id", ""),
                    r.get("channel", ""),
                    r.get("persona", ""),
                    r.get("industry", ""),
                    r.get("variant", ""),
                    r.get("opps", ""),
                    r.get("pipeline_usd", ""),
                    r.get("meeting_rate", ""),
                    r.get("sql_rate", ""),
                    r.get("ctr", ""),
                    r.get("cost_per_sql", ""),
                    r.get("decision", ""),
                ]
            )
        )
    return 0


def add_common_metric_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--week", required=True)
    parser.add_argument("--tracking-id", required=True)
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

    parser.add_argument("--accounts-targeted", default=0, type=float)
    parser.add_argument("--replies", default=0, type=float)
    parser.add_argument("--meetings", default=0, type=float)
    parser.add_argument("--impressions", default=0, type=float)
    parser.add_argument("--clicks", default=0, type=float)
    parser.add_argument("--sqls", default=0, type=float)

    parser.add_argument("--opps", required=True, type=float)
    parser.add_argument("--pipeline-usd", required=True, type=float)
    parser.add_argument("--wins", required=True, type=float)
    parser.add_argument("--spend-usd", required=True, type=float)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    upsert = subparsers.add_parser("upsert", help="Insert or update one weekly variant row")
    upsert.add_argument("--csv-path", default="results/demand_gen_weekly_results.csv")
    add_common_metric_args(upsert)
    upsert.set_defaults(func=command_upsert)

    summary = subparsers.add_parser("summary", help="Print weekly leaderboard")
    summary.add_argument("--csv-path", default="results/demand_gen_weekly_results.csv")
    summary.add_argument("--week", help="Optional ISO week filter, for example 2026-W08")
    summary.set_defaults(func=command_summary)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
