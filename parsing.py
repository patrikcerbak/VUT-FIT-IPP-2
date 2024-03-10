import instructions as ins
import error


# a class for parsing the XML file
class ParseXml:
    # checks if the arguments are correct and there is a correct number of them
    @staticmethod
    def check_arguments(instruction_element, expected_count):
        for i in range(1, expected_count + 1):
            # find the element "argX"
            arg = instruction_element.find(".//arg" + str(i))
            if arg is None:
                error.error_exit("Wrong XML structure!", 32)
            try:
                # check if it has a type
                if arg.attrib["type"] is None:
                    error.error_exit("Wrong XML structure!", 32)
                # check if it has some value (strings can have empty string)
                elif arg.text is None and arg.attrib["type"] != "string":
                    error.error_exit("Wrong XML structure!", 32)
            except KeyError:
                error.error_exit("Wrong XML structure!", 32)

    # looks up all the labels in the XML file and saves their orders into the Labels structure
    @staticmethod
    def get_labels(input_xml):
        label_elements = input_xml.findall(".//instruction[@opcode='LABEL']")
        for label in label_elements:
            order = int(label.attrib["order"])
            arg1 = ins.Argument("label", label.find(".//arg1").text)
            label_ins = ins.Label(order, arg1)
            label_ins.do()

    # method for parsing all instructions from XML and initializing their respective classes
    @staticmethod
    def parse(input_xml):
        instructions_dictionary = {}

        for i in input_xml.findall("./*"):
            # all elements of the root element must be "instruction"s, otherwise error
            if i.tag != "instruction":
                error.error_exit("Wrong XML structure!", 32)

            # get the order of the instruction and check if it is not repeated and that it is positive
            order = int(i.attrib["order"])
            if order in instructions_dictionary:
                error.error_exit("Multiple instructions have the same order!", 32)
            elif order < 0:
                error.error_exit("Instruction has negative order!", 32)

            # get the instruction opcode
            opcode = i.attrib["opcode"].upper()
            
            # check the opcode with all instruction, get the instructions arguments
            # and initialize the class of the instruction
            if opcode == "MOVE":
                ParseXml.check_arguments(i, 2)
                arg1 = ins.Argument(i.find(".//arg1").attrib["type"], i.find(".//arg1").text.strip().strip())
                arg2 = ins.Argument(i.find(".//arg2").attrib["type"], i.find(".//arg2").text)
                instructions_dictionary[order] = ins.Move(order, arg1, arg2)

            elif opcode == "CREATEFRAME":
                ParseXml.check_arguments(i, 0)
                instructions_dictionary[order] = ins.CreateFrame(order)

            elif opcode == "PUSHFRAME":
                ParseXml.check_arguments(i, 0)
                instructions_dictionary[order] = ins.PushFrame(order)

            elif opcode == "POPFRAME":
                ParseXml.check_arguments(i, 0)
                instructions_dictionary[order] = ins.PopFrame(order)

            elif opcode == "DEFVAR":
                ParseXml.check_arguments(i, 1)
                arg1 = ins.Argument(i.find(".//arg1").attrib["type"], i.find(".//arg1").text.strip())
                instructions_dictionary[order] = ins.DefVar(order, arg1)

            elif opcode == "CALL":
                ParseXml.check_arguments(i, 1)
                arg1 = ins.Argument(i.find(".//arg1").attrib["type"], i.find(".//arg1").text.strip())
                instructions_dictionary[order] = ins.Call(order, arg1)

            elif opcode == "RETURN":
                ParseXml.check_arguments(i, 0)
                instructions_dictionary[order] = ins.Return(order)

            elif opcode == "PUSHS":
                ParseXml.check_arguments(i, 1)
                arg1 = ins.Argument(i.find(".//arg1").attrib["type"], i.find(".//arg1").text.strip())
                instructions_dictionary[order] = ins.PushS(order, arg1)

            elif opcode == "POPS":
                ParseXml.check_arguments(i, 1)
                arg1 = ins.Argument(i.find(".//arg1").attrib["type"], i.find(".//arg1").text.strip())
                instructions_dictionary[order] = ins.PopS(order, arg1)

            elif opcode == "ADD":
                ParseXml.check_arguments(i, 3)
                arg1 = ins.Argument(i.find(".//arg1").attrib["type"], i.find(".//arg1").text.strip())
                arg2 = ins.Argument(i.find(".//arg2").attrib["type"], i.find(".//arg2").text)
                arg3 = ins.Argument(i.find(".//arg3").attrib["type"], i.find(".//arg3").text)
                instructions_dictionary[order] = ins.Add(order, arg1, arg2, arg3)

            elif opcode == "SUB":
                ParseXml.check_arguments(i, 3)
                arg1 = ins.Argument(i.find(".//arg1").attrib["type"], i.find(".//arg1").text.strip())
                arg2 = ins.Argument(i.find(".//arg2").attrib["type"], i.find(".//arg2").text)
                arg3 = ins.Argument(i.find(".//arg3").attrib["type"], i.find(".//arg3").text)
                instructions_dictionary[order] = ins.Sub(order, arg1, arg2, arg3)

            elif opcode == "MUL":
                ParseXml.check_arguments(i, 3)
                arg1 = ins.Argument(i.find(".//arg1").attrib["type"], i.find(".//arg1").text.strip())
                arg2 = ins.Argument(i.find(".//arg2").attrib["type"], i.find(".//arg2").text)
                arg3 = ins.Argument(i.find(".//arg3").attrib["type"], i.find(".//arg3").text)
                instructions_dictionary[order] = ins.Mul(order, arg1, arg2, arg3)

            elif opcode == "IDIV":
                ParseXml.check_arguments(i, 3)
                arg1 = ins.Argument(i.find(".//arg1").attrib["type"], i.find(".//arg1").text.strip())
                arg2 = ins.Argument(i.find(".//arg2").attrib["type"], i.find(".//arg2").text)
                arg3 = ins.Argument(i.find(".//arg3").attrib["type"], i.find(".//arg3").text)
                instructions_dictionary[order] = ins.IDiv(order, arg1, arg2, arg3)

            elif opcode == "LT":
                ParseXml.check_arguments(i, 3)
                arg1 = ins.Argument(i.find(".//arg1").attrib["type"], i.find(".//arg1").text.strip())
                arg2 = ins.Argument(i.find(".//arg2").attrib["type"], i.find(".//arg2").text)
                arg3 = ins.Argument(i.find(".//arg3").attrib["type"], i.find(".//arg3").text)
                instructions_dictionary[order] = ins.Lt(order, arg1, arg2, arg3)

            elif opcode == "GT":
                ParseXml.check_arguments(i, 3)
                arg1 = ins.Argument(i.find(".//arg1").attrib["type"], i.find(".//arg1").text.strip())
                arg2 = ins.Argument(i.find(".//arg2").attrib["type"], i.find(".//arg2").text)
                arg3 = ins.Argument(i.find(".//arg3").attrib["type"], i.find(".//arg3").text)
                instructions_dictionary[order] = ins.Gt(order, arg1, arg2, arg3)

            elif opcode == "EQ":
                ParseXml.check_arguments(i, 3)
                arg1 = ins.Argument(i.find(".//arg1").attrib["type"], i.find(".//arg1").text.strip())
                arg2 = ins.Argument(i.find(".//arg2").attrib["type"], i.find(".//arg2").text)
                arg3 = ins.Argument(i.find(".//arg3").attrib["type"], i.find(".//arg3").text)
                instructions_dictionary[order] = ins.Eq(order, arg1, arg2, arg3)

            elif opcode == "AND":
                ParseXml.check_arguments(i, 3)
                arg1 = ins.Argument(i.find(".//arg1").attrib["type"], i.find(".//arg1").text.strip())
                arg2 = ins.Argument(i.find(".//arg2").attrib["type"], i.find(".//arg2").text)
                arg3 = ins.Argument(i.find(".//arg3").attrib["type"], i.find(".//arg3").text)
                instructions_dictionary[order] = ins.And(order, arg1, arg2, arg3)

            elif opcode == "OR":
                ParseXml.check_arguments(i, 3)
                arg1 = ins.Argument(i.find(".//arg1").attrib["type"], i.find(".//arg1").text.strip())
                arg2 = ins.Argument(i.find(".//arg2").attrib["type"], i.find(".//arg2").text)
                arg3 = ins.Argument(i.find(".//arg3").attrib["type"], i.find(".//arg3").text)
                instructions_dictionary[order] = ins.Or(order, arg1, arg2, arg3)

            elif opcode == "NOT":
                ParseXml.check_arguments(i, 2)
                arg1 = ins.Argument(i.find(".//arg1").attrib["type"], i.find(".//arg1").text.strip())
                arg2 = ins.Argument(i.find(".//arg2").attrib["type"], i.find(".//arg2").text)
                instructions_dictionary[order] = ins.Not(order, arg1, arg2)

            elif opcode == "INT2CHAR":
                ParseXml.check_arguments(i, 2)
                arg1 = ins.Argument(i.find(".//arg1").attrib["type"], i.find(".//arg1").text.strip())
                arg2 = ins.Argument(i.find(".//arg2").attrib["type"], i.find(".//arg2").text)
                instructions_dictionary[order] = ins.Int2Char(order, arg1, arg2)

            elif opcode == "STRI2INT":
                ParseXml.check_arguments(i, 3)
                arg1 = ins.Argument(i.find(".//arg1").attrib["type"], i.find(".//arg1").text.strip())
                arg2 = ins.Argument(i.find(".//arg2").attrib["type"], i.find(".//arg2").text)
                arg3 = ins.Argument(i.find(".//arg3").attrib["type"], i.find(".//arg3").text)
                instructions_dictionary[order] = ins.Stri2Int(order, arg1, arg2, arg3)

            elif opcode == "READ":
                ParseXml.check_arguments(i, 2)
                arg1 = ins.Argument(i.find(".//arg1").attrib["type"], i.find(".//arg1").text.strip())
                arg2 = ins.Argument(i.find(".//arg2").attrib["type"], i.find(".//arg2").text)
                instructions_dictionary[order] = ins.Read(order, arg1, arg2)

            elif opcode == "WRITE":
                ParseXml.check_arguments(i, 1)
                arg1 = ins.Argument(i.find(".//arg1").attrib["type"], i.find(".//arg1").text.strip())
                instructions_dictionary[order] = ins.Write(order, arg1)

            elif opcode == "CONCAT":
                ParseXml.check_arguments(i, 3)
                arg1 = ins.Argument(i.find(".//arg1").attrib["type"], i.find(".//arg1").text.strip())
                arg2 = ins.Argument(i.find(".//arg2").attrib["type"], i.find(".//arg2").text)
                arg3 = ins.Argument(i.find(".//arg3").attrib["type"], i.find(".//arg3").text)
                instructions_dictionary[order] = ins.Concat(order, arg1, arg2, arg3)

            elif opcode == "STRLEN":
                ParseXml.check_arguments(i, 2)
                arg1 = ins.Argument(i.find(".//arg1").attrib["type"], i.find(".//arg1").text.strip())
                arg2 = ins.Argument(i.find(".//arg2").attrib["type"], i.find(".//arg2").text)
                instructions_dictionary[order] = ins.StrLen(order, arg1, arg2)

            elif opcode == "GETCHAR":
                ParseXml.check_arguments(i, 3)
                arg1 = ins.Argument(i.find(".//arg1").attrib["type"], i.find(".//arg1").text.strip())
                arg2 = ins.Argument(i.find(".//arg2").attrib["type"], i.find(".//arg2").text)
                arg3 = ins.Argument(i.find(".//arg3").attrib["type"], i.find(".//arg3").text)
                instructions_dictionary[order] = ins.GetChar(order, arg1, arg2, arg3)

            elif opcode == "SETCHAR":
                ParseXml.check_arguments(i, 3)
                arg1 = ins.Argument(i.find(".//arg1").attrib["type"], i.find(".//arg1").text.strip())
                arg2 = ins.Argument(i.find(".//arg2").attrib["type"], i.find(".//arg2").text)
                arg3 = ins.Argument(i.find(".//arg3").attrib["type"], i.find(".//arg3").text)
                instructions_dictionary[order] = ins.SetChar(order, arg1, arg2, arg3)

            elif opcode == "TYPE":
                ParseXml.check_arguments(i, 2)
                arg1 = ins.Argument(i.find(".//arg1").attrib["type"], i.find(".//arg1").text.strip())
                arg2 = ins.Argument(i.find(".//arg2").attrib["type"], i.find(".//arg2").text)
                instructions_dictionary[order] = ins.Type(order, arg1, arg2)

            elif opcode == "LABEL":
                ParseXml.check_arguments(i, 0)
                # we already went through the labels, so we will use the PassLabel instruction
                instructions_dictionary[order] = ins.PassLabel(order)

            elif opcode == "JUMP":
                ParseXml.check_arguments(i, 1)
                arg1 = ins.Argument(i.find(".//arg1").attrib["type"], i.find(".//arg1").text.strip())
                instructions_dictionary[order] = ins.Jump(order, arg1)

            elif opcode == "JUMPIFEQ":
                ParseXml.check_arguments(i, 3)
                arg1 = ins.Argument(i.find(".//arg1").attrib["type"], i.find(".//arg1").text.strip())
                arg2 = ins.Argument(i.find(".//arg2").attrib["type"], i.find(".//arg2").text)
                arg3 = ins.Argument(i.find(".//arg3").attrib["type"], i.find(".//arg3").text)
                instructions_dictionary[order] = ins.JumpIfEq(order, arg1, arg2, arg3)

            elif opcode == "JUMPIFNEQ":
                ParseXml.check_arguments(i, 3)
                arg1 = ins.Argument(i.find(".//arg1").attrib["type"], i.find(".//arg1").text.strip())
                arg2 = ins.Argument(i.find(".//arg2").attrib["type"], i.find(".//arg2").text)
                arg3 = ins.Argument(i.find(".//arg3").attrib["type"], i.find(".//arg3").text)
                instructions_dictionary[order] = ins.JumpIfNEq(order, arg1, arg2, arg3)

            elif opcode == "EXIT":
                ParseXml.check_arguments(i, 1)
                arg1 = ins.Argument(i.find(".//arg1").attrib["type"], i.find(".//arg1").text.strip())
                instructions_dictionary[order] = ins.Exit(order, arg1)

            elif opcode == "DPRINT":
                ParseXml.check_arguments(i, 1)
                arg1 = ins.Argument(i.find(".//arg1").attrib["type"], i.find(".//arg1").text.strip())
                instructions_dictionary[order] = ins.DPrint(order, arg1)

            elif opcode == "BREAK":
                ParseXml.check_arguments(i, 0)
                instructions_dictionary[order] = ins.Break(order)

            else:
                error.error_exit("Unknown instruction!", 32)

        return instructions_dictionary
