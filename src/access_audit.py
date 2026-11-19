
import json
import pandas as pd
from pathlib import Path
from datetime import datetime, timezone


BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_FILE = BASE_DIR / "config" / "settings.json"


def load_security_config():
    """Load access review policies."""

    with open(CONFIG_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def run_access_audit(users, permissions, as_of=None):
    """Identify privileged and potentially excessive access."""

    config = load_security_config()

    privileged_roles = {
        role.lower()
        for role in config["privileged_roles"]
    }

    high_privilege_roles = {
        role.lower()
        for role in config["high_privilege_roles"]
    }

    dormant_days = config["dormant_admin_days"]

    if as_of is None:
        as_of = datetime.now(timezone.utc)

    as_of = pd.Timestamp(as_of)

    if as_of.tzinfo is not None:
        as_of = as_of.tz_localize(None)

    users = users.copy()
    permissions = permissions.copy()

    users["last_login"] = pd.to_datetime(
        users["last_login"], errors="raise"
    )

    # Attach employee information to each permission.
    audit_data = permissions.merge(
        users[
            ["user_id", "name", "email",
             "department", "last_login", "status"]
        ],
        on="user_id",
        how="left",
        validate="many_to_one"
    )

    audit_data["normalized_role"] = (
        audit_data["role"].astype(str).str.strip().str.lower()
    )

    findings = []

    # Count privileged assignments per user.
    audit_data["is_privileged"] = (
        audit_data["normalized_role"].isin(privileged_roles)
    )

    privileged_counts = (
        audit_data.groupby("user_id")["is_privileged"]
        .sum()
        .to_dict()
    )

    for _, row in audit_data.iterrows():

        role = row["normalized_role"]
        finding = None
        severity = "None"
        recommendation = "No action required"

        if role not in privileged_roles:
            finding = "Unclassified role"
            severity = "Medium"
            recommendation = (
                "Verify this role against the approved access policy"
            )

        else:
            inactivity = (as_of - row["last_login"]).days
            user_status = str(row["status"]).strip().lower()

            if role in high_privilege_roles:
                finding = "Highly privileged account"
                severity = "High"
                recommendation = (
                    "Verify business justification and security approval"
                )

            else:
                finding = "Privileged account"
                severity = "Medium"
                recommendation = (
                    "Confirm that administrative access is required"
                )

            if inactivity >= dormant_days:
                finding = "Dormant administrator"
                severity = "Critical"
                recommendation = (
                    "Investigate inactivity and review privileged access"
                )

            if user_status != "active":
                finding = "Privileged access on inactive account"
                severity = "Critical"
                recommendation = (
                    "Verify account status and initiate access remediation"
                )

        if finding:

            findings.append({
                "user_id": row["user_id"],
                "name": row["name"],
                "email": row["email"],
                "department": row["department"],
                "application": row["application"],
                "role": row["role"],
                "last_login": row["last_login"],
                "finding": finding,
                "severity": severity,
                "privileged_assignments": privileged_counts.get(
                    row["user_id"], 0
                ),
                "recommendation": recommendation,
                "review_status": "Pending"
            })

    results = pd.DataFrame(findings)

    # Add a separate finding for users with multiple
    # privileged assignments.
    if not results.empty:

        multiple_privileged = results[
            results["privileged_assignments"] > 1
        ]

        for user_id in multiple_privileged["user_id"].unique():

            user = users[users["user_id"] == user_id].iloc[0]

            user_permissions = audit_data[
                (audit_data["user_id"] == user_id)
                & audit_data["is_privileged"]
            ]

            findings.append({
                "user_id": user_id,
                "name": user["name"],
                "email": user["email"],
                "department": user["department"],
                "application": ", ".join(
                    user_permissions["application"].astype(str)
                ),
                "role": ", ".join(
                    user_permissions["role"].astype(str)
                ),
                "last_login": user["last_login"],
                "finding": "Multiple privileged assignments",
                "severity": "High",
                "privileged_assignments": privileged_counts[user_id],
                "recommendation": (
                    "Review combined administrative access "
                    "and remove unnecessary privileges"
                ),
                "review_status": "Pending"
            })

        results = pd.DataFrame(findings)

    return results


def print_access_summary(findings):

    print("\n=== ACCESS AUDIT SUMMARY ===")

    print(f"Access findings: {len(findings)}")

    if findings.empty:
        print("No access issues detected.")
        return

    print("\nFindings by category:")
    print(findings["finding"].value_counts())

    print("\nFindings by severity:")
    print(findings["severity"].value_counts())

    print("\nDetailed findings:")

    print(
        findings[
            [
                "name",
                "application",
                "role",
                "finding",
                "severity"
            ]
        ].to_string(index=False)
    )
