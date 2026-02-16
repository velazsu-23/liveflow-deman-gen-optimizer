# Demand Gen Schema

Use this schema for weekly planning and performance logs across ABM and paid channels.

## Planning Fields
- `campaign_name`: short slug, for example `q2-multi-entity-pilot`
- `week`: ISO week, for example `2026-W08`
- `persona`: `CFO` | `Controller` | `Head of Finance` | `VP Finance`
- `industry`: one ICP slice per primary test wave
- `channel`: `abm-email` | `landing-page` | `linkedin-ad` | `google-search-ad`
- `pain_theme`: `consolidation-pain` | `ai-first-erp` | `scale-without-headcount`
- `angle`: positioning angle slug
- `offer`: offer slug
- `variant`: variant label, for example `A`, `B`, `C1`
- `variable_under_test`: one variable only per cell

## Generated Artifacts by Channel
- `abm-email`: 4 email steps with subject + body
- `landing-page`: hero, subheadline, proof, CTA, objection handling
- `linkedin-ad`: intro line, primary text, headline, description, CTA
- `google-search-ad`: headlines, descriptions, path fields

## Weekly Log Fields (All Channels)
- `week`
- `tracking_id`
- `persona`
- `industry`
- `channel`
- `angle`
- `offer`
- `variant`
- `opps`
- `pipeline_usd`
- `wins`
- `spend_usd`

## Weekly Log Fields (ABM/Landing)
- `accounts_targeted`
- `replies`
- `meetings`

## Weekly Log Fields (LinkedIn/Google Search)
- `impressions`
- `clicks`
- `sqls`

## Derived KPI Definitions
- `reply_rate = replies / accounts_targeted`
- `meeting_rate = meetings / accounts_targeted`
- `opps_per_100_accounts = (opps / accounts_targeted) * 100`
- `pipeline_per_100_accounts = (pipeline_usd / accounts_targeted) * 100`
- `ctr = clicks / impressions`
- `sql_rate = sqls / clicks`
- `cost_per_sql = spend_usd / sqls`
- `cpc = spend_usd / clicks`
- `cost_per_opp = spend_usd / opps`

## Decision Policy
### ABM / landing
- `SCALE`: `opps_per_100_accounts >= 10` and `meeting_rate >= 0.05`
- `PAUSE`: `opps_per_100_accounts < 4` or `meeting_rate < 0.02`
- `ITERATE`: otherwise

### LinkedIn / Google Search
- `SCALE`: `sql_rate >= 0.04`, `cost_per_sql <= 900`, and `opps >= 2`
- `PAUSE`: `sql_rate < 0.015` or (`cost_per_sql > 1800` and `sqls >= 3`)
- `ITERATE`: otherwise

## Governance Rules
- Keep one control variant per persona and industry cell.
- Change one variable per test cell.
- Keep budgets and audience settings stable while testing copy.
- Run weekly variant-level readouts.
- Scale only after 2 to 3 stable weeks.
