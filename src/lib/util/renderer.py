import errno
import os
import re
import sass
import shutil
from cssmin import cssmin
from jsmin import jsmin
from src.lib.util.injection import *
from src.lib.util.logger import *
from src.lib.util.settings import *


class Renderer:

    def __init__(self):
        settings = Settings.get_instance()
        cwd = os.getcwd()
        sep = os.sep

        self.__page_name        = 'default';
        self.__components_path  = cwd + settings.render_path(settings.prop('app_settings.components_dir')) + sep
        self.__content_path     = cwd + settings.render_path(settings.prop('app_settings.content_dir')) + sep
        self.__css_path         = cwd + settings.render_path(settings.prop('app_settings.css_dir')) + sep
        self.__dist_dir         = cwd + settings.render_path(settings.prop('app_settings.dist_dir')) + sep
        self.__dist_css_path    = cwd + settings.render_path(settings.prop('app_settings.compiled_css_dir')) + sep
        self.__dist_js_path     = cwd + settings.render_path(settings.prop('app_settings.compiled_js_dir')) + sep
        self.__js_path          = cwd + settings.render_path(settings.prop('app_settings.js_dir')) + sep
        self.__pages_path       = cwd + settings.render_path(settings.prop('app_settings.pages_dir')) + sep
        self.__scss_path        = cwd + settings.render_path(settings.prop('app_settings.scss_dir')) + sep


    def render(self):
        ''' begins the rendering process '''
        directories = []
        pages = []
        for file in os.listdir(self.__pages_path):
            if os.path.isfile(f'{self.__pages_path}{file}') and '.html' in file:
                pages.append(file)
            elif os.path.isdir(f'{self.__pages_path}{file}'):
                # todo: move into the directory
                pass

        self.__render_pages(pages)
        self.__render_js()

        settings = Settings.get_instance()
        if settings.use_scss():
            self.__render_scss()
        else:
            self.__render_css()

        # create general symlinks
        if settings.prop('app_settings.use_symlinks'):
            self.__generate_symlinks()


    def __render_scss(self):
        ''' compiles main.scss to main.css in dist  '''
        sass.compile(dirname=(self.__scss_path, self.__dist_css_path), output_style='compressed')


    # TODO: combine js and css renderers (DRY)
    def __render_css(self):
        ''' writes css files to dist '''
        should_minify = Settings.get_instance().minify_css()
        self.__js_css_render(should_minify, self.__css_path, self.__dist_css_path, '.css')


    def __render_js(self):
        ''' writes js files to dist '''
        should_minify = Settings.get_instance().minify_js()
        self.__js_css_render(should_minify, self.__js_path, self.__dist_js_path, '.js')


    def __js_css_render(self, should_minify, path, dist_path, extension):
        ''' . '''
        for file in os.listdir(path):
            # 
            if os.path.isfile(path+file) and file.endswith(extension):
                # 
                if should_minify and '.min.' not in file:
                    with open(path+file, 'r') as f:
                        min_name = file.replace(extension, '.min'+extension)

                        with self.__write_file_path(dist_path+min_name) as min_f:
                            if extension == '.js':
                                min_f.write(jsmin(f.read()))
                            elif extension == '.css':
                                min_f.write(cssmin(f.read()))
                else:
                    # 
                    shutil.copy(path+file, dist_path+file)
            elif os.path.isdir(path+file):
                if Settings.get_instance().prop('app_settings.use_symlinks'):
                    try:
                        # create symlink of the directory
                        os.symlink(path+file, dist_path+file)
                    except Exception as e:
                        pass # the symlink already exists


    def __generate_symlinks(self):
        ''' . '''
        cwd = os.getcwd()
        settings = Settings.get_instance()
        links = {}

        # images
        images_path = cwd + settings.render_path(settings.prop('app_settings.images_dir'))
        images_dist = cwd + settings.render_path(settings.prop('app_settings.compiled_images_dir'))
        links[images_path] = images_dist

        # loop through the links and attempt to create them if they don't already exist
        for src,dest in links.items():
            try:
                os.symlink(src, dest)
            except Exception as e:
                pass # the symlink already exists


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

            # add loop class
            if 'class' in attrs:
                attrs['class'] += f' {children_name} parent'
            else:
                attrs['class'] = f'{children_name}'

            # build the container for the looped elements
            return_html = '<div '
            for attr in attrs:
                if not attr == 'pfFor':
                    return_html += f'{attr}="{attrs[attr]}"'
            return_html += '>'

            # grab the children json
            with open(f'{self.__content_path}{children_name}.json', 'r') as f:
                try:
                    content_json = json.loads(f.read())
                except Exception as e:
                    raise Exception(f'Malformed JSON in {children_name}.json: {e}')

            # start writing out the children
            with open(f'{self.__components_path}{children_name}.html', 'r') as f:
                for child in content_json['children']:
                    # reset the read head
                    f.seek(0)

                    # build the child's container
                    return_html += f'<div class="{children_name} child">'

                    # loop through each line in the child html
                    for line in f.readlines():
                        # check for injection
                        if not '((' in line and not '))' in line:
                            return_html += line
                        else:
                            while '((' in line and '))' in line:
                                start = line.find('((')
                                end = line.find('))')+2
                                attr_inj = line[start:end]

                                try:
                                    content_attr = child[re.sub(r'\(\(|\)\)', '', attr_inj).strip()]
                                    line = line.replace(attr_inj, content_attr)
                                except Exception as e:
                                    Logger.error(f'\t\tmissing content attribute from {children_name}.json: {e}')
                                    line = line.replace(attr_inj, re.sub(r'\(\(|\)\)', '**ERROR**', attr_inj))

                                # print(f'line: {line}')
                                return_html += line

                    return_html += '</div>'
            # close the outer container div
            return return_html + '</div>'
        except Exception as e:
            Logger.error(f'\t\tError rendering children for {attrs["pfFor"]} component. {e}')
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
            with open(self.__pages_path + page, 'r') as f:
                for line in f:
                    new_html += self.__manage_component(line)

            with self.__write_file_path(f'{self.__dist_dir}{page}') as f:
                f.write(new_html)

            Logger.info('\t\t-- Done --')
        Logger.info('')


    def __manage_component(self, line):
        ''' checks if the line contains a pfcomponent and replaces it with the component's html '''
        line = self.__manage_injection(line)
        component_name = '<pfcomponent'

        if component_name in line:
            if '/>' in line:
                start = line.find(component_name)
                end = line.find('/>', start+len(component_name))+2

                component_str = line[start:end]
                line = line.replace(component_str, self.__render_component(component_str))
            else:
                Logger.error(f'\t\tMissing tag terminator ("/>"): {line.strip()}')
                line = ''
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


    def mkdir_p(self, path):
        ''' . '''
        try:
            os.makedirs(path)
        except OSError as o:
            if os.path.isdir(path) and o.errno == errno.EEXIST:
                pass
            else:
                raise


    def __write_file_path(self, path):
        ''' . '''
        self.mkdir_p(os.path.dirname(path))
        return open(path, 'w')
