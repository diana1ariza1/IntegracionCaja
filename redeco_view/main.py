# pylint: disable=superfluous-parens,wrong-import-position,no-self-use,broad-except
# pylint: disable=too-many-instance-attributes
"""
    Modulo encargado de construir la interfaz grafica
    que sera mostrada al usuario de acuerdo a la configuracion
    deifnida.
"""
from os import sys, path, remove
from Tkinter import Label, Frame, PhotoImage, Tk, Button
from collections import OrderedDict
from Queue import Queue
from watchdog.observers import Observer
# It's necessary to add the current path to the entry path to help the import process
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from redeco_core import UserConfig, FileActions, BusinessConfig
from redeco_core import MessageBuilding, MessageReading, CommnController
from redeco_core.utils.logger import get_error_log, activate_logs
from redeco_view import Handler

# DEVELOPER PATH
# CURRENT_PATH = path.dirname(path.dirname(path.abspath(__file__)))
# PRODUCTION PATH
CURRENT_PATH = path.dirname(path.abspath(__file__))

class ApplicationGUI(Tk):
    """
    Clase que posee todos los metodos
    que construye el componente necesario
    acorde a la configuracion
    """
    def __init__(self, main_path, **kwargs):
        self._error_log = get_error_log()
        self._main_path = main_path
        self.controller = kwargs.get('controller')
        self.business_conf = kwargs.get('business_conf')
        self.user_conf = kwargs.get('user_conf')
        self.file_action = kwargs.get('file_action')
        self.queue = Queue()
        self._data_frame = None
        self._msg_frame = None
        Tk.__init__(self)

    def run(self,):
        """
        Configura e inicializa todo
        para mostrar la interfaz
        """

        if(sys.platform.startswith('win')):
            self.iconbitmap("{}/favicon.ico".format(path.join(self._main_path, "assets")))
        else:
            icon = PhotoImage(file='{}/favicon.gif'.format(path.join(self._main_path, "assets")))
            self.call('wm', 'iconphoto', self._w, icon)

        self.title("Redeban Multicolor")
        self.config(width=450, height=500)
        self.resizable(False, False)
        self.config(bg="#fff")
        self.create_banner()
        is_visible = self.user_conf.get_visible()
        labels = self.get_input_data()
        title = "Entrada de Datos"
        if(is_visible == 3):
            self.data_frame(title, labels)
        elif(is_visible == 4):
            self.data_frame(title, labels)
            self.info_frame()
        self.create_button()
        self.run_observer()
        # llama al metodo on_close() al cerrar la GUI
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        # metodo de tkinter para inicializar la ventana
        self.mainloop()


    def get_principal_colors(self):
        """
        Funcion simple que retorna los valores
        de los calores principales de la interfaz.
        """
        bg_color = "#102030"
        fg_color = "#ffffff"
        return bg_color, fg_color

    def get_label_settings(self):
        """
        Metodo genera las las configuraciones
        de los para las etiquetas "Label", las cuales
        se usan para mostrar en pantalla los campos.
        """
        # Configuracion de los titulos.
        bg_color, fg_color = self.get_principal_colors()
        label_conf = dict(bg=bg_color, fg=fg_color)
        label_conf.update(anchor="e", relief="ridge")
        grid_conf = dict(row=1, column=0, sticky="WE", pady=(0, 0))

        # Configuracion del valor asociado a cada titulo.
        value_conf = dict(bg=bg_color, fg=fg_color)
        grid_conf_value = dict(row=1, column=1, sticky="WN", pady=(0, 0), padx=(2, 0))
        return label_conf, grid_conf, value_conf, grid_conf_value

    def create_banner(self):
        """
        Metodo utilizado para mostrar
        el banner de la compania.
        """
        banner_frame = Frame()
        banner_frame.grid(row=0, column=0, columnspan=2)
        temp_image = PhotoImage(file="{}/rbm.gif".format(path.join(self._main_path, "assets")))
        img_label = Label(banner_frame, image=temp_image, bg="#fff")
        img_label.image = temp_image
        img_label.pack()

    def create_button(self):
        """
        Metodo que crea el boton
        que es utilizado para confirmar
        el mensaje.
        """
        bg_color, fg_color = self.get_principal_colors()
        if(self.user_conf.get_confirm_msg()):
            button_frame = Frame()
            button_frame.grid(row=4, column=0, columnspan=2, pady=(0, 5))
            button = Button(button_frame,
                            text="Confirmar mensaje", command=self.callback)
            button.config(bg=bg_color, fg=fg_color)
            button.pack()

    def info_frame(self):
        """
        Metodo que construye el componente
        en la interfaz para mostrar las
        configuraciones de usuario.
        """
        bg_color, fg_color = self.get_principal_colors()
        label_conf, grid_conf, value_conf, grid_conf_value = self.get_label_settings()
        info_frame = Frame(bg=bg_color, bd=5, relief="ridge")
        info_frame.grid(row=1, column=0, columnspan=1, sticky="ne", padx=5, pady=(0, 5))

        user_settings = Label(info_frame, text="Configuraciones del Usuario")
        user_settings.grid(row=0, column=0, columnspan=2, sticky="N")
        user_settings.config(font=("", 12), bd=2, relief="ridge", bg=bg_color)
        user_settings.config(fg=fg_color, padx=8, width=25)
        labels = self.built_config_labels()

        for index, (label, value) in enumerate(labels.iteritems()):
            grid_conf["row"] = index+1
            grid_conf_value["row"] = index+1
            self.built_label(info_frame, label, label_conf, grid_conf)
            self.built_label(info_frame, value, value_conf, grid_conf_value)

    def data_frame(self, title, labels):
        """
        Metodo que construye el componente
        en la interfaz para mostrar los datos
        de entrada.
        """
        bg_color, fg_color = self.get_principal_colors()
        label_conf, grid_conf, value_conf, grid_conf_value = self.get_label_settings()
        self._data_frame = Frame(bg=bg_color, bd=5, relief="ridge")
        self._data_frame.grid(row=2, column=0, columnspan=1, sticky="ne", padx=5, pady=(0, 5))

        data_title = Label(self._data_frame, text=title)
        data_title.grid(row=0, column=0, columnspan=2, sticky="N")
        data_title.config(font=("", 12), bd=2, relief="ridge", bg=bg_color)
        data_title.config(fg=fg_color, padx=8, width=25)

        for index, (label, value) in enumerate(labels.iteritems()):
            grid_conf["row"] = index+1
            grid_conf_value["row"] = index+1
            self.built_label(self._data_frame, label, label_conf, grid_conf)
            self.built_label(self._data_frame, value, value_conf, grid_conf_value)

    def response_frame(self, labels):
        """
        Metodo que construye el componente
        en la interfaz para mostrar los datos
        de salida.
        """
        bg_color, fg_color = self.get_principal_colors()
        label_conf, grid_conf, value_conf, grid_conf_value = self.get_label_settings()
        self._msg_frame = Frame(bg=bg_color, bd=5, relief="ridge")
        self._msg_frame.grid(row=3, column=0, columnspan=3, sticky="n", padx=5, pady=(0, 5))

        data_title = Label(self._msg_frame, text="Mensaje")
        data_title.grid(row=0, column=0, columnspan=3, sticky="N")
        data_title.config(font=("", 12), bd=2, bg=bg_color)
        data_title.config(fg=fg_color, padx=8, width=25)

        for index, (label, value) in enumerate(labels.iteritems()):
            grid_conf["row"] = index+1
            grid_conf_value["row"] = index+1
            label_conf_copy = label_conf.copy()
            label_conf_copy.update(relief=None)
            label_conf_copy.update(anchor='e')
            value_conf_copy = value_conf.copy()
            value_conf_copy.update(anchor='w')
            self.built_label(self._msg_frame, label, label_conf_copy, grid_conf)
            self.built_label(self._msg_frame, value, value_conf_copy, grid_conf_value)

    def built_label(self, frame, label_name, label_conf, grid_conf):
        """
        Funcion generica que se encarga
        de construir todas las etiquetas
        con su valor correspondiente.
        """
        label = Label(frame, text=label_name)
        label.grid(**grid_conf)
        label.config(**label_conf)

    def built_config_labels(self):
        """
        Construye el componente de la ventana
        que muestra las configuraciones de
        usuario.
        """
        conn_conf = self.user_conf.get_connection_config()
        baudrate = conn_conf.get('baudrate')
        parity = conn_conf.get('parity')
        bytesize = conn_conf.get('bytesize')
        stopbits = conn_conf.get('stopbits')
        conf_conex = (baudrate, parity, bytesize, stopbits)
        labels = OrderedDict()
        labels["Cajero:"] = "ACTIVADO" if self.user_conf.get_cashier_flag() else "DESACTIVADO"
        labels["Puerto:"] = conn_conf.get('port')
        labels["Conf. Conexion:"] = ",".join(str(v) for v in conf_conex)
        labels["Time Out:"] = str(conn_conf.get('timeout'))+" seg"
        labels["Time Sleep:"] = str(self.user_conf.get_sleep_time())+" seg"
        labels["Descuento BIN:"] = "ACTIVADO" if self.user_conf.get_previa() else "DESACTIVADO"
        return labels

    def get_input_data(self):
        """
        Obtiene los valores generados en
        el archivo de entrada, para luego
        mostrarlos en la interfaz.
        """
        input_filename = self.user_conf.get_input_file_name()
        data = self.file_action.get_input_data(input_filename)
        data_builds = dict(self.controller.built_fields(data))
        fields = [field for field, _ in data_builds.iteritems()]
        fields = self.business_conf.get_fields(fields)
        fields = dict(fields)
        temp_fields = dict()
        for (field, field_def) in fields.iteritems():
            if(field_def["data_type"] == "N"):
                try:
                    temp_fields[field_def["label"]] = float(data_builds[field])
                except ValueError as error:
                    value = str(error).split(" ")[-1]
                    msg = "99, Error al convertir a float el valor {}".format(value)
                    if(self._error_log):
                        self._error_log.error(msg)
                    raise Exception(msg)
            else:
                temp_fields[field_def["label"]] = data_builds[field]
        return temp_fields

    def get_output_data(self):
        """
        Obtiene los valores generados en
        el archivo de salida, para luego
        mostrarlos en la interfaz.
        """
        output_filename = self.user_conf.get_output_file_name()
        data = self.file_action.get_output_data(output_filename)
        ouput_fields = self.user_conf.get_selected_fields()
        result = None
        if not(len(data) == len(ouput_fields)):
            if(data[0] != '99'):
                result = {'Tarjeta:': data}, True
            else:
                result = {'Error:': ','.join(data)}, True
        else:
            fields = self.business_conf.get_fields_definition()
            fields = {
                field_def["description"]:field_def["label"]
                for _, field_def in fields.iteritems()
            }
            ouput_fields = [fields[field] for field in ouput_fields]
            response = OrderedDict(zip(ouput_fields, data))
            result = response, False

        return result

    def event_handler(self, _):
        """
        Manejador de eventos, modifica o no
        los valores de la interfaz grafica cuando
        un archivo de entrada o salida es manipulado.
        """
        input_filename = self.user_conf.get_input_file_name()
        output_filename = self.user_conf.get_output_file_name()
        event = self.queue.get()
        filename = path.split(event.src_path)[1]
        if(event.event_type == "moved"):
            filename = path.split(event.dest_path)[1]

        if(filename == output_filename and event.event_type != 'deleted'):
            labels, is_msg = self.get_output_data()
            if (is_msg):
                if(getattr(self, "_msg_frame", None)):
                    self._msg_frame.destroy()
                self.response_frame(labels)
            else:
                self._data_frame.destroy()
                if(getattr(self, "_msg_frame", None)):
                    self._msg_frame.destroy()
                title = "Salida de Datos"
                self.data_frame(title, labels)
        elif(filename == input_filename and event.event_type != 'deleted'):
            self._data_frame.destroy()
            labels = self.get_input_data()
            title = "Entrada de Datos"
            self.data_frame(title, labels)

    def run_observer(self):
        """
        Metodo que se encarga de iniciar un hilo
        que esta a la escucha de los archivos de
        entrada y salida.
        """
        handler = Handler(self, ["*.txt"])
        observer = Observer()
        observer.schedule(handler, self._main_path, recursive=True)
        observer.start()
        self.bind("<<WatchdogEvent>>", self.event_handler)

    def notify(self, event):
        """Eventos recibidos desde el Handler"""
        self.queue.put(event)
        self.event_generate("<<WatchdogEvent>>", when="tail")

    def on_close(self):
        """
        Indica que la ventana fue cerrada
        para escribir un archivo para que
        el controlador que cierre todo subproceso
        existente.
        """
        self.callback("kill_process")
        self.destroy()

    def callback(self, filename="redeco"):
        """
        Crea un archivo dependiendo del caso
            * Confirmar
            * Cerrar todo
        Ese archivo le indica al controlador
        que accion realizar
        """
        filename = "{}.helper".format(filename)
        open(filename, 'w').close()
        if(path.exists(filename)):
            remove(filename)

def initialize():
    """
    Inicializa todas las instancias
    necesarias para la construccion
    de la interfaz
    """
    user_conf = None
    try:
        file_action = FileActions(CURRENT_PATH)
        user_conf = UserConfig(file_action.get_user_config_json())
        active_log_flags = user_conf.get_logs_flag()
        activate_logs(*active_log_flags)
        is_visible = user_conf.get_visible()
        if(is_visible != 2):
            business_conf = BusinessConfig(file_action.get_business_config_json())
            message_bldg = MessageBuilding(business_conf)
            message_rdg = MessageReading(business_conf, message_bldg)
            kwargs = dict(message_rdg=message_rdg, business_conf=business_conf)
            kwargs.update(message_bldg=message_bldg, user_conf=user_conf)
            kwargs.update(file_action=file_action)
            controller = CommnController(**kwargs)
            kwargs.update(controller=controller)
            app_gui = ApplicationGUI(CURRENT_PATH, **kwargs)
            app_gui.run()
    except Exception as error:
        if(app_gui):
            app_gui.on_close()
        error = str(error)
        if(user_conf):
            file_action.write_output_data(error, user_conf.get_output_file_name())
        else:
            file_action.write_output_data(error)
        sys.exit()


if __name__ == "__main__":
    initialize()
