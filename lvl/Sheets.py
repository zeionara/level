from os import path

from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from googleapiclient.discovery import build, Resource

from .Range import Range
from .Grid import Grid

SCOPES = (
    'https://www.googleapis.com/auth/spreadsheets',
)


class Sheet:
    def __init__(self, service: Resource, file: str, key: str):
        self.service = service
        self.file = file
        self.key = key

    def __getitem__(self, cells: str):
        items = self.service.get(
            spreadsheetId = self.file,
            ranges = [cells],
            includeGridData = True
        ).execute()

        for sheet in items['sheets']:
            props = sheet['properties']

            if props['title'] == self.key:
                return Grid.from_google(self.key, Range.from_cells(self.key, cells), sheet)

        raise ValueError(f'Cannot find sheet "{self.key}" within given file')

    def __setitem__(self, cells: str, values: str):
        self.service.values().update(
            spreadsheetId = self.file,
            range = Range.from_cells(self.key, cells).description,
            valueInputOption = 'RAW',
            body = {
                'values': values
            }
        ).execute()


class File:
    def __init__(self, service: Resource, key: str):
        self.service = service
        self.key = key

    def __getitem__(self, sheet: str):
        return Sheet(self.service, self.key, sheet)


class Sheets:
    def __init__(self, cert_path: str = 'assets/cert.json', token_path: str = 'assets/token.json'):
        self.cert_path = cert_path
        self.token_path = token_path

        creds = None

        if path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)

        if creds is None or not creds.valid:
            if creds is not None and creds.expired and creds.refresh_token is not None:
                try:
                    creds.refresh(Request())
                except RefreshError:
                    creds = self._authenticate()
            else:
                creds = self._authenticate()

            with open(token_path, 'w', encoding = 'utf-8') as file:
                file.write(creds.to_json())

        self.creds = creds
        self.service = build('sheets', 'v4', credentials = creds).spreadsheets()

    def _authenticate(self):
        flow = InstalledAppFlow.from_client_secrets_file(self.cert_path, SCOPES)
        return flow.run_local_server(port = 0)

    def __getitem__(self, file: str):
        return File(self.service, file)
