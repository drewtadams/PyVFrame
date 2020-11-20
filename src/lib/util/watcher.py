import sys
import src.lib.util.renderer as r
import time
from src.lib.util.logger import *
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class Watcher:
    ''' class that watches for file changes '''


    @staticmethod
    def watch():
        ''' watches the files specified in settings.json '''
        settings = Settings.get_instance()
        prop = 'app_settings.watch'
        watch_files = settings.prop(prop)

        if len(watch_files) == 0 or watch_files == prop:
            Logger.warning('\n\tNo files to watch - please update your settings.json file\n')
        else:
            handler = Watcher.WatchHandler()
            observer = Observer()

            Logger.data('\n\tWatching files:')
            for file in watch_files:
                path = settings.render_path(file)
                Logger.data(f'\t    {path}')
                observer.schedule(handler, path=f'.{path}', recursive=True)

            observer.start()
            print('')
            
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                observer.stop()
            observer.join()
            

    class WatchHandler(FileSystemEventHandler): 
        def on_modified(self, event):
            Logger.data(f'\tChange detected in {event.src_path}')
            r.Renderer().render()

