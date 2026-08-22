from pathlib import Path
import pandas as pd


def reconcile_payments(ledger_df: pd.DataFrame, gateway_df: pd.DataFrame):
    """Reconcile ledger transactions against the gateway export."""
    merged = pd.merge(
        ledger_df,
        gateway_df,
        on="transaction_id",
        how="outer",
        indicator=True,
        suffixes=("_ledger", "_gateway"),
    )

    missing_in_gateway = (
        merged[merged["_merge"] == "left_only"]
        .drop(columns=["_merge"])
        .sort_values("transaction_id")
        .reset_index(drop=True)
    )
    missing_in_ledger = (
        merged[merged["_merge"] == "right_only"]
        .drop(columns=["_merge"])
        .sort_values("transaction_id")
        .reset_index(drop=True)
    )

    common = merged[merged["_merge"] == "both"]

    amt_diff = common["amount_inr_gateway"] != common["amount_inr_ledger"]
    amount_mismatches = common.loc[
        amt_diff, ["transaction_id", "amount_inr_ledger", "amount_inr_gateway"]
    ].copy()
    amount_mismatches["amount_difference_inr"] = (
        amount_mismatches["amount_inr_gateway"]
        - amount_mismatches["amount_inr_ledger"]
    )
    amount_mismatches = amount_mismatches.sort_values(
        "transaction_id"
    ).reset_index(drop=True)

    status_diff = common["status_ledger"] != common["status_gateway"]
    status_mismatches = (
        common.loc[
            status_diff, ["transaction_id", "status_ledger", "status_gateway"]
        ]
        .sort_values("transaction_id")
        .reset_index(drop=True)
    )

    return (
        missing_in_gateway,
        missing_in_ledger,
        amount_mismatches,
        status_mismatches,
    )

if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent
    ledger_df = pd.read_csv(base_dir / "ledger.csv")
    gateway_df = pd.read_csv(base_dir / "gateway_export.csv")

    results = reconcile_payments(ledger_df, gateway_df)
    missing_gw, missing_ldg, amt_mismatch, status_mismatch = results

    print("Payment Reconciliation Results")
    print("=" * 35)
    print(f"Ledger transactions:             {len(ledger_df)}")
    print(f"Gateway transactions:            {len(gateway_df)}")
    print(f"Missing in gateway:              {len(missing_gw)}")
    print(f"Missing in ledger / extra gateway: {len(missing_ldg)}")
    print(f"Amount mismatches:               {len(amt_mismatch)}")
    print(f"Status mismatches:               {len(status_mismatch)}")