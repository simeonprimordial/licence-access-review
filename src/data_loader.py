
import pandas as pd
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


class DataValidationError(Exception):
    """Raised when input data fails validation."""
    pass


def load_csv(filename, required_columns):
    """Load a CSV file and validate its structure."""

    file_path = DATA_DIR / filename

    if not file_path.exists():
        raise FileNotFoundError(f"Dataset not found: {file_path}")

    df = pd.read_csv(file_path)

    missing_columns = set(required_columns) - set(df.columns)

    if missing_columns:
        raise DataValidationError(
            f"{filename} is missing columns: {missing_columns}"
        )

    if df.empty:
        raise DataValidationError(
            f"{filename} contains no records"
        )

    return df


def load_users():
    users = load_csv(
        "users.csv",
        ["user_id", "name", "email", "department",
         "last_login", "status"]
    )

    users["last_login"] = pd.to_datetime(
        users["last_login"], errors="coerce"
    )

    if users["user_id"].isna().any():
        raise DataValidationError("Users contain missing user IDs")

    if users["user_id"].duplicated().any():
        raise DataValidationError("Duplicate user IDs detected")

    if users["last_login"].isna().any():
        raise DataValidationError("Invalid or missing login dates")

    return users


def load_licences():
    licences = load_csv(
        "licences.csv",
        ["licence_id", "user_id", "application",
         "plan", "cost_monthly", "currency"]
    )

    if licences["licence_id"].isna().any():
        raise DataValidationError("Missing licence IDs")

    if licences["licence_id"].duplicated().any():
        raise DataValidationError("Duplicate licence IDs detected")

    licences["cost_monthly"] = pd.to_numeric(
        licences["cost_monthly"], errors="coerce"
    )

    if licences["cost_monthly"].isna().any():
        raise DataValidationError("Invalid licence costs")

    if (licences["cost_monthly"] < 0).any():
        raise DataValidationError("Negative licence costs detected")

    return licences


def load_permissions():
    permissions = load_csv(
        "permissions.csv",
        ["user_id", "application", "role", "permission_level"]
    )

    if permissions["user_id"].isna().any():
        raise DataValidationError(
            "Permissions contain missing user IDs"
        )

    return permissions


def load_all_data():
    """Load all datasets and validate relationships."""

    users = load_users()
    licences = load_licences()
    permissions = load_permissions()

    valid_user_ids = set(users["user_id"])

    assigned_licences = licences["user_id"].dropna()
    assigned_permissions = permissions["user_id"]

    unknown_licence_users = set(assigned_licences) - valid_user_ids
    unknown_permission_users = set(assigned_permissions) - valid_user_ids

    if unknown_licence_users:
        raise DataValidationError(
            f"Licences reference unknown users: {unknown_licence_users}"
        )

    if unknown_permission_users:
        raise DataValidationError(
            f"Permissions reference unknown users: {unknown_permission_users}"
        )

    return users, licences, permissions
