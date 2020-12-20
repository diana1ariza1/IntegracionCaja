# pylint: disable=superfluous-parens,broad-except,global-statement,relative-import
"""
    Modulo controllador orientado a delegar acciones especificas
    a los demas modulos, encargandose unicamente del paso de
    informacion y/o dependencias necesarias para cada una de las funcionalidades.
"""

from os import path, sys
from serial import SerialException
from utils import BusinessConfig, UserConfig, Connection, MessageBuilding
from utils import MessageReading, FileActions, CommnController
from utils.logger import activate_logs

# DEVELOPER PATH
# CURRENT_PATH = path.dirname(path.dirname(path.abspath(__file__)))
# PRODUCTION PATH
CURRENT_PATH = path.dirname(path.abspath(__file__))

FILE_ACTION = None
USER_CONF = None
BUSINESS_CONF = None
MESSAGE_BLDG = None
MESSAGE_RDG = None
CONNECTION = None
CONTROLLER = None

def run():
    """
    Encargada de obtener los datos de
    entrada y pasarselos al controlador
    para que inicia la comunicacion
    con el datafono.
    """
    # Se valida que el puerto este abierto
    if(CONNECTION.is_open()):
        try:
            # Se los datos de entrada generados por la caja a partir del archivo
            data = FILE_ACTION.get_input_data(USER_CONF.get_input_file_name())
            FILE_ACTION.delete_files(USER_CONF)
            response = CONTROLLER.initializer(CONNECTION, data)
            output_data = USER_CONF.get_output_data(response, BUSINESS_CONF)
            FILE_ACTION.write_output_data(output_data, USER_CONF.get_output_file_name())
        except Exception as error:
            error = str(error)
            FILE_ACTION.write_output_data(error, USER_CONF.get_output_file_name())

        CONNECTION.close()

def instance_class():
    """
    Instancia todas las clases necesarias
    para leer la configuracion de usuario,
    configuracion de negocio, el tipo de conexion.
    Del mismo modo, para leer y construir un mensaje
    """
    global FILE_ACTION
    global USER_CONF
    global BUSINESS_CONF
    global MESSAGE_BLDG
    global MESSAGE_RDG
    global CONNECTION
    global CONTROLLER

    try:
        FILE_ACTION = FileActions(CURRENT_PATH)
        USER_CONF = UserConfig(FILE_ACTION.get_user_config_json())
        active_log_flags = USER_CONF.get_logs_flag()
        activate_logs(*active_log_flags)
        BUSINESS_CONF = BusinessConfig(FILE_ACTION.get_business_config_json())
        MESSAGE_BLDG = MessageBuilding(BUSINESS_CONF)
        MESSAGE_RDG = MessageReading(BUSINESS_CONF, MESSAGE_BLDG)

        kwargs = dict(message_rdg=MESSAGE_RDG, business_conf=BUSINESS_CONF)
        kwargs.update(message_bldg=MESSAGE_BLDG, user_conf=USER_CONF)
        kwargs.update(file_action=FILE_ACTION)
        CONTROLLER = CommnController(**kwargs)
        CONNECTION = Connection(USER_CONF)
    except (SerialException, ValueError, Exception) as error:
        error = str(error)
        if(USER_CONF):
            FILE_ACTION.write_output_data(error, USER_CONF.get_output_file_name())
        else:
            FILE_ACTION.write_output_data(error)
        sys.exit()

if (__name__ == '__main__'):
    instance_class()
    run()
