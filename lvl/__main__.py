from os import environ as env

from click import group, argument, option

from .Sheets import Sheets


FILE = env['LEVEL_FILE']


@group()
def main():
    pass


@main.command()
@argument('cells', type = str, default = 'A1:B2')
@option('--sheet', '-s', help = 'name of sheet from which to select cells', type = str, default = 'main')
def pull(cells: str, sheet: str):
    sheets = Sheets()[FILE][sheet]

    sheets[cells] | print
    # sheets['d1:e2'] = [['one', 'two'], ['three', 'four']]


if __name__ == '__main__':
    main()
