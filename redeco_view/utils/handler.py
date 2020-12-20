"""
Este modulo se encarga de manejar las acciones
cuando un archivo es creado acorde a su extension.
"""
from watchdog.events import PatternMatchingEventHandler
class Handler(PatternMatchingEventHandler):
    """
    Clase manejadora de eventos de PatternMatching
    """
    def __init__(self, app, pattern):
        self.app = app
        PatternMatchingEventHandler.__init__(self, patterns=pattern,
                                             ignore_directories=True,
                                             case_sensitive=False
                                            )

    def on_created(self, event):
        self.app.notify(event)

    def on_modified(self, event):
        self.app.notify(event)

    def on_deleted(self, event):
        self.app.notify(event)

    def on_any_event(self, event):
        self.app.notify(event)
