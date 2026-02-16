# LiveFlow Deman Gen Optimizer

Codex skill for generating and optimizing LiveFlow demand generation campaigns with disciplined weekly testing.

## What It Covers
- Persona- and industry-specific ABM email sequences
- Landing page copy variants
- LinkedIn ad copy variants
- Google Search ad copy variants
- Deterministic tracking ID generation for every variant
- Weekly performance logging and decisioning (`SCALE`, `ITERATE`, `PAUSE`)

## Core Files
- `SKILL.md`: skill workflow and operating rules
- `references/demand-gen-schema.md`: required fields and KPI definitions
- `scripts/generate_tracking_id.py`: variant tracking ID + UTM generator
- `scripts/log_weekly_results.py`: weekly upsert + leaderboard summary

## Quick Use
1. Build a weekly experiment matrix with one variable under test per cell.
2. Generate channel-specific copy variants.
3. Generate tracking IDs with `scripts/generate_tracking_id.py`.
4. Log weekly outcomes with `scripts/log_weekly_results.py upsert`.
5. Review decisions with `scripts/log_weekly_results.py summary`.

Invoke in Codex as: `$liveflow-deman-gen-optimizer`.
