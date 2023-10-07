import re

from dataclasses import dataclass

LOCATION_TEMPLATE = re.compile('([a-zA-Z]+)([0-9]+)')

SMALL_A_CODE = 97
CAPITAL_A_CODE = 65
N_COLUMNS_PER_CHARACTER = 26


@dataclass
class Location:
    row: int
    column: int

    @classmethod
    def from_description(cls, description: str):
        match = LOCATION_TEMPLATE.fullmatch(description)

        column, row = match.groups()

        row_index = int(row)
        column_index = 0

        for (i, character) in enumerate(column[::-1]):
            code = ord(character)

            if code >= SMALL_A_CODE:
                column_index += (code - SMALL_A_CODE + 1) * pow(N_COLUMNS_PER_CHARACTER, i)
            else:
                column_index += (code - CAPITAL_A_CODE + 1) * pow(N_COLUMNS_PER_CHARACTER, i)

        return cls(row = row_index - 1, column = column_index - 1)

    @property
    def description(self):
        column_index = self.column + 1
        column = []

        while column_index > 0:
            column.append(chr(SMALL_A_CODE + column_index % N_COLUMNS_PER_CHARACTER - 1))
            column_index = column_index // N_COLUMNS_PER_CHARACTER

        return f'{"".join(column[::-1])}{self.row + 1}'
