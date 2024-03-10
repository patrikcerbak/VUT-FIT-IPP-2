import error


# a class used for storing the variable frames
class Frame:
    def __init__(self):
        self.dictionary = {}  # name : value
        self.defined_vars = []  # name

    # creates a uninitialized variable
    def create(self, name):
        if name in self.dictionary or name in self.defined_vars:
            error.error_exit("Redefinition of a variable!", 52)
        else:
            self.defined_vars.append(name)

    # updates a value of a variable (and if it was uninitialized, it moves it into the main dictionary)
    def update(self, name, value):
        if name in self.dictionary:
            self.dictionary[name] = value
        elif name in self.defined_vars:
            self.dictionary[name] = value
            self.defined_vars.remove(name)
        else:
            error.error_exit("The variable does not exist!", 54)

    # gets the value of a variable with given name
    def get(self, name):
        if name in self.dictionary:
            return self.dictionary[name]
        else:
            error.error_exit("The variable does not exist!", 54)


class Stack:
    def __init__(self):
        self.list = []  # value

    # pushes a value into the stack
    def push(self, value):
        self.list.append(value)

    # checks if there is something in the stack and then pops a value
    def pop(self):
        if len(self.list) == 0:
            error.error_exit("The stack is empty!", 56)
        else:
            return self.list.pop()


# a class for storing the information about labels
class Labels:
    def __init__(self):
        self.dictionary = {}  # name : order

    # checks if the given label is new and then adds it with its order into the dictionary
    def add(self, name, order):
        if name in self.dictionary and self.dictionary[name] != order:
            error.error_exit("The label was already defined!", 52)
        else:
            self.dictionary[name] = order

    # gets the order of the label with given name
    def get(self, name):
        if name in self.dictionary:
            return self.dictionary[name]
        else:
            error.error_exit("Undefined label!", 52)