import argparse
import sys
import xml.etree.ElementTree as ET

import globals as g
from parsing import ParseXml
import error


def main():
    # define the arguments parser
    parser = argparse.ArgumentParser(description="Interpret for the IPPcode23 programming language.")
    parser.add_argument("--source", dest="source", help="a path to the XML file to interpret")
    parser.add_argument("--input", dest="input", help="a path to the file with user inputs")

    arguments = parser.parse_args()

    if arguments.source is None and arguments.input is None:
        error.error_exit("No argument was specified!", 10)

    # if source or input were not specified, it will be set to sys.stdin
    if arguments.source is None:
        input_xml = ET.parse(sys.stdin)
    else:
        input_xml = ET.parse(arguments.source)

    if arguments.input is None:
        g.READ_INPUT = sys.stdin
    else:
        g.READ_INPUT = open(arguments.input, "r")

    ParseXml.get_labels(input_xml)  # parse the XML file the first time to get labels and its orders

    instructions = ParseXml.parse(input_xml)  # parse the rest of instructions

    first_order = min(instructions.keys())  # the minimum (first) order
    last_order = max(instructions.keys())  # the maximum (last) order

    g.CURRENT_ORDER = first_order
    while g.CURRENT_ORDER <= last_order:
        # check if the current order is in the instructions dictionary
        if g.CURRENT_ORDER in instructions:
            instructions[g.CURRENT_ORDER].do()  # "do" the instruction
            g.CURRENT_ORDER += 1
        else:
            # otherwise, add to the current order
            g.CURRENT_ORDER += 1

    g.READ_INPUT.close()


if __name__ == '__main__':
    main()
