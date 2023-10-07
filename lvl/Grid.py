from dataclasses import dataclass

from .Location import Location
from .Cell import Cell
from .Range import Range


@dataclass
class Atom:
    location: Location
    cell: Cell


@dataclass
class Grid:
    atoms: tuple[tuple[Atom]]
    range: Range

    @property
    def description(self):
        strings = []

        last_line = None

        for line in self.atoms:
            string = []

            last_atom = None

            for i, atom in enumerate(line):
                cell = atom.cell

                if last_atom is not None and last_atom.cell == cell:
                    string.extend([' ', '<'])
                elif last_line is not None and last_line[i].cell == cell:
                    string.extend([' ', '^'])
                else:
                    string.extend(['|', cell.text])

                last_atom = atom

            strings.append(
                ''.join(string)
                # '|'.join(atom.cell.text for atom in line)
            )

            last_line = line

        return '\n'.join(strings)

    def __or__(self, call: callable):
        return call(self.description)

    def __getitem__(self, location: Location):
        raise NotImplementedError()

    @classmethod
    def from_google(cls, sheet: str, range_: Range, data: dict):
        merges = []
        merge_to_cell = {}

        for merge in data['merges']:
            merges.append(merge_range := Range.from_merge(sheet, merge))
            merge_to_cell[merge_range.description] = None

        # print(merges, merge_to_cell)

        grid = []

        for row, locations in zip(data['data'][0]['rowData'], range_.grid):
            line = []

            for cell, location in zip(row['values'], locations):
                for merge in merges:
                    if location in merge:
                        if (cell_ := merge_to_cell[merge.description]) is None:
                            merge_to_cell[merge.description] = cell_ = Cell.from_google(cell)

                        line.append(Atom(location, cell_))
                        break
                else:
                    line.append(Atom(location, Cell.from_google(cell)))

            grid.append(tuple(line))

        return cls(
            atoms = tuple(grid),
            range = range_
        )
