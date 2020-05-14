import json, os


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
			settings_path = f'{os.getcwd()}{sep}src{sep}util{sep}settings.json'
			with open(settings_path, 'r') as f:
				Settings.__settings = json.loads(f.read())


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
	def minify_js():
		''' getter for minify_js from settings.json '''
		return Settings.__settings['app_settings']['minify_js']


	@staticmethod
	def use_scss():
		''' getter for use_scss from settings.json '''
		return Settings.__settings['app_settings']['use_scss']


	@staticmethod
	def get_cust_modules():
		''' getter for custom_modules from settings.json '''
		return Settings.__settings['app_settings']['custom_modules']
