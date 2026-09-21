import argparse
import glob
import sys
from itertools import chain
from os.path import isfile

import sigtype


def main() -> None:
    """Run the sigtype CLI entry point."""
    parser = argparse.ArgumentParser(prog="sigtype", description="Determine type of FILEs.")
    parser.add_argument("file", nargs="+", help="files, wildcard is supported")
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {sigtype.version}",
        help="output version information and exit",
    )

    args = parser.parse_args()
    items = chain.from_iterable(map(glob.iglob, args.file))
    files = filter(isfile, items)

    for file in files:
        kind = sigtype.guess(file)
        if kind is None:
            sys.stdout.write(f"{file}: cannot determine file type\n")
        else:
            sys.stdout.write(f"{file}: {kind.mime} ({kind.extension})\n")


if __name__ == "__main__":
    main()
