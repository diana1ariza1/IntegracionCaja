# pylint: disable=superfluous-parens,global-statement,broad-except
"""
Modulo usado para registrar los eventos de las transacciones y
errores presentados en la ejecucion del software.
"""
from string import printable
import logging
from binascii import hexlify
from datetime import date
from os import path, mkdir
from getpass import getuser
# Rutas donde se guardaran los archivos logs
ERROR_FORMATTER = logging.Formatter("%(user)s | "
                                    +"%(levelname)s | "
                                    +"%(asctime)s | "
                                    +"%(filename)s | "
                                    +"%(funcName)s | "
                                    +"%(lineno)d | "
                                    +"%(message)s",
                                    datefmt="%Y-%m-%d %H:%M")
TRANSA_FORMATTER = logging.Formatter("%(user)s |"
                                     +"%(levelname)s| "
                                     +"%(asctime)s | "
                                     +"%(who)s \n"
                                     +"%(message)s",
                                     datefmt="%Y-%m-%d %H:%M")
TRANSA_FOLDER = "transaccional_logs"
ERROR_FOLDER = "error_logs"
TRANSA_LOGGER = None
ERROR_LOGGER = None
IS_TRANSA_LOG_ACTIVE = False
IS_ERROR_LOG_ACTIVE = False
PRINTABLE_ASCII = None

def config_error_logger():
    """
    Si esta activado el registro de errores
    en las configuraciones de usuario, se procede a inicializar
    los componentes necesarios.
    """
    error_logger = None
    if (IS_ERROR_LOG_ACTIVE):
        extra_info = {'user': getuser()}
        # Nombre del archivo para el log de errores
        error_log_file = './{}/{}-error.log'.format(ERROR_FOLDER, str(date.today()))
        error_logger = logging.getLogger("error")
        error_handler = logging.FileHandler(error_log_file)
        error_handler.setFormatter(ERROR_FORMATTER)
        error_logger.setLevel(logging.INFO)
        error_logger.addHandler(error_handler)
        error_logger = logging.LoggerAdapter(error_logger, extra_info)
    return error_logger

def config_transactional_logger():
    """
    Si esta activado el registro de transacciones
    en las configuraciones de usuario, se procede a inicializar
    los componentes necesarios.
    """
    transa_logger = None
    if (IS_TRANSA_LOG_ACTIVE):
        # Nombre del archivo para el log de las transacciones
        transa_log_file = './{}/{}-transaccion.log'.format(TRANSA_FOLDER, str(date.today()))
        transa_logger = logging.getLogger("transactional")
        transa_handler = logging.FileHandler(transa_log_file)
        transa_handler.setFormatter(TRANSA_FORMATTER)
        transa_logger.setLevel(logging.INFO)
        transa_logger.addHandler(transa_handler)
    return transa_logger

def create_folders():
    """
    Crea las carpetas donde se colocaran los archivos
    de errores y transacciones.
    """
    if(IS_TRANSA_LOG_ACTIVE and not path.exists(TRANSA_FOLDER)):
        mkdir(TRANSA_FOLDER)
    if(IS_ERROR_LOG_ACTIVE and not path.exists(ERROR_FOLDER)):
        mkdir(ERROR_FOLDER)

def set_printable_values():
    """Se utiliza este metodo para cambiar
    los valores definidos a continuacion por un punto."""
    global PRINTABLE_ASCII
    temp = set(printable)
    temp.remove("\x09")
    temp.remove("\x20")
    temp.remove("\x0A")
    temp.remove("\x0C")
    PRINTABLE_ASCII = temp


def activate_logs(activate_transa_log, activate_error_log):
    """Activa los logs acorde a las configuraciones del usuario"""
    global IS_TRANSA_LOG_ACTIVE
    global IS_ERROR_LOG_ACTIVE
    global TRANSA_LOGGER
    global ERROR_LOGGER
    IS_TRANSA_LOG_ACTIVE = activate_transa_log
    IS_ERROR_LOG_ACTIVE = activate_error_log
    create_folders()
    set_printable_values()

    if(IS_TRANSA_LOG_ACTIVE):
        TRANSA_LOGGER = config_transactional_logger()

    if(IS_ERROR_LOG_ACTIVE):
        ERROR_LOGGER = config_error_logger()

def get_error_log():
    """
    Retorna la instancia del logger para el registro
    de errores.
    """
    return ERROR_LOGGER

def transa_log(msg, **kwargs):
    """
    Registra todos los mensajes de una transaccion
    tanto ascii como en hexadecimal.
    """
    extra_info = {'user': getuser(), 'who': kwargs.get("who_send", "SISTEMA")}
    if(IS_TRANSA_LOG_ACTIVE):
        if (kwargs.get("is_hexa_data", False)):
            msg_hex = msg_chunks(hexlify(msg), 2, True)
            msg = replace_values(msg)
            msg = msg_chunks(msg, 1, True, join_ws=False)
            msg = "HEXA\n{}\nASCII\n{}".format(msg_hex, msg)
        elif(kwargs.get("user_conf", None)):
            user_conf = kwargs.get("user_conf", None)
            conf_msg = get_conf_msg(user_conf)
            msg = "{}\n{}\n".format(msg, conf_msg)
        else:
            symbol = kwargs.get("symbol", "=")
            msg = "{} {} {}\n".format(symbol*5, msg, symbol*5)

        TRANSA_LOGGER.info(msg, extra=extra_info,)


def msg_chunks(message, number, line_break=False, join_ws=True):
    """
    Se utiliza para cortar un mensaje hexadecimal en trozos
    que puedan ser legibles y entendibles.
    """
    result = None
    divide_msg = [message[i:i+number] for i in range(0, len(message), number)]
    divide_msg = [divide_msg[i:i+15] for i in range(0, len(divide_msg), 15)]
    if(line_break):
        divide_msg = [values+["\n"] for values in divide_msg]
    # join_ws = Unir con espacios en blanco
    if(join_ws):
        result = ''.join([' '.join(values) for values in divide_msg])
    else:
        result = ''.join([''.join(values) for values in divide_msg])
    return result

def replace_values(data):
    """
    Reemplaza los valores que no son graficamente visibles
    por puntos.
    """
    data = list(data)
    return ''.join([v if(v in PRINTABLE_ASCII) else '.' for v in data])


def get_conf_msg(user_conf):
    """
    Construye las configuraciones del usuario
    para insertarlas en el registro de transacciones.
    """
    try:
        conn_conf = user_conf.get_connection_config()
        baudrate = conn_conf.get('baudrate')
        parity = conn_conf.get('parity')
        bytesize = conn_conf.get('bytesize')
        stopbits = conn_conf.get('stopbits')
        conf_conex = (baudrate, parity, bytesize, stopbits)
        port = "Puerto: " + conn_conf.get('port')
        conf_conex = "Conf. Conex: " + str(conf_conex)
        time_sleep = "Time Sleep: " + str(user_conf.get_sleep_time())
        time_out = "Time Out: " + str(conn_conf.get('timeout'))
        cashier = "Cajero: " + ("ACTIVADO" if(user_conf.get_cashier_flag()) else "DESACTIVADO")
        previa = "Descuento BIN: " + ("ACTIVADO" if(user_conf.get_previa()) else "DESACTIVADO")
        return '{0},\n{1},\n{2},\n{3},\n{4},\n{5}'.format(port,
                                                          conf_conex,
                                                          time_sleep,
                                                          time_out,
                                                          cashier,
                                                          previa
                                                         )
    except AttributeError as err:
        if(ERROR_LOGGER):
            err = str(err).split(" ")
            err = "99, El metodo {} no existe en {}".format(err[-1], err[0])
            ERROR_LOGGER.error(err)
            raise Exception("99, Revisar log de errores.")
    except Exception as err:
        if(ERROR_LOGGER):
            ERROR_LOGGER.error(str(err))
            raise Exception("99, Revisar log de errores.")
