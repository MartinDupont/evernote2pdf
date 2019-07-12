import argparse

from evernote2pdf.read_in import convert


def main():

    p = argparse.ArgumentParser()
    p.add_argument(
        "name",
        help="The name of the person whose journal it is",
    )
    p.add_argument(
        "input_file",
        help="the path to the .enex file you wish to convert",
    )
    p.add_argument(
        "output_dir",
        help="the directory where you want the LaTex files to be saved",
    )

    args = p.parse_args()

    convert(args.name, args.input_file, args.output_dir)
