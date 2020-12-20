# pylint: disable=old-style-class,too-few-public-methods
"""
Modulo para la conexion a traves del puerto COM
"""
import serial
from serial import SerialException

class COMConnection():
    """
    Clase utilizada para la configuracion e
    instancia del puerto COM.
    """
    def __init__(self, config):
        self.config = config
        self._create_serial_connection()

    def _create_serial_connection(self):
        """
        Crea la instancia de la conexion serial a traves del puerto COM.
        """
        try:
            self._serial_com = serial.Serial(**self.config)
        except SerialException as _:
            msg = "99, No se pudo abrir el puerto {}.".format(self.config['port'])
            raise SerialException(msg)

    def get_serial_com(self):
        """Retorna la instancia de la conexion serial"""
        return self._serial_com
