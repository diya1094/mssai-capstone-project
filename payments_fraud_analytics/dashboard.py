from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# File Setup
BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "dashboard"
OUTPUT_DIR.mkdir(exist_ok=True)

ledger_df = pd.read_csv(BASE_DIR / "ledger.csv")
gateway_df = pd.read_csv(BASE_DIR / "gateway_export.csv")
merchants_df = pd.read_csv(BASE_DIR / "merchants.csv")

ledger_df["transaction_time"] = pd.to_datetime(ledger_df["transaction_time"])
gateway_df["transaction_time"] = pd.to_datetime(gateway_df["transaction_time"])
ledger_df["transaction_date"] = ledger_df["transaction_time"].dt.normalize()


total_gmv = ledger_df["amount_inr"].sum()
total_transactions = len(ledger_df)
successful_transactions = (ledger_df["status"] == "captured").sum()
success_rate = (successful_transactions / total_transactions) * 100

common_transactions = pd.merge(
    ledger_df[["transaction_id", "amount_inr", "status"]],
    gateway_df[["transaction_id", "amount_inr", "status"]],
    on="transaction_id",
    how="inner",
    suffixes=("_ledger", "_gateway"),
)

exact_matches = (
    (common_transactions["amount_inr_ledger"] == common_transactions["amount_inr_gateway"])
    & (common_transactions["status_ledger"] == common_transactions["status_gateway"])
).sum()

match_rate = (exact_matches / total_transactions) * 100
chargeback_transactions = (ledger_df["status"] == "chargeback").sum()
chargeback_ratio = (chargeback_transactions / total_transactions) * 100

headline_interpretation = (
    f"Total GMV across the 30-day ledger is INR {total_gmv:,.0f} across {total_transactions:,} transactions. "
    f"The overall success rate is {success_rate:.2f}%, while the reconciliation match rate is {match_rate:.2f}% "
    f"because a transaction must exist in both files with identical amount and status. "
    f"The platform-wide chargeback ratio is {chargeback_ratio:.2f}% based on transaction count."
)

fig, ax = plt.subplots(figsize=(16, 8))
ax.axis("off")

headline_metrics = [
    ("TOTAL GMV", f"INR {total_gmv:,.0f}"),
    ("SUCCESS RATE", f"{success_rate:.2f}%"),
    ("RECONCILIATION MATCH RATE", f"{match_rate:.2f}%"),
    ("CHARGEBACK RATIO", f"{chargeback_ratio:.2f}%"),
]

for x, (label, value) in zip([0.125, 0.375, 0.625, 0.875], headline_metrics):
    ax.text(x, 0.76, value, ha="center", va="center", fontsize=25, fontweight="bold")
    ax.text(x, 0.61, label, ha="center", va="center", fontsize=11)

ax.text(0.02, 0.13, "Interpretation: " + headline_interpretation, ha="left", va="bottom", fontsize=10.5, wrap=True)
ax.set_title("Paytm Payments — Headline Scorecards", loc="left", fontsize=18, fontweight="bold", pad=18)
fig.tight_layout()
fig.savefig(OUTPUT_DIR / "headline.png", dpi=200, bbox_inches="tight")
plt.close(fig)


daily_metrics = (
    ledger_df.groupby("transaction_date")
    .agg(
        daily_gmv=("amount_inr", "sum"),
        daily_chargebacks=("status", lambda x: (x == "chargeback").sum()),
    )
    .reset_index()
)

peak_gmv = daily_metrics.loc[daily_metrics["daily_gmv"].idxmax()]
peak_cb = daily_metrics.loc[daily_metrics["daily_chargebacks"].idxmax()]

trends_interpretation = (
    f"Daily GMV peaks at INR {peak_gmv['daily_gmv']:,.0f} on {peak_gmv['transaction_date'].strftime('%d %b %Y')}. "
    f"Chargeback activity shows spikes, with a maximum daily count of {int(peak_cb['daily_chargebacks'])} "
    f"recorded on {peak_cb['transaction_date'].strftime('%d %b %Y')}. High-chargeback dates should be prioritized for fraud investigation."
)

fig, (ax_gmv, ax_chargebacks) = plt.subplots(
    2, 1, figsize=(16, 10), sharex=True, gridspec_kw={"height_ratios": [2.3, 1]}
)

ax_gmv.plot(daily_metrics["transaction_date"], daily_metrics["daily_gmv"], marker="o", linewidth=1.8)
ax_gmv.set_ylabel("Daily GMV (INR)")
ax_gmv.set_title("Daily GMV", loc="left", fontsize=13, fontweight="bold")
ax_gmv.grid(axis="y", alpha=0.25)

ax_chargebacks.bar(daily_metrics["transaction_date"], daily_metrics["daily_chargebacks"], width=0.7)
ax_chargebacks.set_ylabel("Chargeback Count")
ax_chargebacks.set_xlabel("Transaction Date")
ax_chargebacks.set_title("Daily Chargeback Count", loc="left", fontsize=13, fontweight="bold")
ax_chargebacks.grid(axis="y", alpha=0.25)
ax_chargebacks.tick_params(axis="x", rotation=45)

fig.suptitle("Paytm Payments — Trends Layer", x=0.02, ha="left", fontsize=18, fontweight="bold")
fig.text(0.02, 0.015, "Interpretation: " + trends_interpretation, ha="left", va="bottom", fontsize=10.5, wrap=True)
fig.tight_layout(rect=[0, 0.08, 1, 0.94])
fig.savefig(OUTPUT_DIR / "trends.png", dpi=200, bbox_inches="tight")
plt.close(fig)


payment_method_gmv = ledger_df.groupby("payment_method", as_index=False)["amount_inr"].sum().sort_values("amount_inr", ascending=False)

category_transactions = ledger_df.merge(merchants_df[["merchant_id", "category"]], on="merchant_id", how="left", validate="many_to_one")
category_gmv = category_transactions.groupby("category", as_index=False)["amount_inr"].sum().sort_values("amount_inr", ascending=False)

top_pm = payment_method_gmv.iloc[0]
top_cat = category_gmv.iloc[0]

breakdown_interpretation = (
    f"{top_pm['payment_method']} leads payment methods with INR {top_pm['amount_inr']:,.0f} in GMV. "
    f"Among categories, {top_cat['category']} leads at INR {top_cat['amount_inr']:,.0f}. "
    f"This breakdown maps transaction value concentration across payment types and merchant segments."
)

fig, (ax_payment, ax_category) = plt.subplots(1, 2, figsize=(16, 7))

ax_payment.barh(payment_method_gmv["payment_method"][::-1], payment_method_gmv["amount_inr"][::-1])
ax_payment.set_title("GMV by Payment Method", fontsize=13, fontweight="bold")
ax_payment.set_xlabel("GMV (INR)")

ax_category.barh(category_gmv["category"][::-1], category_gmv["amount_inr"][::-1])
ax_category.set_title("GMV by Merchant Category", fontsize=13, fontweight="bold")
ax_category.set_xlabel("GMV (INR)")

fig.suptitle("Paytm Payments — Breakdown Layer", x=0.02, ha="left", fontsize=18, fontweight="bold")
fig.text(0.02, 0.015, "Interpretation: " + breakdown_interpretation, ha="left", va="bottom", fontsize=10.5, wrap=True)
fig.tight_layout(rect=[0, 0.08, 1, 0.94])
fig.savefig(OUTPUT_DIR / "breakdown.png", dpi=200, bbox_inches="tight")
plt.close(fig)


merchant_stats = (
    ledger_df.groupby("merchant_id")
    .agg(
        transaction_count=("transaction_id", "count"),
        gmv=("amount_inr", "sum"),
        chargeback_count=("status", lambda x: (x == "chargeback").sum()),
    )
    .reset_index()
)

merchant_stats["chargeback_ratio"] = (merchant_stats["chargeback_count"] / merchant_stats["transaction_count"]) * 100
merchant_stats = merchant_stats.merge(merchants_df[["merchant_id", "merchant_name", "category", "region"]], on="merchant_id", how="left", validate="one_to_one")
merchant_stats["flag"] = merchant_stats["chargeback_ratio"].apply(lambda v: "HIGH RISK" if v > 1 else "OK")

top_10_merchants = merchant_stats.sort_values(["transaction_count", "merchant_id"], ascending=[False, True]).head(10).copy()
flagged_merchants = (top_10_merchants["flag"] == "HIGH RISK").sum()

details_interpretation = (
    f"The table lists the top 10 merchants by volume and evaluates chargeback ratios. "
    f"{flagged_merchants} of these top merchants exceed the 1% threshold, receiving a HIGH RISK flag for operational review."
)

details_table = top_10_merchants[["merchant_name", "category", "region", "transaction_count", "gmv", "chargeback_count", "chargeback_ratio", "flag"]].copy()
details_table["gmv"] = details_table["gmv"].map(lambda v: f"{v:,.0f}")
details_table["chargeback_ratio"] = details_table["chargeback_ratio"].map(lambda v: f"{v:.2f}%")

fig, ax = plt.subplots(figsize=(16, 8))
ax.axis("off")

table = ax.table(
    cellText=details_table.values,
    colLabels=["Merchant", "Category", "Region", "Txns", "GMV (INR)", "Chargebacks", "CB Ratio", "Flag"],
    cellLoc="center",
    loc="center",
)
table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1, 1.8)

for row_idx, flag in enumerate(details_table["flag"], start=1):
    if flag == "HIGH RISK":
        for col_idx in range(len(details_table.columns)):
            table[(row_idx, col_idx)].get_text().set_weight("bold")

ax.set_title("Paytm Payments — Details Layer: Top 10 Merchants", loc="left", fontsize=18, fontweight="bold", pad=18)
fig.text(0.02, 0.015, "Interpretation: " + details_interpretation, ha="left", va="bottom", fontsize=10.5, wrap=True)
fig.tight_layout(rect=[0, 0.08, 1, 0.94])
fig.savefig(OUTPUT_DIR / "details.png", dpi=200, bbox_inches="tight")
plt.close(fig)

interpretations = f"""# Paytm Payments — Dashboard Interpretations
## Headline\n{headline_interpretation}
## Trends\n{trends_interpretation}
## Breakdown\n{breakdown_interpretation}
## Details\n{details_interpretation}
"""
(OUTPUT_DIR / "interpretations.md").write_text(interpretations.strip(), encoding="utf-8")