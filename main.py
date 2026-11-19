
from src.data_loader import load_all_data, DataValidationError
from src.licence_audit import (
    run_licence_audit,
    print_licence_summary
)


def main():
    try:
        users, licences, permissions = load_all_data()

        print("\n=== LICENCE & ACCESS REVIEW ===")
        print("Data ingestion successful.")

        findings = run_licence_audit(
            users,
            licences,
            inactive_days=90
        )

        print_licence_summary(findings)

        if not findings.empty:
            print("\n=== DETAILED FINDINGS ===")
            print(
                findings[
                    [
                        "licence_id",
                        "name",
                        "application",
                        "finding",
                        "severity",
                        "review_status"
                    ]
                ].to_string(index=False)
            )

    except (FileNotFoundError, DataValidationError) as error:
        print(f"\nAUDIT FAILED: {error}")


if __name__ == "__main__":
    main()
