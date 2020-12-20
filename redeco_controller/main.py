# pylint: disable=superfluous-parens,old-style-class,broad-except
# pylint: disable=wrong-import-position,useless-else-on-loop
"""
Modulo encargado de ejecutar la interfaz grafica
y el Core del software por separado, generando
dos procesos independientes.
"""
from os import path, sys, kill, getpid
import subprocess
from time import sleep
from watchdog.observers import Observer
# It's necessary to add the current path to the entry path to help the import process
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from redeco_core import UserConfig, FileActions
from redeco_view import Handler
class AppController():
    """
    Se encarga de ejecutar los procesos para
    la GUI y el core de manera independiente,
    acorde al archivo de configuracion.
    """
    def __init__(self, main_path, user_conf, file_action):
        self._main_path = main_path
        self.user_conf = user_conf
        self.file_action = file_action
        self.is_active = True
        self.view = None
        self.core = None

    def run(self):
        """
        Metodo que inicia una o ambas aplicaciones
        dependiendo de la configuracion definida en
        'user.config.json'
        """
        self.set_executables()
        windows_displayed = self.user_conf.get_visible()
        confirm_msg = self.user_conf.get_confirm_msg()
        # windows_displayed puede tener 3 posibles valores.
        # 2 = No mostar intefaz.
        # 3 = Mostrar solo entrada/salida de datos.
        # 4 = Mostrar entrada/salida de datos y configuracion.
        if(windows_displayed in [3, 4]):
            # Si se muestra la interfaz grafica y no esta habilitado
            # el boton de confirmar mensaje, entonces se inician ambas apps
            if not(confirm_msg):
                self.execute_apps("both")
            # Si se muestra la interfaz grafica y esta habilitado
            # el boton de confirmar mensaje, entonces se inicia la vista
            # y se inicia un observador que esta a la escucha del evento
            # "Confirmar mensaje" para dar inicio al 'core'
            else:
                self.execute_apps("view")
                self.run_observer()
        # Si windows_displayed es 2 u otro valor diferente a 3 y 4
        # entonces solo se inicia el 'core'
        else:
            self.execute_apps("core")

    def set_executables(self):
        """
        Asigna las rutas donde se encuentran
        los ejecutables, dependiendo del tipo S.O.
        Para windows asigna los ejecutables '.exe'.
        """
        # Si la plataforma es windows, se ejecutaran los '.exe'
        if(sys.platform.startswith("win")):
            self.view = '{}/redeview.exe'.format(self._main_path)
            self.core = '{}/redecore.exe'.format(self._main_path)
        # Si la plataforma es Linux/Unix se iniciaran los correspondientes
        else:
            self.view = '{}/./redeview'.format(self._main_path)
            self.core = '{}/./redecore'.format(self._main_path)


    def execute_apps(self, throw_app):
        """
        Ejecuta el proceso para una aplicacion
        dependiendo del argumento 'throw_app'.
        """
        # Ejecuta ambas aplicaciones en procesos separados
        # Se duerme el software 1seg para evitar conflictos
        if(throw_app == 'both'):
            subprocess.Popen(self.view)
            sleep(1)
            subprocess.Popen(self.core)
        # Solo ejecuta el core en un proceso independiente
        elif(throw_app == 'core'):
            subprocess.Popen(self.core)
        # Solo ejecuta la vista en un proceso independiente
        elif(throw_app == 'view'):
            subprocess.Popen(self.view)

    def notify(self, event):
        """
        AppController se mantiene a la escucha
        de eventos generados por la GUI.
        Por lo que este metodo se encarga, de
        eliminar el proceso existente o cancelar la
        escucha de eventos creada en run_observer()
        para posteriormente iniciar el core de la app.
        """
        filename = path.split(event.src_path)[1]
        # El archivo es generado al cerrar la GUI
        # Se mata todo proceso del software si el archivo es 'kill_process.helper'
        if(filename == "kill_process.helper"):
            self.is_active = False
            kill(getpid(), 9)
        # El archivo es generado cuando se da clic en 'Confirmar mensaje'
        # Se ejecuta el 'core' si el archivo es 'redeco.helper'
        elif(filename == "redeco.helper"):
            self.is_active = False
            self.execute_apps("core")

    def run_observer(self):
        """
        Inicia un proceso que se mantiene a la escucha
        de archivos con la extension '.helper'.
        """
        handler = Handler(self, ["*.helper"])
        observer = Observer()
        observer.schedule(handler, self._main_path, recursive=True)
        observer.start()
        # Se mantiene observando los archivos que se generan,
        # hasta que es cancelado en notify()
        while self.is_active:
            sleep(1)
        else:
            observer.stop()

if __name__ == "__main__":
    USER_CONF = None
    try:
        CURRENT_PATH = path.dirname(path.abspath(__file__))
        FILE_ACTION = FileActions(CURRENT_PATH)
        USER_CONF = UserConfig(FILE_ACTION.get_user_config_json())
        FILE_ACTION.get_input_data(USER_CONF.get_input_file_name())
        APP_CTRL = AppController(CURRENT_PATH, USER_CONF, FILE_ACTION)
        APP_CTRL.run()
    except (ValueError, Exception) as error:
        ERROR = str(error)
        if(USER_CONF):
            FILE_ACTION.write_output_data(ERROR, USER_CONF.get_output_file_name())
        else:
            FILE_ACTION.write_output_data(ERROR)
        sys.exit()
