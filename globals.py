import memory as mem


FRAME_STACK = mem.Stack()  # stack of frames (LF)
FRAME_STACK.push(None)  # pushing None to have some item in it

LOCAL_F = None  # local frame
TEMPORARY_F = None  # temporary frame
GLOBAL_F = mem.Frame()  # global frame

STACK = mem.Stack()  # stack for values

LABELS = mem.Labels()  # structure for storing labels

CURRENT_ORDER = 1  # variable to store the current order while going through the program
ORDER_STACK = mem.Stack()  # stack of order (with CALL and RETURN)

READ_INPUT = None  # file to read the input from
