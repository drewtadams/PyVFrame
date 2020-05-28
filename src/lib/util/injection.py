import sys
import importlib as il
from src.lib.util.settings import *


class Injection:
	''' singleton class that handles python injection from the html components and pages '''
	__instance	= None
	__functions	= {}


	def __init__(self):
		''' private constructor '''
		if Injection.__instance != None:
			raise Exception('Cannot create new instance of singleton class')
		else:
			Injection.__instance = self

			# add custom functions to the __functions table
			s = Settings.get_instance()
			for mod in s.get_cust_modules():
				Injection.__functions[mod] = il.import_module(mod)


	@staticmethod
	def get_instance():
		''' static access method '''
		if Injection.__instance == None:
			Injection()

		return Injection.__instance


	@staticmethod
	def exec_inj(func_str):
		''' executes the code injected into the html '''
		try:
			# check if the function is in the __functions table
			if func_str[:func_str.rfind('.')] in Injection.__functions:
				# separate the module and the function
				mod,func = func_str.rsplit('.',1)

				# store parameters in a list
				op = func_str.find('(')
				cp = func_str.find(')')
				params = tuple(map(lambda a: a.strip(), func_str[op+1:cp].strip(','))) if cp-op > 1 else []
				
				# check if the function has parameters or not and call it
				if params:
					return getattr(Injection.__functions[mod], func[:func.find('(')])(*params)
				
				return getattr(Injection.__functions[mod], func.replace('(','').replace(')',''))()

			return eval(func_str)
		except Exception as e:
			print(e)
			return str(e)