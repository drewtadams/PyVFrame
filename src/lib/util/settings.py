import json, os
from src.lib.util.logger import *


class Settings:
	''' singleton class that stores the settings.json values '''
	__instance = None
	__settings = None


	def __init__(self):
		''' private constructor '''
		if Settings.__instance != None:
			raise Exception('Cannot create new instance of a singleton class')
		else:
			Settings.__instance = self

			sep = os.sep
			settings_path = f'{os.getcwd()}{sep}settings.json'
			with open(settings_path, 'r') as f:
				Settings.__settings = json.loads(f.read())


	@staticmethod
	def render_path(path, *args):
		''' replaces all forward separators in path with the os equivalent '''
		while '{' in path and '}' in path:
			start = path.find('{')
			end = path.find('}')+1
			replacement = path[start:end]

			# get the path of the injected directory
			prop = replacement[start+1:end-1]
			# TODO: build out the json path for the directory with *args; e.g. app_settings

			# 
			if Settings.has_prop(f'app_settings.{prop}'):
				inj_path = Settings.prop(f'app_settings.{prop}')
				path = path.replace(replacement, inj_path)
			else:
				print(f'\tPath for "{prop}" does not exist in settings.json - building path without path injection')
				path = path.replace(replacement, f'{os.sep}{prop}')

		return path.replace('/', os.sep)


	@staticmethod
	def get_instance():
		''' static access method '''
		if Settings.__instance == None:
			Settings()

		return Settings.__instance


	@staticmethod
	def has_prop(prop_name):
		''' . '''
		tree = Settings.__settings

		props = prop_name.split('.')
		for prop in props:
			if prop in tree:
				tree = tree[prop]
			else:
				return False
		return True


	@staticmethod
	def prop(key_str):
		''' . '''
		prop = Settings.__settings
		keys = key_str.split('.')

		for key in keys:
			if key in prop:
				prop = prop[key]
			else:
				return key_str

		return prop


	@staticmethod
	def get_build_tree():
		''' returns a list of all directory paths under the build directory from settings.json '''
		dirs = []
		for k,v in Settings.__settings['app_settings'].items():
			if type(v) == str and ('/build' in v or '{build_dir}' in v):
				dirs.append(Settings.render_path(v))

		return dirs


	@staticmethod
	def get_dist_tree():
		''' returns a list of all directory paths under the dist directory from settings.json '''
		dirs = []
		for k,v in Settings.__settings['app_settings'].items():
			if type(v) == str and ('/dist' in v or '{dist_dir}' in v):
				dirs.append(Settings.render_path(v))

		return dirs


	@staticmethod
	def use_starter_files():
		''' getter for use_starter_files from settings.json '''
		return Settings.__settings['app_settings']['use_starter_files']


	@staticmethod
	def get_starter_files():
		''' getter for the starter files' paths '''
		files = []
		for path in Settings.__settings['app_settings']['starter_files']:
			files.append(Settings.render_path(path))
		return files


	@staticmethod
	def build_dir():
		''' getter for the build directory root '''
		return Settings.render_path(Settings.__settings['app_settings']['build_dir'])


	@staticmethod
	def dist_dir():
		''' getter for the dist directory root '''
		return Settings.render_path(Settings.__settings['app_settings']['dist_dir'])


	@staticmethod
	def minify_js():
		''' getter for minify_js from settings.json '''
		return Settings.__settings['app_settings']['minify_js']


	@staticmethod
	def minify_css():
		''' . '''
		return Settings.__settings['app_settings']['minify_css']


	@staticmethod
	def use_scss():
		''' getter for use_scss from settings.json '''
		return Settings.__settings['app_settings']['use_scss']


	@staticmethod
	def get_cust_modules():
		''' getter for custom_modules from settings.json '''
		return Settings.__settings['app_settings']['custom_modules']
