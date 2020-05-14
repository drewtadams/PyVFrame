from src.util.decorators import *


def do_something(*args):
	if not args:
		return 2+2
	return args[0]


@ignore(ValueError,default_val=0)
def parse_int(str_arg):
	return int(str_arg)