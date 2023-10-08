from __future__ import annotations

from time import sleep
from dataclasses import dataclass

from .Location import Location
from .Cell import Cell
from .Range import Range


@dataclass
class Atom:
    location: Location
    cell: Cell

    top: Atom = None
    left: Atom = None
    bottom: Atom = None
    right: Atom = None


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
                    string.extend(['|', '^'])
                else:
                    string.extend(['|', '-' if cell.text is None else cell.text])

                if cell.is_header:
                    string.append('*')

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
        row, column = self.range.unshift(location)

        return self.atoms[row][column]

    def trace_headers(self, location: Location):
        atom = self[location]

        cells = []

        top = atom

        while top is not None:
            if (cell := top.cell) not in cells and cell.is_header and cell != atom.cell:
                cells.append(cell)

            top = top.top

        left = atom

        while left is not None:
            if (cell := left.cell) not in cells and cell.is_header and cell != atom.cell:
                cells.append(cell)

            left = left.left

        return cells

    @classmethod
    def from_google(cls, sheet: str, range_: Range, data: dict):
        merges = []
        merge_to_cell = {}

        merges_ = data.get('merges')

        if merges_ is not None:
            for merge in merges_:
                merges.append(merge_range := Range.from_merge(sheet, merge))
                merge_to_cell[merge_range.description] = None

        # print(merges, merge_to_cell)

        grid = []

        top = None

        for row, locations in zip(data['data'][0]['rowData'], range_.grid):
            line = []

            left = None

            def push(location, cell_, i):
                nonlocal line, left, top

                # print('pushing', i, cell_.text, 'top will be', None if top is None else top[i])
                # print(None if top is None else [atom.cell.text for atom in top])

                line.append(
                    atom := Atom(
                        location, cell_,
                        left = None if left is None else left,
                        top = None if top is None else top[i]
                    )
                )

                # if (atom.cell.text == 'seven'):
                #     print(atom.top.top.cell.text)

                if left is not None:
                    left.right = atom

                if top is not None:
                    top[i].bottom = atom

                left = atom

            if 'values' in row:
                for i, (cell, location) in enumerate(zip(row['values'], locations)):
                    for merge in merges:
                        if location in merge:
                            if (cell_ := merge_to_cell[merge.description]) is None:
                                merge_to_cell[merge.description] = cell_ = Cell.from_google(cell)

                            push(location, cell_, i)

                            # line.append(
                            #     atom := Atom(
                            #         location, cell_,
                            #         left = None if left is None else left,
                            #         top = None if top is None else top[i]
                            #     )
                            # )

                            # if left is not None:
                            #     left.right = atom

                            # if top is not None:
                            #     top.bottom = atom

                            break
                    else:
                        push(location, Cell.from_google(cell), i)

                        # line.append(
                        #     Atom(
                        #         location, Cell.from_google(cell),
                        #         left = None if left is None else left
                        #     )
                        # )
            else:
                for location in locations:
                    # line.append(Atom(location, Cell.empty()))
                    push(location, Cell.empty(), i)

            grid.append(tuple(line))
            top = line

        grid = cls(
            atoms = tuple(grid),
            range = range_
        )

        # print(grid[Location.from_description('c7')].top.top.cell.text)
        print([cell.text for cell in grid.trace_headers(Location.from_description('c7'))])

        return grid
