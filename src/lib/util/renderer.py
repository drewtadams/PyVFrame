import os
import re
import sass
import shutil
from jsmin import jsmin
from src.lib.util.injection import *
from src.lib.util.logger import *
from src.lib.util.settings import *


class Renderer:

	def __init__(self):
		cwd = os.getcwd()
		sep = os.sep
		dist_path = Settings.get_instance().dist_dir().replace('/', sep)
		dist = f'{cwd}{sep}{dist_path}{sep}'
		build = f'{cwd}{sep}build{sep}'

		self.__page_name		= 'default';
		self.__components_path	= f'{build}components{sep}'
		self.__content_path		= f'{build}content{sep}'
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
		if Settings.use_scss():
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
			# handle page_meta defaulting
			split_parsed = parsed.split('.')
			if split_parsed[0] == 'page_meta' and not Settings.get_instance().has_prop(parsed):
				Logger.warning(f'\t\tUsing default attributes for property: {parsed}')
				split_parsed[1] = 'default'
				
				parsed = ''
				for i in range(len(split_parsed)):
					parsed += f'{"." if i > 0 else ""}{split_parsed[i]}'

			return Settings.get_instance().prop(parsed)
		elif '{{' in containers and '}}' in containers:
			return Injection.get_instance().exec_inj(parsed)


	def __render_content(self, content_name, component_html):
		''' gets the rendered html of a specific component with the specified content '''
		try:
			with open(f'{self.__content_path}{content_name}.json', 'r') as f:
				content_json = json.loads(f.read())

				# go through the component's html and inject the appropriate content
				return_html = ''
				for line in component_html.splitlines():
					while '((' in line and '))' in line:
						start = line.find('((')
						end = line.find('))')+2
						attr_inj = line[start:end]

						try:
							content_attr = content_json[re.sub(r'\(\(|\)\)', '', attr_inj).strip()]
							line = line.replace(attr_inj, content_attr)
						except Exception as e:
							Logger.error(f'\t\tmissing content attribute from {content_name}.json: {e}')
							line = line.replace(attr_inj, re.sub(r'\(\(|\)\)', '**ERROR**', attr_inj))
					return_html += line

			return return_html
		except Exception as e:
			Logger.error(e)
			return component_html


	def __render_loop(self, attrs):
		''' gets the rendered html of the specified children component '''
		try:
			children_name = attrs['pfFor']

			# build the container for the looped elements
			return_html = '<div '
			for attr in attrs:
				if not attr == 'pfFor':
					return_html += f'{attr}="{attrs[attr]}"'
			return_html += '>'

			with open(f'{self.__content_path}{children_name}.json', 'r') as f:
				content_json = json.loads(f.read())

				# start looping through the children
				for child in content_json['children']:
					return_html += f'<div class="{children_name} child">'

					# add the values to the html with the class being the key
					for k,v in child.items():
						return_html += f'<span class="{k}">{v}</span>'

					return_html += '</div>'
			return return_html + '</div>'
		except Exception as e:
			Logger.error(e)
			return f'<div>{e}</div>'


	def __render_component(self, component_str):
		''' gets the rendered html of a specific component '''
		split_attr = component_str.replace('<pfcomponent','').replace('/>','').strip().split(' ')
		attrs = {}

		# break apart the component's attributes
		for attr in split_attr:
			split = attr.split('=')
			attrs[split[0].strip()] = split[1].replace('"','').strip()

		# look for general components
		return_str = ''
		if 'name' in attrs:
			with open(f'{self.__components_path}{attrs["name"]}.html', 'r') as f:
				for line in f:
					return_str += self.__manage_component(line)

		# look for content segments
		if 'content' in attrs:
			return self.__render_content(attrs['content'], return_str)

		# look for repeated content segments
		if 'pfFor' in attrs:
			return self.__render_loop(attrs)

		return return_str


	def __render_pages(self, pages):
		''' gets the rendered html of each page and saves each file in dist '''
		for page in pages:
			new_html = ''
			Logger.info(f'\n\tRendering "{page}"')

			#  manage page name details for page_meta
			page_name = page.split('.')[0]
			if Settings.get_instance().has_prop(f'page_meta.{page_name}'):
				self.__page_name = page_name
			else:
				self.__page_name = 'default'

			# loop through the page and look for components to render
			with open(self.__pages_path + page) as f:
				for line in f:
					new_html += self.__manage_component(line)

			with open(f'{self.__dist_dir}{page}', 'w') as f:
				f.write(new_html)

			Logger.info('\t\t-- Done --')
		Logger.info('')


	def __manage_component(self, line):
		''' checks if the line contains a pfcomponent and replaces it with the component's html '''
		line = self.__manage_injection(line)
		component_name = '<pfcomponent'

		if component_name in line:
			start = line.find(component_name)
			end = line.find('/>', start+len(component_name))+2

			component_str = line[start:end]
			line = line.replace(component_str, self.__render_component(component_str))

		return line


	def __manage_injection(self, line, content=''):
		''' checks if the line contains injected code and renders it '''
		while '[[' in line and ']]' in line:
			start = line.find('[[')
			end = line.find(']]')+2
			line_replacement = line[start:end]

			# add the current page to the page_meta if it exists
			injection_str = line_replacement.replace('page_meta', f'page_meta.{self.__page_name}')

			# update the line with the new parsed value
			line = line.replace(line_replacement, str(self.__parse_value(injection_str, ('[[',']]'))))

		while '{{' in line and '}}' in line:
			start = line.find('{{')
			end = line.find('}}')+2

			injection_str = line[start:end]
			line = line.replace(injection_str, str(self.__parse_value(injection_str, ('{{','}}'))))

		return line
