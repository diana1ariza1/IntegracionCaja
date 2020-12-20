"""Modulo encargado de manejar el tipo de conexiones"""
# pylint: disable=superfluous-parens,old-style-class,relative-import
from com_connection import COMConnection
from logger import transa_log

class Connection:
    """
    Instancia de la clase de acuerdo al tipo
    de comunicacion definida por el usuario
    """
    def __init__(self, user_conf):
        self._user_conf = user_conf
        self._connection = None
        self._type_connection = user_conf.get_type_connection()

        if(self._type_connection == "COM"):
            self._connection = COMConnection(user_conf.get_connection_config()).get_serial_com()
        else:
            msg = "99,Tipo de conexion (Puerto:{}) no permitido.".format(self._type_connection)
            raise ValueError(msg)


    def write(self, data, **kwargs):
        """
        Modulo encargado de enviar los datos por
        el canal que corresponda de acuerdo al tipo
        de comunicacion. Del mismo modo escribe en el
        transa_log cada mensaje enviado.

        Parametros (Opcionales)
        -----------------------
        audit_msg: type(str) ->  Mensaje que describe alguna
        accion sucedida en la transaccion.

        who_send: type(str) -> Se envia 'sistema' cuando
        el mensaje es una notificacion o accion
        que finalice la transaccion. Se envia 'Caja' cuando
        es un mensaje de la transaccion.

        is_hexa: type(bool) -> Si el mensaje es hexadecimal
        se debe enviar True para que el mensaje pueda ser
        escrito en un formato correcto en transa_log.
        """
        audit_msg = kwargs.get("audit_msg", None)
        who_send = kwargs.get("who_send", None)
        is_hexa = kwargs.get("is_hexa", False)

        if(self._type_connection == "COM"):
            self._connection.write(data)
        else:
            msg = "99, Error al enviar por la conexion {}".format(self._type_connection)
            raise ValueError(msg)

        if(is_hexa and audit_msg):
            transa_log(data, is_hexa_data=is_hexa, who_send=who_send)
            transa_log(audit_msg)
        elif(is_hexa and not audit_msg):
            transa_log(data, is_hexa_data=is_hexa, who_send=who_send)

    def read(self, bytes_to_receive=512, **kwargs):
        """
        Modulo encargado de recibir los datos por
        el canal que corresponda de acuerdo al tipo
        de comunicacion. Del mismo modo escribe en el
        transa_log cada mensaje enviado.

        Parametros
        ----------
        bytes_to_receive: type(str) -> Numero de bytes
        a recibir en un mensaje enviado por el datafono.
        Por defecto son 512 bytes.

        Parametros (Opcionales)
        -----------------------
        who_send: type(str) -> Se envia 'Dataphone' cuando
        es un mensaje de la transaccion
        """
        who_send = kwargs.get("who_send", None)
        data = None
        if(self._type_connection == "COM"):
            data = self._connection.read(bytes_to_receive)
        else:
            msg = "99, Error al recibir por la conexion {}".format(self._type_connection)
            raise ValueError(msg)

        transa_log(data, is_hexa_data=True, who_send=who_send)
        return data


    def is_open(self):
        """Valida si el puerto para el tipo de conexion
        este abierto."""
        result = None
        if(self._type_connection == "COM"):
            result = self._connection.is_open
        else:
            msg = "99, No se puede validar la conexion para {}.".format(self._type_connection)
            raise ValueError(msg)

        return result

    def close(self):
        """Cierra el puerto para el tipo de conexion definido
        del mismo modo limpia el buffer de entrada y salida
        para que no queden residuo de datos."""
        if(self._type_connection == "COM"):
            self._connection.reset_input_buffer()
            self._connection.reset_output_buffer()
            self._connection.close()
        else:
            msg = "99, No se puede cerrar la conexion para {}.".format(self._type_connection)
            raise ValueError(msg)
