import os
import sass
import shutil
from jsmin import jsmin
from src.util.injection import *
from src.util.settings import *


class Renderer:

	def __init__(self):
		cwd = os.getcwd()
		sep = os.sep
		dist = f'{cwd}{sep}dist{sep}'
		build = f'{cwd}{sep}build{sep}'

		self.__page_name		= 'default';
		self.__components_path	= f'{build}components{sep}'
		self.__dist_css_path	= f'{dist}assets{sep}css{sep}'
		self.__dist_dir			= f'{dist}'
		self.__dist_js_path		= f'{dist}assets{sep}js{sep}'
		self.__js_path			= f'{build}assets{sep}js{sep}'
		self.__pages_path		= f'{build}pages{sep}'
		self.__scss_path		= f'{build}assets{sep}scss{sep}'


	def render(self):
		''' begins the rendering process '''
		directories = []
		pages = []
		for file in os.listdir(self.__pages_path):
			if os.path.isfile(self.__pages_path+file) and '.html' in file:
				pages.append(file)
			elif os.path.isdir(self.__pages_path+file):
				# todo: move into the directory
				pass

		self.__render_pages(pages)
		self.__render_scss()
		self.__render_js()


	def __render_scss(self):
		''' compiles main.scss to main.css in dist  '''
		sass.compile(dirname=(self.__scss_path, self.__dist_css_path), output_style='compressed')


	def __render_js(self):
		''' minifies js files and writes them to dist '''
		should_minify = Settings.get_instance().minify_js()

		for file in os.listdir(self.__js_path):
			# make sure the file is a js file
			if os.path.isfile(self.__js_path+file) and file.endswith('.js'):
				# check if we need to minify js files
				if should_minify and '.min.' not in file:
					with open(self.__js_path+file, 'r') as f:
						min_name = file.replace('.js', '.min.js')

						with open(self.__dist_js_path+file, 'w') as min_f:
							min_f.write(jsmin(f.read()))
				else:
					# copy js files over to the dist directory
					shutil.copy(self.__js_path+file, self.__dist_js_path+file)


	def __parse_value(self, injection_str, containers):
		''' pare the value from the injection string '''
		parsed = injection_str.replace(containers[0],'').replace(containers[1],'').strip()

		if '[[' in containers and ']]' in containers:
			return Settings.get_instance().prop(parsed)
		elif '{{' in containers and '}}' in containers:
			return Injection.get_instance().exec_inj(parsed)


	def __render_component(self, component_str):
		''' gets the rendered html of a specific component '''
		split_attr = component_str.replace('<pfcomponent','').replace('/>','').strip()
		attrs = {}

		# break apart the component's attributes
		for attr in split_attr:
			split = split_attr.split('=')
			attrs[split[0].strip()] = split[1].replace('"','').strip()

		# 
		return_str = ''
		if 'name' in attrs:
			with open(f'{self.__components_path}{attrs["name"]}.html', 'r') as f:
				for line in f:
					return_str += self.__manage_component(line)

		return return_str


	def __render_pages(self, pages):
		''' gets the rendered html of each page and saves each file in dist '''
		for page in pages:
			new_html = ''

			#  manage page name details for page_meta
			page_name = page.split('.')[0]
			if Settings.get_instance().has_prop(f'page_meta.{page_name}'):
				self.__page_name = page_name

			# loop through the page and look for components to render
			with open(self.__pages_path + page) as f:
				for line in f:
					new_html += self.__manage_component(line)

			with open(f'{self.__dist_dir}{page}', 'w') as f:
				f.write(new_html)


	def __manage_component(self, line):
		''' checks if the line contains a pfcomponent and replaces it with the component's html '''
		line = self.__manage_injection(line)
		component_name = '<pfcomponent'

		if component_name in line:
			# indentation = 
			start = line.find(component_name)
			end = line.find('/>', start+len(component_name))+2

			component_str = line[start:end]
			line = line.replace(component_str, self.__render_component(component_str))

		return line


	def __manage_injection(self, line):
		''' checks if the line contains injected code and renders it '''
		while '[[' in line and ']]' in line:
			start = line.find('[[')
			end = line.find(']]')+2
			
			# add the current page to the page_meta
			line_replacement = line[start:end]
			injection_str = line_replacement.replace('page_meta', f'page_meta.{self.__page_name}')
			line = line.replace(line_replacement, str(self.__parse_value(injection_str, ('[[',']]'))))

		while '{{' in line and '}}' in line:
			start = line.find('{{')
			end = line.find('}}')+2

			injection_str = line[start:end]
			line = line.replace(injection_str, str(self.__parse_value(injection_str, ('{{','}}'))))

		return line
