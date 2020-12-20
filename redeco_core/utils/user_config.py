# pylint: disable=superfluous-parens,old-style-class,missing-docstring,no-self-use
# pylint: disable=too-many-instance-attributes
"""
Modulo utilizado para la manipulacion y uso de las
configuraciones del usuario
"""
from collections import OrderedDict
class UserConfig:
    """
    Clase utilizada como setter and getter
    para la manipulacion de las configuraciones
    de usuario.
    """
    def __init__(self, json_data):
        self._set_values(json_data)

    def _set_values(self, json_data):
        """
        Asignacion de valores apartir de la lectura
        del archivo json, generando un diccionario
        que mejora la accesibilidad de los datos para
        poder asignarlos a variables de la clase.
        """
        self._id_terminal = json_data.get("id_terminal", None)
        self._port = json_data.get("puerto")
        self._connection_type = json_data.get("tipo_conexion")
        self._baudrate, self._parity, self._bytesize, self._stopbits = json_data.get("config_conexion")
        self._sleep = float(json_data.get("sleep", 5))
        self._timeout = float(json_data.get("time_out", 10))
        self._visible = int(json_data.get("visible", 2))
        self._cashier = bool(json_data.get("cajero", 0))
        self._input_file_name = json_data.get("archivo_solicitud")
        self._output_file_name = json_data.get("archivo_respuesta")
        self._delete_files = int(json_data.get("borrar_archivos", 2))
        self._unified_flow = bool(json_data.get("flujo_unificado", 0))
        self._selected_fields = json_data.get("datos_respuesta")
        self._previa = bool(json_data.get("previa", 0))
        self._log_transaccional = bool(json_data.get("log_transaccional", 0))
        self._log_errores = bool(json_data.get("log_errores", 0))
        self._commerce_code = json_data.get("comercio", None)
        self._confirmar = bool(json_data.get("confirmar", 0))

    def get_terminal(self):
        return self._id_terminal

    def get_confirm_msg(self):
        return self._confirmar

    def get_connection_config(self):
        """Retorna las configuraciones de conexion
        en un diccionario para mejor manipulacion"""
        config = dict()
        config.update(port=self._port, baudrate=self._baudrate)
        config.update(parity=str(self._parity), bytesize=self._bytesize)
        config.update(stopbits=self._stopbits, timeout=self._timeout)
        return config

    def get_sleep_time(self):
        return self._sleep

    def get_cashier_flag(self):
        return self._cashier

    def get_visible(self):
        return self._visible

    def get_input_file_name(self):
        return self._input_file_name

    def get_output_file_name(self):
        return self._output_file_name

    def get_delete_files_flag(self):
        return self._delete_files

    def is_unified_flow_active(self):
        return self._unified_flow

    def get_previa(self):
        return self._previa

    def get_logs_flag(self):
        return bool(self._log_transaccional), bool(self._log_errores)

    def has_commerce_code(self):
        return self._commerce_code

    def get_type_connection(self):
        return self._connection_type

    def get_selected_fields(self):
        return self._selected_fields

    def get_output_data(self, built_fields, business_conf):
        """
        De la respuesta de la transaccion se reciben una lista con campos
        previamente separados, cada uno con su respectivo valor.

        Parametros
        ----------
        built_fields: type(list) -> Campos previamente separados de la respuesta
        de la transaccion
        Por ejemplo: [
            ('C00', '00'),
            ('C01', 'HOME01'),
            ('C30', '430366**8180'),
            ('C33', 'alvaro    '),
            ('C34', 'CR'),
            ('C35', 'VISA      '),
            ('C40', '000000010000'),
            ('C41', '000000000020'),
            ('C42', '000000000022'),
            ('C65', '000034'),
            ('C67', '01'),
        ]

        business_conf: type(BusinessConf): Instacia de la clase para poder
        acceder a metodos pertenecientes a la misma

        Return
        ------
        str -> Se retorna los campos seleccionados por el usuario
        definidos previamente en el archivo de configuracion.
        Por ejemplo
        00, HOME01, 430366**8180,VISA, alvaro, 10000...
        """
        try:
            # Se obtienen los "datos respuesta" que espera el usuario
            selected_fields = self._selected_fields[:]
            # Se obtienen todos los campos definidos en el archivo business.config
            fields_definition = business_conf.get_fields_definition()
            # Se crea un Diccionario(dict) de tipo OrderedDict()
            # Para mantener el orden en el que se ingresan los campos
            # acorde al orden definido por el usuario
            output_data = OrderedDict()
            # Este bucle for es utilizado para obtener el "campo" y "tipo de dato"
            # de cada campo seleccionado por el usuario apoyandose de la
            # propiedad "description" definida para cada campo
            for field in selected_fields:
                for key, value in fields_definition.iteritems():
                    if(value["description"] == field):
                        output_data[key] = value["data_type"]
                        break

            # Una vez obtenido cuales son los campos que el usuario selecciono
            # se empieza a reemplazar los campos seleccionados por los
            # campos de la respuesta de la transaccion
            for field, value in built_fields:
                value = self._clear_value(value)
                if(field in output_data):
                    if(output_data[field] == 'N' and value.isdecimal()):
                        value = int(value)
                    output_data[field] = value

            return ','.join([self._delete_static_data(value) for value in output_data.values()])
        except Exception as _:
            msg = "99, Error al construir los datos de salida"
            raise Exception(msg)


    def _clear_value(self, value):
        """
        Funcion encargada de eliminar espacios en blanco
        asi como tambien, eliminar los valores \x00 que envia
        el datafono como representacion "un valor nulo"
        """
        value = ''.join(value.split())
        value = value.replace("\x00", '')
        return value.decode(encoding='utf-8')

    def _delete_static_data(self, value):
        """
        Se elimina el tipo de dato correspondiente a un campo
        que fue insertado temporalmente para posteriormente
        ser reemplazado con el verdadero valor del campo.

        Algunos campos no son reemplazados debido a que la respuesta
        de la transaccion no devuelve dicho campo, por lo que para campo
        seleccionado se mantiene el valor "tipo de dato" de ese campo.

        Por lo que se tiene que reemplazar por un valor como "Null".
        """
        if(value == 'ANS' or value == 'N' or value == ""):
            value = 'Vacio'
        return value if not isinstance(value, int) else str(value)
