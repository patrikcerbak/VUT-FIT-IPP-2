import sys
import re

import globals as g
import memory as mem
import error


# a helper function for getting the frame of a given variable
def get_var_frame(var):
    frame = None
    # it checks the first letter of the variable (L, T or G) and decides based on that
    if var.value[0] == "L":
        frame = g.LOCAL_F
    elif var.value[0] == "T":
        frame = g.TEMPORARY_F
    elif var.value[0] == "G":
        frame = g.GLOBAL_F
    else:
        error.error_exit("Wrong variable syntax!", 52)

    if frame is None:
        error.error_exit("The frame does not exists!", 55)
    else:
        return frame


# a helper function for getting the value from a symbol (can be either a variable or a constant)
def get_symbol_value(symbol):
    value = None
    # if it is variable, check its frame and get value
    if symbol.arg_type == "var":
        if symbol.value[0] == "L":
            value = g.LOCAL_F.get(symbol.value[3:])
        elif symbol.value[0] == "T":
            value = g.TEMPORARY_F.get(symbol.value[3:])
        elif symbol.value[0] == "G":
            value = g.GLOBAL_F.get(symbol.value[3:])
    # if it is nil, return None
    elif symbol.arg_type == "nil":
        value = None
    # if it is int, return the value
    elif symbol.arg_type == "int":
        value = int(symbol.value)
    # if it is bool, check its value
    elif symbol.arg_type == "bool":
        if symbol.value.lower() == "true":
            value = True
        elif symbol.value.lower() == "false":
            value = False
        else:
            error.error_exit("Bool must be TRUE or FALSE!", 32)
    # if it is a string...
    elif symbol.arg_type == "string":
        # ...first check if it is an empty string
        if symbol.value is None:
            value = ""
        # ...or else replace all escape sequences with their corresponding value and return the result
        else:
            string = symbol.value

            escape_sequences = re.findall(r"\\[0-9]{3}", string)

            for escape in escape_sequences:
                char_value = chr(int(escape[1:]))
                string = string.replace(escape, char_value)

            value = string
    # if it is something else, just return its value
    else:
        value = symbol.value

    return value


# a class for arguments, it stores the argument typo (int, bool, string etc.) and a value
class Argument:
    def __init__(self, arg_type, value):
        self.arg_type = arg_type
        self.value = value


# a base class for all instructions => all instruction classes are inherited from this
class Instruction:
    def __init__(self, order):
        self.order = order

    order: int  # the order of the instruction

    def do(self):  # implementation of the instruction behaviour
        pass


# CLASSES FOR EACH INSTRUCTION:

class Move(Instruction):
    def __init__(self, order, arg1, arg2):
        super().__init__(order)
        self.arg1 = arg1
        self.arg2 = arg2

    def do(self):
        # gets the frame of the destination variable and value of the second argument (symbol)
        frame = get_var_frame(self.arg1)
        value = get_symbol_value(self.arg2)

        # stores the value in the variable
        # [3:], since the name of variable is after three characters (GF@)
        frame.update(self.arg1.value[3:], value)


class CreateFrame(Instruction):
    def __init__(self, order):
        super().__init__(order)

    def do(self):
        # creates a new frame and stores it into the global temporary frame variable
        g.TEMPORARY_F = mem.Frame()


class PushFrame(Instruction):
    def __init__(self, order):
        super().__init__(order)

    def do(self):
        # check if there was CREATEFRAME before calling this
        if g.TEMPORARY_F is None:
            error.error_exit("No frame was created!", 55)

        g.FRAME_STACK.push(g.LOCAL_F)  # push the local frame into the frame stack
        g.LOCAL_F = g.TEMPORARY_F  # save the temporary frame into the local frame
        g.TEMPORARY_F = None  # temporary frame is now uninitialized


class PopFrame(Instruction):
    def __init__(self, order):
        super().__init__(order)

    def do(self):
        g.TEMPORARY_F = g.LOCAL_F  # move local frame into temporary frame
        popped = g.FRAME_STACK.pop()  # take frame from stack
        if len(g.FRAME_STACK.list) == 0:
            # if the stack is now empty, there was no frame in stack
            error.error_exit("There is no frame in stack!", 55)
        else:
            # else move the popped stack into local frame
            g.LOCAL_F = popped


class DefVar(Instruction):
    def __init__(self, order, arg1):
        super().__init__(order)
        self.arg1 = arg1

    def do(self):
        # initialize new variable
        frame = get_var_frame(self.arg1)
        frame.create(self.arg1.value[3:])


class Call(Instruction):
    def __init__(self, order, arg1):
        super().__init__(order)
        self.arg1 = arg1

    def do(self):
        g.ORDER_STACK.push(g.CURRENT_ORDER)  # save current order into order stack
        g.CURRENT_ORDER = g.LABELS.get(self.arg1.value)  # set the current label to the label order


class Return(Instruction):
    def __init__(self, order):
        super().__init__(order)

    def do(self):
        # pop the order from stack into current order global variable
        g.CURRENT_ORDER = g.ORDER_STACK.pop()


class PushS(Instruction):
    def __init__(self, order, arg1):
        super().__init__(order)
        self.arg1 = arg1

    def do(self):
        # push a value into stack
        value = get_symbol_value(self.arg1)
        g.STACK.push(value)


class PopS(Instruction):
    def __init__(self, order, arg1):
        super().__init__(order)
        self.arg1 = arg1

    def do(self):
        # get a value from stack into variable
        frame = get_var_frame(self.arg1)
        frame.update(self.arg1.value[3:], g.STACK.pop())


class Add(Instruction):
    def __init__(self, order, arg1, arg2, arg3):
        super().__init__(order)
        self.arg1 = arg1
        self.arg2 = arg2
        self.arg3 = arg3

    def do(self):
        # gets the variable frame and the two values
        frame = get_var_frame(self.arg1)
        value1 = get_symbol_value(self.arg2)
        value2 = get_symbol_value(self.arg3)

        # checks the value types and does the addition
        if type(value1) != int or type(value2) != int:
            error.error_exit("Wrong operand type!", 53)
        else:
            frame.update(self.arg1.value[3:], value1 + value2)


class Sub(Instruction):
    def __init__(self, order, arg1, arg2, arg3):
        super().__init__(order)
        self.arg1 = arg1
        self.arg2 = arg2
        self.arg3 = arg3

    def do(self):
        # gets the variable frame and the two values
        frame = get_var_frame(self.arg1)
        value1 = get_symbol_value(self.arg2)
        value2 = get_symbol_value(self.arg3)

        # checks the value types and does the subtraction
        if type(value1) != int or type(value2) != int:
            error.error_exit("Wrong operand type!", 53)
        else:
            frame.update(self.arg1.value[3:], value1 - value2)


class Mul(Instruction):
    def __init__(self, order, arg1, arg2, arg3):
        super().__init__(order)
        self.arg1 = arg1
        self.arg2 = arg2
        self.arg3 = arg3

    def do(self):
        # gets the variable frame and the two values
        frame = get_var_frame(self.arg1)
        value1 = get_symbol_value(self.arg2)
        value2 = get_symbol_value(self.arg3)

        # checks the value types and does the multiplication
        if type(value1) != int or type(value2) != int:
            error.error_exit("Wrong operand type!", 53)
        else:
            frame.update(self.arg1.value[3:], value1 * value2)


class IDiv(Instruction):
    def __init__(self, order, arg1, arg2, arg3):
        super().__init__(order)
        self.arg1 = arg1
        self.arg2 = arg2
        self.arg3 = arg3

    def do(self):
        # gets the variable frame and the two values
        frame = get_var_frame(self.arg1)
        value1 = get_symbol_value(self.arg2)
        value2 = get_symbol_value(self.arg3)

        # checks the value type
        if type(value1) != int or type(value2) != int:
            error.error_exit("Wrong operand type!", 53)
        # checks for division by zero
        elif value2 == 0:
            error.error_exit("Division by zero!", 57)
        # does the whole number division
        else:
            frame.update(self.arg1.value[3:], value1 // value2)


class Lt(Instruction):
    def __init__(self, order, arg1, arg2, arg3):
        super().__init__(order)
        self.arg1 = arg1
        self.arg2 = arg2
        self.arg3 = arg3

    def do(self):
        frame = get_var_frame(self.arg1)
        value1 = get_symbol_value(self.arg2)
        value2 = get_symbol_value(self.arg3)

        # checks for nil
        if value1 is None or value2 is None:
            error.error_exit("Cannot compare with nil@nil", 53)
        # checks if the types are the same
        elif not type(value1) == type(value2):
            error.error_exit("Cannot compare operands with different types!", 53)
        # does the comparison itself
        else:
            frame.update(self.arg1.value[3:], value1 < value2)


class Gt(Instruction):
    def __init__(self, order, arg1, arg2, arg3):
        super().__init__(order)
        self.arg1 = arg1
        self.arg2 = arg2
        self.arg3 = arg3

    def do(self):
        frame = get_var_frame(self.arg1)
        value1 = get_symbol_value(self.arg2)
        value2 = get_symbol_value(self.arg3)

        # checks for nil
        if value1 is None or value2 is None:
            error.error_exit("Cannot compare with nil@nil", 53)
        # checks if the types are the same
        elif not type(value1) == type(value2):
            error.error_exit("Cannot compare operands with different types!", 53)
        # does the comparison
        else:
            frame.update(self.arg1.value[3:], value1 > value2)


class Eq(Instruction):
    def __init__(self, order, arg1, arg2, arg3):
        super().__init__(order)
        self.arg1 = arg1
        self.arg2 = arg2
        self.arg3 = arg3

    def do(self):
        frame = get_var_frame(self.arg1)
        value1 = get_symbol_value(self.arg2)
        value2 = get_symbol_value(self.arg3)

        # checks if the types are the same or if at least one type is nil
        if not type(value1) == type(value2) and value1 is not None and value2 is not None:
            error.error_exit("Cannot compare operands with different types!", 53)
        else:
            frame.update(self.arg1.value[3:], value1 == value2) # compares


class And(Instruction):
    def __init__(self, order, arg1, arg2, arg3):
        super().__init__(order)
        self.arg1 = arg1
        self.arg2 = arg2
        self.arg3 = arg3

    def do(self):
        frame = get_var_frame(self.arg1)
        value1 = get_symbol_value(self.arg2)
        value2 = get_symbol_value(self.arg3)

        # checks for types and does the operation
        if type(value1) != bool or type(value2) != bool:
            error.error_exit("Wrong operand type!", 53)
        else:
            frame.update(self.arg1.value[3:], value1 and value2)


class Or(Instruction):
    def __init__(self, order, arg1, arg2, arg3):
        super().__init__(order)
        self.arg1 = arg1
        self.arg2 = arg2
        self.arg3 = arg3

    def do(self):
        frame = get_var_frame(self.arg1)
        value1 = get_symbol_value(self.arg2)
        value2 = get_symbol_value(self.arg3)

        # checks for types and does the operation
        if type(value1) != bool or type(value2) != bool:
            error.error_exit("Wrong operand type!", 53)
        else:
            frame.update(self.arg1.value[3:], value1 or value2)


class Not(Instruction):
    def __init__(self, order, arg1, arg2):
        super().__init__(order)
        self.arg1 = arg1
        self.arg2 = arg2

    def do(self):
        frame = get_var_frame(self.arg1)
        value = get_symbol_value(self.arg2)

        # checks for type and does the operation
        if type(value) != bool:
            error.error_exit("Wrong operand type!", 53)
        else:
            frame.update(self.arg1.value[3:], not value)


class Int2Char(Instruction):
    def __init__(self, order, arg1, arg2):
        super().__init__(order)
        self.arg1 = arg1
        self.arg2 = arg2

    def do(self):
        frame = get_var_frame(self.arg1)
        value = get_symbol_value(self.arg2)

        # checks if the value is int
        if type(value) != int:
            error.error_exit("Wrong operand type!", 53)

        # tries to convert the int into char with chr()
        try:
            frame.update(self.arg1.value[3:], chr(value))
        except ValueError:
            # captures the exception when given wrong value and prints the error message
            error.error_exit("Non valid value!", 58)


class Stri2Int(Instruction):
    def __init__(self, order, arg1, arg2, arg3):
        super().__init__(order)
        self.arg1 = arg1
        self.arg2 = arg2
        self.arg3 = arg3

    def do(self):
        frame = get_var_frame(self.arg1)
        value1 = get_symbol_value(self.arg2)
        value2 = get_symbol_value(self.arg3)

        # checks for symbol types
        if type(value1) != str or type(value2) != int:
            error.error_exit("Wrong operand type!", 53)
        if value2 >= len(value1):
            error.error_exit("Index out of range!", 58)

        # tries to convert the char into int
        try:
            frame.update(self.arg1.value[3:], ord(value1[value2]))
        except ValueError:
            # captures the exception and prints the error message
            error.error_exit("Non valid value!", 58)


class Read(Instruction):
    def __init__(self, order, arg1, arg2):
        super().__init__(order)
        self.arg1 = arg1
        self.arg2 = arg2

    def do(self):
        frame = get_var_frame(self.arg1)

        # check if the arguments is of the type "type"
        if self.arg2.arg_type != "type":
            error.error_exit("Type must be specified!", 32)

        value = get_symbol_value(self.arg2)  # get its value

        # it MUST be either int, string or bool
        if value not in ["int", "string", "bool"]:
            error.error_exit("Wrong specified type!", 53)

        # read line from the input source
        inputted = g.READ_INPUT.readline()
        if inputted == "":
            # nothing was inputted
            frame.update(self.arg1.value[3:], None)
        elif value == "int":
            # try to convert the input into int
            try:
                frame.update(self.arg1.value[3:], int(inputted))
            except ValueError:
                frame.update(self.arg1.value[3:], None)
        elif value == "string":
            # get the string
            frame.update(self.arg1.value[3:], inputted)
        elif value == "bool":
            # get bool value
            if inputted.lower() == "true":
                frame.update(self.arg1.value[3:], True)
            elif inputted.lower() == "false":
                frame.update(self.arg1.value[3:], False)
            else:
                frame.update(self.arg1.value[3:], None)


class Write(Instruction):
    def __init__(self, order, arg1):
        super().__init__(order)
        self.arg1 = arg1

    def do(self):
        # gets the value and prints it (and flushes it to be printed right now)
        value = get_symbol_value(self.arg1)
        if type(value) == bool:
            if value:
                print("true", end="", flush=True)
            else:
                print("false", end="", flush=True)
        elif value is None:
            print("", end="", flush=True)
        else:
            print(value, end="", flush=True)


class Concat(Instruction):
    def __init__(self, order, arg1, arg2, arg3):
        super().__init__(order)
        self.arg1 = arg1
        self.arg2 = arg2
        self.arg3 = arg3

    def do(self):
        frame = get_var_frame(self.arg1)
        value1 = get_symbol_value(self.arg2)
        value2 = get_symbol_value(self.arg3)

        # checks for correct types
        if type(value1) != str or type(value2) != str:
            error.error_exit("Wrong operand type!", 53)

        # concats the strings
        frame.update(self.arg1.value[3:], value1 + value2)


class StrLen(Instruction):
    def __init__(self, order, arg1, arg2):
        super().__init__(order)
        self.arg1 = arg1
        self.arg2 = arg2

    def do(self):
        frame = get_var_frame(self.arg1)
        value = get_symbol_value(self.arg2)

        if type(value) != str:
            error.error_exit("Wrong operand type!", 53)

        frame.update(self.arg1.value[3:], len(value)) # gets the string length


class GetChar(Instruction):
    def __init__(self, order, arg1, arg2, arg3):
        super().__init__(order)
        self.arg1 = arg1
        self.arg2 = arg2
        self.arg3 = arg3

    def do(self):
        frame = get_var_frame(self.arg1)
        value1 = get_symbol_value(self.arg2)
        value2 = get_symbol_value(self.arg3)

        # check for correct types
        if type(value1) != str or type(value2) != int:
            error.error_exit("Wrong operand type!", 53)
        # and if the index is in the range
        elif value2 >= len(value1):
            error.error_exit("Index out of range!", 58)
        # then get the char
        else:
            frame.update(self.arg1.value[3:], value1[value2])


class SetChar(Instruction):
    def __init__(self, order, arg1, arg2, arg3):
        super().__init__(order)
        self.arg1 = arg1
        self.arg2 = arg2
        self.arg3 = arg3

    def do(self):
        frame = get_var_frame(self.arg1)
        value1 = get_symbol_value(self.arg1)
        value2 = get_symbol_value(self.arg2)
        value3 = get_symbol_value(self.arg3)

        # check for the values, if they have the correct types
        if type(value1) != str or type(value2) != int or type(value3) != str:
            error.error_exit("Wrong operand type!", 53)
        # check if the index is out of range or the string is empty
        elif value2 >= len(value1) or value3 == "":
            error.error_exit("Wrong operation with strings!", 58)
        else:
            string = value1
            # split the string and set the char
            final_string = string[:value2] + value3 + string[value2 + 1:]
            frame.update(self.arg1.value[3:], final_string)


class Type(Instruction):
    def __init__(self, order, arg1, arg2):
        super().__init__(order)
        self.arg1 = arg1
        self.arg2 = arg2

    def do(self):
        frame = get_var_frame(self.arg1)

        # if the type of the symbol is variable
        if self.arg2.arg_type == "var":
            symbol_frame = get_var_frame(self.arg2)
            # and the variable has no type (it is uninitialized)
            if self.arg2.value[3:] in symbol_frame.defined_vars:
                # return empty string
                frame.update(self.arg1.value[3:], "")
                return

        # get the value
        value = get_symbol_value(self.arg2)

        # check for its type and save the string corresponding to the type
        if value is None:
            frame.update(self.arg1.value[3:], "nil")
        elif type(value) == int:
            frame.update(self.arg1.value[3:], "int")
        elif type(value) == bool:
            frame.update(self.arg1.value[3:], "bool")
        elif type(value) == str:
            frame.update(self.arg1.value[3:], "string")


class Label(Instruction):
    def __init__(self, order, arg1):
        super().__init__(order)
        self.arg1 = arg1

    def do(self):
        # add the label into the labels variable (with the order of this instruction)
        g.LABELS.add(self.arg1.value, self.order)


class PassLabel(Instruction):
    def __init__(self, order):
        super().__init__(order)

    def do(self):
        # a function representing labels once the labels were already checked
        pass


class Jump(Instruction):
    def __init__(self, order, arg1):
        super().__init__(order)
        self.arg1 = arg1

    def do(self):
        # set the current order variable to the order of the label
        g.CURRENT_ORDER = g.LABELS.get(self.arg1.value)


class JumpIfEq(Instruction):
    def __init__(self, order, arg1, arg2, arg3):
        super().__init__(order)
        self.arg1 = arg1
        self.arg2 = arg2
        self.arg3 = arg3

    def do(self):
        value1 = get_symbol_value(self.arg2)
        value2 = get_symbol_value(self.arg3)

        # check if the types are the same (or there is nil)
        if not type(value1) == type(value2) and value1 is not None and value2 is not None:
            error.error_exit("Wrong operand type!", 53)

        # check the condition itself
        if value1 == value2:
            g.CURRENT_ORDER = g.LABELS.get(self.arg1.value)


class JumpIfNEq(Instruction):
    def __init__(self, order, arg1, arg2, arg3):
        super().__init__(order)
        self.arg1 = arg1
        self.arg2 = arg2
        self.arg3 = arg3

    def do(self):
        value1 = get_symbol_value(self.arg2)
        value2 = get_symbol_value(self.arg3)

        # check if the types are the same (or there is nil)
        if not type(value1) == type(value2) and value1 is not None and value2 is not None:
            error.error_exit("Wrong operand type!", 53)

        # check the condition itself
        if value1 != value2:
            g.CURRENT_ORDER = g.LABELS.get(self.arg1.value)


class Exit(Instruction):
    def __init__(self, order, arg1):
        super().__init__(order)
        self.arg1 = arg1

    def do(self):
        value = get_symbol_value(self.arg1)

        # check if the type is int
        if type(value) != int:
            error.error_exit("Wrong operand type!", 53)
        # check if the value is in the range it should be in (0 - 49)
        if value < 0 or value > 49:
            error.error_exit("Wrong operand value!", 57)

        sys.exit(value)


class DPrint(Instruction):
    def __init__(self, order, arg1):
        super().__init__(order)
        self.arg1 = arg1

    def do(self):
        value = get_symbol_value(self.arg1.value)

        # print the value of the given symbol into stderr
        if type(value) == bool:
            if value:
                print("true", end='', file=sys.stderr)
            else:
                print("false", end='', file=sys.stderr)
        elif value is None:
            print("", end='', file=sys.stderr)
        else:
            print(value, end='', file=sys.stderr)


class Break(Instruction):
    def __init__(self, order):
        super().__init__(order)

    def do(self):
        # print information about the program to stderr
        print("Current instruction order: " + str(g.CURRENT_ORDER), file=sys.stderr)
        print("Temporary frame: ", file=sys.stderr)
        if g.TEMPORARY_F is not None:
            print(g.TEMPORARY_F.dictionary, file=sys.stderr)
        print("Local frame variables: ", file=sys.stderr)
        if g.LOCAL_F is not None:
            print(g.LOCAL_F.dictionary, file=sys.stderr)
        print("Global frame variables: ", file=sys.stderr)
        print(g.GLOBAL_F.dictionary, file=sys.stderr)
        print("Number of elements in stack: " + str(len(g.STACK.list)), file=sys.stderr)
        # -1, since there is the first helper None element
        print("Number of elements in frame stack: " + str(len(g.FRAME_STACK.list) - 1), file=sys.stderr)
        print("Number of elements in orders stack: " + str(len(g.ORDER_STACK.list)), file=sys.stderr)
