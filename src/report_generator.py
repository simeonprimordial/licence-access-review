
import csv

from pathlib import Path
from datetime import datetime

import pandas as pd

from openpyxl import Workbook
from openpyxl.styles import (
    Font,
    PatternFill,
    Alignment,
    Border,
    Side
)
from openpyxl.utils import get_column_letter


BASE_DIR = Path(__file__).resolve().parent.parent
REPORT_DIR = BASE_DIR / "reports"

HEADER_FILL = PatternFill(
    fill_type="solid",
    fgColor="17365D"
)

HEADER_FONT = Font(
    bold=True,
    color="FFFFFF"
)

SEVERITY_COLORS = {
    "Critical": "F4CCCC",
    "High": "FCE4D6",
    "Medium": "FFF2CC",
    "Low": "D9EAD3"
}


def style_worksheet(ws):

    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions

    for cell in ws[1]:
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = Alignment(
            horizontal="center",
            vertical="center"
        )

    ws.row_dimensions[1].height = 25

    for column_cells in ws.columns:

        column_letter = get_column_letter(
            column_cells[0].column
        )

        max_length = max(
            len(str(cell.value or ""))
            for cell in column_cells
        )

        ws.column_dimensions[column_letter].width = min(
            max(max_length + 3, 14),
            45
        )

    thin_border = Border(
        bottom=Side(
            style="thin",
            color="D9E2F3"
        )
    )

    for row in ws.iter_rows(min_row=2):
        for cell in row:
            cell.border = thin_border
            cell.alignment = Alignment(
                vertical="center",
                wrap_text=True
            )


def write_dataframe(wb, sheet_name, df):

    ws = wb.create_sheet(sheet_name)

    # Make an empty report understandable.
    if df.empty:
        ws.append(["No findings detected"])
        return ws

    ws.append(list(df.columns))

    for row in df.itertuples(index=False, name=None):
        ws.append([
            value.isoformat() if isinstance(value, (datetime, pd.Timestamp))
            else value
            for value in row
        ])

    style_worksheet(ws)

    # Highlight severity cells.
    if "severity" in df.columns:

        severity_column = (
            list(df.columns).index("severity") + 1
        )

        for row in range(2, ws.max_row + 1):

            cell = ws.cell(
                row=row,
                column=severity_column
            )

            color = SEVERITY_COLORS.get(
                str(cell.value),
                "FFFFFF"
            )

            cell.fill = PatternFill(
                fill_type="solid",
                fgColor=color
            )

    return ws


def generate_report(
    users,
    licences,
    licence_findings,
    access_findings
):

    REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    wb = Workbook()

    summary = wb.active
    summary.title = "Executive Summary"

    summary.append(["MONTHLY LICENCE & ACCESS REVIEW"])
    summary.append(["Report generated", datetime.now().isoformat()])
    summary.append(["Users reviewed", len(users)])
    summary.append(["Licence records", len(licences)])
    summary.append(["Licence findings", len(licence_findings)])
    summary.append(["Access findings", len(access_findings)])

    currencies = (
        licence_findings["currency"].dropna().unique()
        if not licence_findings.empty and "currency" in licence_findings
        else []
    )

    for currency in currencies:

        monthly_savings = licence_findings.loc[
            licence_findings["currency"] == currency,
            "potential_monthly_saving"
        ].sum()

        summary.append([
            f"Potential monthly savings ({currency})",
            float(monthly_savings)
        ])

        summary.append([
            f"Potential annual savings ({currency})",
            float(monthly_savings * 12)
        ])

    summary.column_dimensions["A"].width = 38
    summary.column_dimensions["B"].width = 28

    for cell in summary[1]:
        cell.fill = HEADER_FILL
        cell.font = Font(
            bold=True,
            color="FFFFFF",
            size=14
        )

    # Individual audit sheets.
    write_dataframe(
        wb,
        "Licence Findings",
        licence_findings
    )

    write_dataframe(
        wb,
        "Access Findings",
        access_findings
    )

    # Consolidated action tracker.
    licence_tracker = licence_findings.copy()
    access_tracker = access_findings.copy()

    if not licence_tracker.empty:
        licence_tracker["audit_type"] = "Licence"

    if not access_tracker.empty:
        access_tracker["audit_type"] = "Access"

    tracker = pd.concat(
        [licence_tracker, access_tracker],
        ignore_index=True
    )

    tracker = tracker.reindex(
        columns=[
            "audit_type",
            "user_id",
            "name",
            "application",
            "finding",
            "severity",
            "recommendation",
            "review_status"
        ]
    )

    write_dataframe(
        wb,
        "Remediation Tracker",
        tracker
    )

    # Generate a unique timestamp for this audit.
    run_timestamp = datetime.now().astimezone()

    timestamp = run_timestamp.strftime("%Y%m%d_%H%M%S")

    output_file = (
        REPORT_DIR /
        f"monthly_access_review_{timestamp}.xlsx"
    )

    wb.save(output_file)

    # Maintain a historical audit register.
    history_file = REPORT_DIR / "audit_history.csv"

    history_record = {
        "run_timestamp": run_timestamp.isoformat(),
        "report_file": output_file.name,
        "users_reviewed": len(users),
        "licence_findings": len(licence_findings),
        "access_findings": len(access_findings)
    }

    file_exists = history_file.exists()

    with open(
        history_file,
        "a",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=history_record.keys()
        )

        if not file_exists:
            writer.writeheader()

        writer.writerow(history_record)

    return output_file