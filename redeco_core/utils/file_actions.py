# pylint: disable=superfluous-parens,old-style-class,relative-import,no-self-use
"""Modulo para manejar todas las acciones referente
a un archivo"""
import json
from os import path, remove
from codecs import open as copen
from logger import get_error_log

class FileActions:
    """
    Clase para leer los archivos de configuracion, entrada
    de datos. Del mismo modo para escribir el archivo
    para la salida de datos.
    """
    def __init__(self, main_path):
        self._business_conf_file_path = path.join(main_path, 'business.config.json')
        self._user_conf_file_path = path.join(main_path, 'user.config.json')
        self.error_log = get_error_log()

    def get_user_config_json(self):
        """Obtiene las configuraciones de usuario definidas"""
        try:
            with open(name=self._user_conf_file_path, mode='r') as file_temp:
                return json.loads(file_temp.read())
        except IOError as error:
            file_name = str(error).split("'")[1]
            msg = "99, No se pudo abrir de la siguiente ruta: {}".format(file_name)
            if(self.error_log):
                self.error_log.error(msg)
            raise Exception(msg)
        except Exception as error:
            msg = "Error en user.config.json -> {}".format(str(error))
            if(self.error_log):
                self.error_log.error(msg)
            raise Exception(msg)

    def get_business_config_json(self):
        """Obtiene las configuraciones del negocio definidas"""
        try:
            with open(name=self._business_conf_file_path, mode='r') as file_temp:
                return  json.loads(file_temp.read())
        except IOError as error:
            file_name = str(error).split("'")[1]
            msg = "99, No se pudo abrir de la siguiente ruta: {}".format(file_name)
            if(self.error_log):
                self.error_log.error(msg)
            raise Exception(msg)
        except Exception as error:
            msg = "Error en business.config.json -> {}".format(str(error))
            if(self.error_log):
                self.error_log.error(msg)
            raise Exception(msg)

    def get_input_data(self, filename):
        """Obtiene los datos de entrada, datos necesarios
        para realizar una operacion."""
        try:
            with open(name=filename, mode='r') as file_temp:
                data = file_temp.read().split(',')
            return data
        except IOError as error:
            file_name = str(error).split(" ")[-1]
            err_msg = "99, No se pudo abrir el archivo {}".format(file_name)
            if(self.error_log):
                self.error_log.error(err_msg)
            raise Exception(err_msg)

    def get_output_data(self, filename):
        """Utilizado por redeco_view para mostrar los datos
        despues cuando termine la transaccion."""
        with open(name=filename, mode='r') as file_temp:
            data = file_temp.read().split(',')
        return data

    def write_output_data(self, data, filename="error.txt"):
        """Escribe la respuesta de una transaccion.
        Si no hay un nombre para el archivo de salida, por defecto
        el nombre del archivo sera error.txt """
        with copen(filename, mode="w", encoding="utf-8") as file_temp:
            file_temp.write(data)


    def delete_files(self, user_conf):
        """
        Elimina los archivos entrada y salida de datos
        dependiendo de la configuracion. Si previa (Descuento BIN)
        esta activado, el archivo entrada sera eliminado.
        """
        previa_activated = user_conf.get_previa()
        rm_files_activated = user_conf.get_delete_files_flag()
        input_file_name = user_conf.get_input_file_name()
        output_file_name = user_conf.get_output_file_name()
        try:
            if(rm_files_activated == 0):
                remove(input_file_name)
                remove(output_file_name)
            elif(rm_files_activated == 1 or previa_activated):
                remove(input_file_name)

        except OSError as error:
            file_name = str(error).split(" ")[-1]
            err_msg = "99, No se pudo eliminar el archivo {}".format(file_name)
            if(self.error_log):
                self.error_log.error(err_msg)
            raise Exception(err_msg)
