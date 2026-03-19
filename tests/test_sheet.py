from google.oauth2.service_account import Credentials
import gspread

scopes = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly"
]

creds = Credentials.from_service_account_file(
    "credentials.json",
    scopes=scopes
)

client = gspread.authorize(creds)

sheet = client.open_by_url(
    "https://docs.google.com/spreadsheets/d/1vWPrFQoOKXfaIihTPAFmJyk0isuUj75jNk4Y30hny60/edit?gid=984507337#gid=984507337"
).sheet1

print(sheet.get_all_records()[:3])