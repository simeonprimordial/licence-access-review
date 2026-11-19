
from src.data_loader import load_all_data, DataValidationError

from src.licence_audit import (
    run_licence_audit,
    print_licence_summary
)

from src.access_audit import (
    run_access_audit,
    print_access_summary
)


def main():

    try:
        users, licences, permissions = load_all_data()

        print("\n================================")
        print(" LICENCE & ACCESS REVIEW SYSTEM")
        print("================================")

        print("\nData ingestion successful.")

        # Licence audit
        licence_findings = run_licence_audit(
            users,
            licences,
            inactive_days=90
        )

        print_licence_summary(licence_findings)

        # Access audit
        access_findings = run_access_audit(
            users,
            permissions
        )

        print_access_summary(access_findings)

        print("\n================================")
        print(" AUDIT EXECUTION COMPLETED")
        print("================================")

    except (FileNotFoundError, DataValidationError) as error:
        print(f"\nAUDIT FAILED: {error}")


if __name__ == "__main__":
    main()
