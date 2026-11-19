
from src.data_loader import load_all_data, DataValidationError

from src.licence_audit import run_licence_audit
from src.access_audit import run_access_audit
from src.report_generator import generate_report


def main():

    try:
        print("\nStarting monthly access review...")

        # Step 1: Load datasets
        users, licences, permissions = load_all_data()

        print("Data ingestion completed.")

        # Step 2: Run licence audit
        licence_findings = run_licence_audit(
            users,
            licences,
            inactive_days=90
        )

        print(
            f"Licence findings: {len(licence_findings)}"
        )

        # Step 3: Run access audit
        access_findings = run_access_audit(
            users,
            permissions
        )

        print(
            f"Access findings: {len(access_findings)}"
        )

        # Step 4: Generate Excel report
        report = generate_report(
            users,
            licences,
            licence_findings,
            access_findings
        )

        print("\n================================")
        print(" AUDIT COMPLETED SUCCESSFULLY")
        print("================================")

        print(f"\nReport generated: {report}")

    except (FileNotFoundError, DataValidationError) as error:
        print(f"\nAUDIT FAILED: {error}")


if __name__ == "__main__":
    main()
