import gspread
from google.oauth2.service_account import Credentials

from config import (
    GOOGLE_CREDENTIALS,
    SPREADSHEET_ID,
    DISCORD_SHEET,
    NEGATIVE_SHEET,
    FLOOR_SHEET,
    SUMMARY_SHEET,
)


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def get_spreadsheet():
    creds = Credentials.from_service_account_info(
        GOOGLE_CREDENTIALS,
        scopes=SCOPES,
    )
    client = gspread.authorize(creds)
    return client.open_by_key(SPREADSHEET_ID)


def get_or_create_worksheet(spreadsheet, title, rows=1000, cols=20):
    try:
        return spreadsheet.worksheet(title)
    except gspread.WorksheetNotFound:
        return spreadsheet.add_worksheet(title=title, rows=rows, cols=cols)


def get_records(sheet_name):
    spreadsheet = get_spreadsheet()
    worksheet = spreadsheet.worksheet(sheet_name)
    return worksheet.get_all_records()


def ensure_summary_sheet():
    spreadsheet = get_spreadsheet()
    worksheet = get_or_create_worksheet(spreadsheet, SUMMARY_SHEET)

    headers = [
        "요약일자",
        "일별 리포트",
        "생성 시간",
    ]

    current = worksheet.row_values(1)
    if current != headers:
        worksheet.clear()
        worksheet.append_row(headers)

    return worksheet


def append_summary(row):
    worksheet = ensure_summary_sheet()
    worksheet.append_row(row, value_input_option="USER_ENTERED")
