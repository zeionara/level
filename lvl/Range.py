from dataclasses import dataclass

from .Location import Location
from .util import as_tuple


CELL_SEPARATOR = ':'
SHEET_SEPARATOR = '!'


@dataclass
class Range:
    sheet: str

    first: Location
    last: Location

    @classmethod
    def from_cells(cls, sheet: str, cells: str):
        locations = cells.split(CELL_SEPARATOR, maxsplit = 1)

        assert len(locations) == 2, f'Incorrect range: {cells}'

        first, last = locations

        return cls(
            sheet,
            Location.from_description(first),
            Location.from_description(last)
        )

    @classmethod
    def from_merge(cls, sheet: str, merge: dict):
        return cls(
            sheet,
            Location(merge['startRowIndex'], merge['startColumnIndex']),
            Location(merge['endRowIndex'] - 1, merge['endColumnIndex'] - 1)
        )

    @property
    def description(self):
        # return f'{self.sheet}!{self.cells}'
        return f'{self.sheet}{SHEET_SEPARATOR}{self.first.description}{CELL_SEPARATOR}{self.last.description}'

    @property
    @as_tuple
    def grid(self):
        for row in range(self.first.row, self.last.row + 1):
            yield tuple(
                Location(row, column)
                for column in range(self.first.column, self.last.column + 1)
            )

    def __contains__(self, location: Location):
        return (
            self.first.row <= location.row <= self.last.row and
            self.first.column <= location.column <= self.last.column
        )

    def unshift(self, location: Location):
        assert location in self, f'Location {location.description} is outside of range {self.description} - cannot unshift'

        return location.row - self.first.row, location.column - self.first.column
