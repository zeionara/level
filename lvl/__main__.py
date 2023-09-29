from click import group, argument


@group()
def main():
    pass


@main.command()
@argument('sheet', type = str, default = 'main')
def pull(sheet):
    print(sheet)


if __name__ == '__main__':
    main()
