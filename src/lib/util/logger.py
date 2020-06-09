from src.lib.util.settings import *


class Logger:
    ''' class that handles console logging '''
    __logger_root_setting = 'app_settings.logger'


    @staticmethod
    def info(info_msg):
        ''' prints the passed info_msg to the console if info logs are turned on '''
        if Settings.get_instance().prop(f'{Logger.__logger_root_setting}.info'):
            print(info_msg)


    @staticmethod
    def warning(warning_msg):
        ''' prints the passed warning_msg to the console if warning logs are turned on '''
        if Settings.get_instance().prop(f'{Logger.__logger_root_setting}.warning'):
            print(f'\033[93m{warning_msg}\033[0m')


    @staticmethod
    def error(error_msg):
        ''' prints the passed error_msg to the console if error logs are turned on '''
        if Settings.get_instance().prop(f'{Logger.__logger_root_setting}.error'):
            print(f'\033[31m{error_msg}\033[0m')