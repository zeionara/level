from os import path
from dataclasses import dataclass

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from googleapiclient.discovery import build, Resource


SCOPES = (
    'https://www.googleapis.com/auth/spreadsheets',
)


@dataclass
class Range:
    sheet: str
    cells: str

    @property
    def description(self):
        return f'{self.sheet}!{self.cells}'


@dataclass
class Cells:
    range: str
    values: list[list[str]]

    def __or__(self, call: callable):
        return call(self.values)


class Sheet:
    def __init__(self, service: Resource, file: str, key: str):
        self.service = service
        self.file = file
        self.key = key

    # def _make_range(self, cells: str):
    #     return f'{self.key}!{cells}'

    def __getitem__(self, cells: str):
        values = self.service.values().get(
            spreadsheetId = self.file,
            range = (range_ := Range(self.key, cells)).description
            # range = self._make_range(cells)
        ).execute().get('values', [])

        return Cells(range = range_, values = values)

    def __setitem__(self, cells: str, values: str):
        self.service.values().update(
            spreadsheetId = self.file,
            range = Range(self.key, cells).description,
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
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(cert_path, SCOPES)
                creds = flow.run_local_server(port = 0)

            with open(token_path, 'w', encoding = 'utf-8') as file:
                file.write(creds.to_json())

        self.creds = creds
        self.service = build('sheets', 'v4', credentials = creds).spreadsheets()

    def __getitem__(self, file: str):
        return File(self.service, file)
