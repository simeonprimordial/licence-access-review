
import pandas as pd
from datetime import datetime, timezone

from src.data_loader import load_all_data


def run_licence_audit(
    users,
    licences,
    inactive_days=90,
    as_of=None
):
    """
    Audit SaaS licences for inactivity and unassigned seats.

    Returns a DataFrame containing review findings.
    """

    if as_of is None:
        as_of = datetime.now(timezone.utc)

    as_of = pd.Timestamp(as_of)

    if as_of.tzinfo is not None:
        as_of = as_of.tz_localize(None)

    users = users.copy()
    licences = licences.copy()

    users["last_login"] = pd.to_datetime(
        users["last_login"], errors="raise"
    )

    # Join licence records with user records.
    audit_data = licences.merge(
        users,
        on="user_id",
        how="left",
        indicator=True
    )

    findings = []

    for _, row in audit_data.iterrows():

        finding = None
        severity = "None"
        recommendation = "No action required"
        potential_monthly_saving = 0.0

        # Case 1: Unassigned licence.
        if pd.isna(row["user_id"]):
            finding = "Unassigned licence"
            severity = "Medium"
            recommendation = "Review whether this seat is still required"
            potential_monthly_saving = row["cost_monthly"]

        # Case 2: Licence assigned to a missing user.
        elif row["_merge"] == "left_only":
            finding = "Unknown user"
            severity = "High"
            recommendation = "Investigate the orphaned licence assignment"
            potential_monthly_saving = row["cost_monthly"]

        # Case 3: Licence assigned to disabled account.
        elif str(row["status"]).strip().lower() != "active":
            finding = "Licence assigned to inactive account"
            severity = "High"
            recommendation = "Verify account status and review licence removal"
            potential_monthly_saving = row["cost_monthly"]

        else:
            inactivity = (as_of - row["last_login"]).days

            if inactivity >= inactive_days:
                finding = "Potentially unused licence"
                severity = "Medium"
                recommendation = (
                    "Confirm application usage with the user or team lead"
                )
                potential_monthly_saving = row["cost_monthly"]

        if finding:
            findings.append({
                "licence_id": row["licence_id"],
                "user_id": row["user_id"],
                "name": row.get("name"),
                "application": row["application"],
                "plan": row["plan"],
                "last_login": row.get("last_login"),
                "cost_monthly": row["cost_monthly"],
                "currency": row["currency"],
                "finding": finding,
                "severity": severity,
                "recommendation": recommendation,
                "potential_monthly_saving": potential_monthly_saving,
                "review_status": "Pending"
            })

    return pd.DataFrame(findings)


def print_licence_summary(findings):

    print("\n=== LICENCE AUDIT SUMMARY ===")

    print(f"Findings detected: {len(findings)}")

    if findings.empty:
        print("No licence issues detected.")
        return

    for currency, group in findings.groupby("currency"):

        monthly = group["potential_monthly_saving"].sum()

    print(f"\nCurrency: {currency}")
    print(f"Potential monthly savings: {monthly:,.2f}")
    print(f"Potential annual savings: {monthly * 12:,.2f}")

    print("\nFindings by category:")

    print(findings["finding"].value_counts())


if __name__ == "__main__":
    users, licences, permissions = load_all_data()

    findings = run_licence_audit(users, licences)

    print_licence_summary(findings)
