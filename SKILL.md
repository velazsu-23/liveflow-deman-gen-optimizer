---
name: liveflow-deman-gen-optimizer
description: Generate and optimize LiveFlow demand generation variants by persona and industry across ABM email, landing pages, LinkedIn ads, and Google Search ads. Use when Codex needs disciplined experimentation with tracking IDs, weekly performance logging, and explicit scale/iterate/pause decisions from pipeline and efficiency metrics.
---

# LiveFlow Deman Gen Optimizer

Run a disciplined demand gen experimentation loop for LiveFlow. Generate ABM and ad variants, assign deterministic tracking IDs, and optimize weekly with channel-specific decision gates.

## Quick Start
1. Collect inputs with `references/demand-gen-schema.md`.
2. Build one weekly matrix with one variable changed per test cell.
3. Generate copy assets for ABM and ad channels.
4. Assign one tracking ID per variant using `scripts/generate_tracking_id.py`.
5. Log weekly results using `scripts/log_weekly_results.py`.
6. Apply decision gates and propose next-week actions.

## Step 1: Build Weekly Experiment Matrix
Define:
- `persona`: CFO, Controller, Head of Finance, VP Finance
- `industry`: one validated ICP slice at a time
- `pain_theme`: consolidation pain, AI-first ERP, scale without headcount
- `offer`: demo, ROI one-pager, readiness assessment, comparison guide
- `channel`: `abm-email` | `landing-page` | `linkedin-ad` | `google-search-ad`
- `variable_under_test`: exactly one variable per cell

Keep all non-tested variables fixed.

## Step 2: Generate Channel Variants
For each test cell, produce the matching output blocks.

```markdown
## Variant: <variant_name>
- Persona: <persona>
- Industry: <industry>
- Pain theme: <pain_theme>
- Offer: <offer>
- Channel: <channel>
- Variable under test: <variable_under_test>

### ABM Email Sequence (for `abm-email`)
1. Subject:
   Body:
2. Subject:
   Body:
3. Subject:
   Body:
4. Subject:
   Body:

### Landing Page Copy Blocks (for `landing-page`)
- Hero headline:
- Subheadline:
- Proof block:
- CTA:
- Objection handling block:

### LinkedIn Ad Copy (for `linkedin-ad`)
- Intro line:
- Primary text:
- Headline:
- Description:
- CTA:

### Google Search Ad Copy (for `google-search-ad`)
- Headlines (8 to 15, each <= 30 chars):
- Descriptions (2 to 4, each <= 90 chars):
- Path fields:
```

Keep copy concise, finance-buyer specific, and outcome-led.

## Step 3: Assign Tracking IDs
Generate one ID per channel variant:

```bash
python3 scripts/generate_tracking_id.py \
  --campaign-name "q2-multi-entity-pilot" \
  --persona "CFO" \
  --industry "SaaS" \
  --channel "linkedin-ad" \
  --angle "close-faster" \
  --offer "roi-one-pager" \
  --variant "A" \
  --week "2026-W08"
```

Reuse the same ID in ad naming, UTM content, landing links, and weekly logs.

## Step 4: Log Weekly Results
### ABM or landing variants
```bash
python3 scripts/log_weekly_results.py upsert \
  --csv-path results/demand_gen_weekly_results.csv \
  --week 2026-W08 \
  --tracking-id LFABM-EXAMPLE \
  --persona CFO \
  --industry SaaS \
  --channel abm-email \
  --angle close-faster \
  --offer roi-one-pager \
  --variant A \
  --accounts-targeted 100 \
  --replies 9 \
  --meetings 6 \
  --opps 10 \
  --pipeline-usd 240000 \
  --wins 2 \
  --spend-usd 3800
```

### LinkedIn or Google Search variants
```bash
python3 scripts/log_weekly_results.py upsert \
  --csv-path results/demand_gen_weekly_results.csv \
  --week 2026-W08 \
  --tracking-id LFABM-EXAMPLE \
  --persona CFO \
  --industry SaaS \
  --channel google-search-ad \
  --angle close-faster \
  --offer roi-one-pager \
  --variant A \
  --impressions 12000 \
  --clicks 420 \
  --sqls 19 \
  --opps 5 \
  --pipeline-usd 130000 \
  --wins 1 \
  --spend-usd 7600
```

Generate weekly leaderboard:

```bash
python3 scripts/log_weekly_results.py summary \
  --csv-path results/demand_gen_weekly_results.csv \
  --week 2026-W08
```

## Step 5: Enforce Optimization Gates
### ABM / landing channels
- `SCALE`: `opps_per_100_accounts >= 10` and `meeting_rate >= 0.05`
- `PAUSE`: `opps_per_100_accounts < 4` or `meeting_rate < 0.02`
- `ITERATE`: otherwise

### LinkedIn / Google Search channels
- `SCALE`: `sql_rate >= 0.04`, `cost_per_sql <= 900`, and `opps >= 2`
- `PAUSE`: `sql_rate < 0.015` or (`cost_per_sql > 1800` and `sqls >= 3`)
- `ITERATE`: otherwise

Scale only after 2 to 3 stable weeks in quality and efficiency.

## Output Requirements
Always return:
1. Weekly experiment matrix with control values.
2. Variant copy for each requested channel.
3. Tracking ID map.
4. Weekly scorecard with KPIs and decision labels.
5. Next-week actions with rationale (scale, iterate, pause).

## Resources
- `references/demand-gen-schema.md`: planning and KPI schema for ABM + ad channels.
- `scripts/generate_tracking_id.py`: deterministic tracking ID generator.
- `scripts/log_weekly_results.py`: weekly logging and decision summary.

If required data is missing, make one explicit assumption and continue.
