
import logging
import sys

from src.data_loader import load_all_data, DataValidationError
from src.licence_audit import run_licence_audit
from src.access_audit import run_access_audit
from src.report_generator import generate_report


logging.basicConfig(
    filename="logs/monthly_review.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


def main():

    try:
        logger.info("Monthly access review started")

        # 1. Load datasets
        users, licences, permissions = load_all_data()

        logger.info(
            "Data loaded: users=%s licences=%s permissions=%s",
            len(users),
            len(licences),
            len(permissions)
        )

        # 2. Licence audit
        licence_findings = run_licence_audit(
            users,
            licences,
            inactive_days=90
        )

        logger.info(
            "Licence audit completed: %s findings",
            len(licence_findings)
        )

        # 3. Access audit
        access_findings = run_access_audit(
            users,
            permissions
        )

        logger.info(
            "Access audit completed: %s findings",
            len(access_findings)
        )

        # 4. Generate report
        report = generate_report(
            users,
            licences,
            licence_findings,
            access_findings
        )

        logger.info("Report generated: %s", report)
        logger.info("Monthly access review completed successfully")

        print(f"Audit successful: {report}")

    except Exception:
        logger.exception("Monthly access review failed")
        raise


if __name__ == "__main__":

    try:
        main()
    except Exception:
        sys.exit(1)
