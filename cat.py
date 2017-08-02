import sys


def cat(files):
    """print files"""
    for file_name in files:
        try:
            with open(file_name, 'r') as file:
                lines = file.read()
                print(lines)
        except FileNotFoundError:
            print("{} FILE NOT FOUND".format(file_name))


if __name__ == "__main__":
    cat(sys.argv[1:])
