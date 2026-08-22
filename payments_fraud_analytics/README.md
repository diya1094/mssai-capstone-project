# Part 1 — Payments & Fraud Analytics

Part 1 of the capstone. Parts 2 and 3 live in `/credit_risk_lending_ml` and
`/ai_advisory_blockchain` in this same repository. The committed CSVs are the
source of truth for the Excel, SQL, reconciliation and dashboard work.

## Structure

```text
payments_fraud_analytics/
├── generate_data.py
├── merchants.csv  users.csv  ledger.csv  gateway_export.csv
├── merchant_workbook.xlsx
├── paytm_payments.db        sql_fraud_queries.sql
├── reconcile.py             reconcile_result.md
├── dashboard.py
└── dashboard/  headline.png  trends.png  breakdown.png  details.png  interpretations.md
```

## Setup and run

Python 3.10+. One consolidated `requirements.txt` at the repository root covers
all three parts (`sqlite3` ships with Python).

```bash
pip install -r requirements.txt

cd payments_fraud_analytics    # scripts use relative paths
python generate_data.py        # seed 42 -> the four CSVs
python reconcile.py            # -> reconcile_result.md
python dashboard.py            # -> dashboard/*.png
```

Then open `merchant_workbook.xlsx`, `sql_fraud_queries.sql` (queries with their
output inline) and `paytm_payments.db`.

`generate_data.py` produces the 547-row ledger (500 baseline + 15 burner-account
chargebacks + 32 velocity rows) and a deliberately discrepant gateway export.

---

## Excel workbook

```excel
VLOOKUP  =IFERROR(VLOOKUP(C2,Merchants!$A$2:$D$41,2,FALSE),"Merchant not found")
HLOOKUP  =HLOOKUP(F2,HLOOKUP_Reference!$A$1:$E$2,2,FALSE)
Class.   =IF(AND(M2>5000,K2<>"East"),"High-Value Merchant Day","Normal Merchant Day")
```

- **VLOOKUP** uses an absolute range so it fills down safely.
- **HLOOKUP** is exact-match: the reference row holds four discrete payment-method
  names, not numeric tiers, so approximate match could return a wrong fee.
  Assumed MDR fees — UPI 0.20%, Wallet 0.65%, Card 1.50%, Netbanking 1.00%.
- **Classification** — both comparisons are strict: exactly INR 5,000 does not
  qualify, and an `East` merchant never qualifies. The daily total comes from
  `Daily_Merchant_Pivot`.
- **Count vs distinct count** — `transaction_date = INT(transaction_time)`, so
  three transactions on one day count as one unique day. Covers all 40 merchants.

## SQLite and SQL

Three normalised tables — `merchants(merchant_id PK)`, `users(user_id PK,
signup_date)`, `transactions(transaction_id PK, user_id FK, merchant_id FK)` —
with `PRAGMA foreign_keys = ON`. Loaded: 40 / 365 / 547 rows. Eight queries in
`sql_fraud_queries.sql`, each with its output inline.

| Requirement | Query |
| --- | --- |
| SELECT / WHERE / ORDER BY / LIMIT | 1 |
| DISTINCT | 2 |
| GROUP BY / HAVING | 3 |
| Chargeback impact | 4 |
| INNER JOIN | 5, 7 |
| LEFT JOIN | 6 |
| Burner accounts | 7 |
| Velocity attacks | 8 |

- **Chargeback impact** — 28 transactions, 27 unique users, INR 54,472.
- **Burner accounts** — boundary is explicitly
  `0 <= (transaction_time − signup_date).days < 30`, so signup is never after the
  transaction and exactly 30 days does not qualify. Surfaces **15 / 15** seeded rows.
- **Velocity attacks** — floored 10-minute buckets per user, `COUNT(*) >= 3`.
  Surfaces **8 / 8** seeded clusters. Graded on the presence of the seeded
  (user, cluster-start) pairs, since overlapping windows group several valid ways.

## Reconciliation

`reconcile_payments(ledger_df, gateway_df)` returns four DataFrames — set
operations on `transaction_id` for one-sided rows, an inner `pd.merge` for
field-level differences. Amount mismatches carry the difference (gateway − ledger).

| Discrepancy | Count | Rate |
| --- | ---: | ---: |
| Missing in gateway | 27 | 4.94% |
| Extra in gateway | 10 | 1.83% |
| Amount mismatches | 16 | 2.93% |
| Status mismatches | 9 | 1.65% |

Consistent with the injected ~5% / ~3% / ~2% / ~2% rates, allowing for integer
sampling and overlap between categories.

## Dashboard

Four PNGs in `dashboard/`, each carrying its own 2–4 sentence interpretation
inside the image; `interpretations.md` repeats them as text.

| Scorecard | Value | Definition |
| --- | --- | --- |
| Total GMV | INR 382,603 | Sum of `amount_inr` across all ledger transactions |
| Success rate | 85.56% | `count(captured) / count(all)` |
| Match rate | 90.49% | In both files with identical `amount_inr` **and** `status`, over all 547 ledger rows |
| Chargeback ratio | 5.12% | `count(chargeback) / count(all)` — count-based |

Missing rows, amount mismatches and status mismatches all count as *not* matched.

- **Trends** — daily GMV and daily chargeback count as two stacked panels sharing
  one x-axis, not a dual y-axis, so no relationship is implied between two
  unrelated scales.
- **Breakdown** — GMV by `payment_method` and by `category`, the latter joined
  from `merchants.csv` on `merchant_id`.
- **Details** — top 10 merchants by transaction count, saved as a table image.
  Per-merchant `chargeback_ratio = merchant chargebacks / that merchant's
  transactions`, flagged `HIGH RISK` strictly above 1%.

## Design decisions

- **GMV includes all transactions**, not only captured — INR 54,472 charged back
  and INR 37,749 failed are included. Success rate and chargeback ratio are
  separate scorecards, so outcome is not conflated with volume.
- **Both chargeback ratios are count-based**, headline and per-merchant, never
  amount-based.
- **Small denominators** — merchant ratios rest on 9–20 transactions over 30 days,
  so the flags are an analyst triage queue, not automated suspension decisions.