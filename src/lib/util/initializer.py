import os
from src.lib.util.logger import *
from src.lib.util.settings import *


class Initializer:

    def __init__(self):
        self.settings = Settings.get_instance()

    def init(self):
        ''' initializes the project with build and dist directories and their structure '''
        Logger.info('\n\tInitializing project...')

        self.init_build_dir()
        # self.init_dist_dir()

        Logger.info('\n\tProject build complete.\n')


    def init_build_dir(self):
        ''' create the build directory and its children '''
        Logger.info(f'\n\t\tCreating build/ directory')

        vendor_dirs = [
            self.settings.render_path(self.settings.prop('app_settings.js_dir') + '/vendor'),
            self.settings.render_path(self.settings.prop('app_settings.css_dir') + '/vendor')
        ]

        # create the build directory tree
        self.__make_dirs(self.settings.get_build_tree() + vendor_dirs)

        # generate starter files
        if self.settings.use_starter_files():
            Logger.info(f'\t\tCreating starter files')
            self.__make_files(self.settings.get_starter_files())


    def init_dist_dir(self):
        ''' create the dist directory and its children '''
        Logger.info(f'\n\t\tCreating dist/ directory')

        # create the dist directory tree
        self.__make_dirs(self.settings.get_dist_tree())


    def __make_files(self, files):
        ''' creates files from the passed files list '''
        try:
            root = os.getcwd()
            for file in files:
                abs_path = f'{root}{file}'
                if not os.path.isfile(abs_path):
                    with open(abs_path, 'w') as f:
                        if abs_path.endswith('.css'):
                            f.write(
'''/*
    *** WARNING ***
    Only use this file if you aren't using SCSS! The default setting is to use
    SCSS - to change it, update the "use_scss" value to false in the
    settings.json file.
*/'''
                            )
                    Logger.info(f'\t\t    Created {file}')
                else:
                    Logger.warning(f'\t\t    The file "{abs_path}" already exists')
        except Exception as e:
            Logger.error(f'\n\t\t{e}')


    def __make_dirs(self, tree):
        ''' creates directories from the passed tree '''
        try:
            project_root = os.getcwd()
            for path in tree:
                abs_path = f'{project_root}{path}'
                if not os.path.exists(abs_path):
                    os.makedirs(abs_path)
                    Logger.info(f'\t\t    Created {path}')
                else:
                    Logger.warning(f'\t\t    The directory "{abs_path}" already exists')
            print('')

        except Exception as e:
            Logger.error(f'\n\t\t{e}')