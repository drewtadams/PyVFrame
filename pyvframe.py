import sys
import src.lib.util.initializer as i
import src.lib.util.renderer as r
from src.lib.util.logger import *


def main():
    try:
        if len(sys.argv) > 1:
            if sys.argv[1] == 'init':
                initializer = i.Initializer()
                initializer.init()
            elif sys.argv[1] == 'build':
                renderer = r.Renderer()
                renderer.render()
            else:
                raise Exception(f'Invalid command: {sys.argv[1]}')
        else:
            raise Exception(f'Invalid number of command arguments. Expected: pyvframe.py [ init | build ]')
    except Exception as e:
        Logger.error(f'\n\t{e}\n')


if __name__ == '__main__':
    main()