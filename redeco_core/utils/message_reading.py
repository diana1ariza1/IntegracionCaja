# pylint: disable=superfluous-parens,relative-import,old-style-class,deprecated-lambda
# pylint: disable=no-self-use
"""
Modulo encargado de interpretar cada parte de un mensaje
de acuerdo a su estructura definida en business.config.json
"""
from binascii import unhexlify
from logger import get_error_log
class MessageReading:
    """
    Clase encargada de leer los mensajes recibidos por el datafono, separar cada campo y
    entregarlos para ser interpretados. El metodo principal a ser llamado siempre a de ser
    read_message()
    """
    def __init__(self, business_conf, message_bldg):
        """
        Metodo constructor que inicializa las variables con las instancias previas
        de otras clases.

        business_conf: type(BusinessConfig) -> Instancia de la clase utilizada para
        obtener datos del archivo de configuracion 'business.config.json'.

        message_bldg: type(MessageBuilding) -> Instancia de la clase utilizada para
        la reutilizacion de codigo.
        """
        self._business_conf = business_conf
        self._message_bldg = message_bldg
        self._error_log = get_error_log()

    def read_message(self, data, confirm_msg_incl):
        """
        Se encarga de interpretar cada dato enviado por el datafono. Este proceso consta
        de separar cada dato para generar un diccionario para mejor manipulacion en el
        resto del software.

        Parametros
        ----------
        data: type(str) -> Mensaje recibido a traves de la conexion establecida por el datafono.
        Por ejemplo: ..760000000001099  0.33..40..69..93....

        confirm_msg_incl: type(bool) -> Parametro recibido de la validacion previa
        que identifico si el mensaje incluye el campo "CONFIRM_MESSAGE"; Este campo, en flujo
        unificado, no es recibido inicialmente.

        Return
        ------
        dict -> {
            'LRC': '\\x02',
            'BCD': '\\x007',
            'DATA': ['33\\x00\\x00', '40\\x00\\x00', '69\\x00\\x00', '93\\x00\\x00'],
            'ETX': '\\x03',
            'CONFIRM_MESSAGE': '\\x06',
            'HEADER_FIELDS': {
                'cod_trans': '99',
                'indicator': '0',
                'req_res': '0',
                'cod_res': '  ',
                'version': '1',
                'transport_header': '6000000000'},
                'STX': '\\x02'
            }
        }
        """
        # Se obtiene la estructura basica de un mensaje
        message_definition = self._business_conf.get_message_definition()
        # Se obtienen la configuracion para los campos
        data_frame_structure = self._business_conf.get_data_frame()
        # Se obtiene la configuracion definida para el separador de campos
        field_separator = data_frame_structure["separador_campo"]
        # Se convierte en hexa a byte (1C -> \x1C)
        field_separator = str(
            self._message_bldg.get_byte_from_hex(field_separator["value"],
                                                 max_length=field_separator["max_length"],
                                                 is_hexa=True)
            )

        # Se extran los campos principales: Understood (Opcional), STX, ETX, LRC, BCD.
        separate_data, fields = self.separate_fields(data, message_definition, confirm_msg_incl)
        # Se dividen los campos a partir del separador de campos
        temp_data = fields.split(field_separator)
        separate_data["DATA"] = temp_data
        # Se obtiene los valores de la cabecera. P. ej. "60000000001099"
        header_data = separate_data["DATA"].pop(0)
        # Se obtiene cada "campo" de la cabecera
        header_fields = self.get_header_fields(header_data, data_frame_structure)
        separate_data["HEADER_FIELDS"] = header_fields
        # Cada campo recibido del mensaje es separado individualmente
        separate_data["DATA"] = self.disassemble_data(separate_data["DATA"])
        return separate_data

    def separate_fields(self, data, message_definition, confirm_msg_incl=False):
        """
        Se encarga de extraer los siguientes campos base: Understod, STX, ETX,
        LRC, BCD. Se retorna como un diccionario.
        Asi mismo, retorna unicamente la "cabecera"+"campos de datos" del mensaje.

        Parametros
        ----------
        data: type(str) -> Cadena de datos recibidos por el datafono

        message_definition: type(dict) -> Estructura basica de un mensaje definida en
        'business.config.json'.

        confirm_msg_incl: type(bool) -> Parametro recibido de la validacion previa
        que identifico si el mensaje incluye el campo "CONFIRM_MESSAGE"; Este campo, en flujo
        unificado, no es recibido inicialmente.

        Return
        ------
        Tuple(dict, str): Los campos descritos en el ejemplo de abajo.
        Por ejemplo: (
            {
                'LRC': '\\xb5',
                'BCD': '\\x00\\x90',
                'ETX': '\\x03',
                'CONFIRM_MESSAGE': '\\x06',
                'STX': '\\x02'
            },
            "60000000001099  033  40  69  93"
        )

        Raise
        -----
        ValueError -> Si los valores para los campos STX y ETX no corresponden
        al valor definido en business.config, se considera como mensaje no entendido.
        """
        tmp_data = list(data)
        structure = message_definition["structure"][:]
        if not (confirm_msg_incl):
            structure.pop(structure.index("CONFIRM_MESSAGE"))
        field_structure = dict()
        index = 0
        for field in structure:
            if not(field in ["DATA", "ETX", "LRC"]):
                max_length = int(message_definition[field]["max_length"])
                idx_max = index + max_length
                field_structure[field] = ''.join(tmp_data[index:idx_max])
                tmp_data[index:idx_max] = [None]*max_length
                index = idx_max

        field_structure["LRC"] = tmp_data[-1]
        field_structure["ETX"] = tmp_data[-2]
        tmp_data[-1] = None
        tmp_data[-2] = None
        tmp_data = ''.join(filter(lambda v: v != None, tmp_data))

        stx = unhexlify(message_definition["STX"]["value"])
        etx = unhexlify(message_definition["ETX"]["value"])
        if(field_structure["STX"] == stx and field_structure["ETX"] == etx):
            return field_structure, tmp_data
        else:
            msg = "99, Error. No se entendio el mensaje recibido."
            if(self._error_log):
                self._error_log.error(msg)
            raise ValueError(msg)

    def get_header_fields(self, header_data, data_frame_conf):
        """
        Se encargaa de separar todos los 'campos' que conforman la cabecera del mensaje.

        Parametros
        ----------
        header_data: type(str) -> Cabecera del mensaje
        Por ejemplo: 60000000001000000

        data_frame_conf: type(dict) -> Estructura de la cabecera definida
        en el 'business.config.json'
        Por ejemplo: {
            'cod_trans': {'max_length': 2, 'description': 'Identifica el tipo de transaccion',
            'value': ''},
            'indicator': {'max_length': 1, 'description': 'Siempre 0', 'value': '0'},
            ...
            }

        Return
        ------
        dict -> {
            'cod_trans': '00',
            'indicator': '0',
            'req_res': '0',
            'cod_res': '00',
            'version': '1',
            'transport_header': '6000000000'
            }
        """
        header_structure = data_frame_conf["header_structure"]
        min_position = 0
        header_fields = dict()
        for field_name in header_structure:
            if (field_name != "separador_campo"):
                max_length = data_frame_conf[field_name]["max_length"]
                max_position = min_position + max_length
                value = header_data[min_position :  max_position]
                header_fields[field_name] = value
                min_position = max_position
        return header_fields

    def disassemble_data(self, data):
        """
        Se encarga encarga de extraer unicamente los "campos de datos", es decir
        los campos en los que se envia informacion como el monto,
        iva, descuento, codigo cajero, numero de factura y demas.
        Con la finalidad de obtener cuales son los campos que espera el datafono.

        Parametros
        ----------
        data: type(str) -> "Campos de datos" del mensaje, previamente procesados.
        Por ejemplo: [
            '33\\x00\\n0         ',
            '40\\x00\\x0c000000080000',
            '41\\x00\\x0c000000000000',
            '42\\x00\\x0c000000000000',
            '44\\x00\\x0c000000000000',
            '66\\x00\n0         '
        ]

        Return
        ------

        list ->  Lista de tuplas con el codigo del campo y el valor correspondiente.
        Por ejemplo:[
            ('C33', '0         '),
            ('C40', '000000080000'),
            ('C41', '000000000000'),
            ('C42', '000000000000'),
            ('C44', '000000000000'),
            ('C66', '0         ')
        ]
        """
        field_structure = self._business_conf.get_field_structure()
        extracted_values = list()
        for value in data:
            min_position = 0
            temp_list = list()
            for field in field_structure["structure"]:
                if not(field in ["separador_campo", "value", "message_length"]):
                    max_position = min_position + field_structure[field]["max_length"]
                    value_extracted = value[min_position: max_position]
                    value_extracted = 'C'+ value_extracted
                    min_position = max_position
                    temp_list.append(value_extracted)
                elif(field == "message_length"):
                    max_position = min_position + field_structure[field]["max_length"]
                    value_extracted = value[max_position :]
                    temp_list.append(value_extracted)
            extracted_values.append(tuple(temp_list))

        return extracted_values

    def generate_inputs(self, message, built_fields, field_code, op_type):
        """
        Se encarga de generar los datos de entrada a partir
        de los campos solicitados por el datafono.

        Parametros
        ----------
        message: type(dict) -> Mensaje enviado por el datafono previamente procesado.
        Por ejemplo: {
            'LRC': '\\x02',
            'BCD': '\\x007',
            'DATA': [('C33', ''), ('C40', ''), ('C69', ''), ('C93', '')],
            'ETX': '\\x03',
            'CONFIRM_MESSAGE': '\\x06',
            'HEADER_FIELDS': {u'cod_trans': '99', u'indicator': '0', ...},
            'STX': '\\x02'
        }

        built_fields: type(list) -> Datos de entrada generados por el usuario
        previamente procesados para obtener la siguiente estructura.
        Por ejemplo: [
            (u'C33', '0         '),
            (u'C40', '000000080000'),
            ...
        ]

        field_code: type(str) -> Campo que sera utilizado para enviar el tipo de
        operacion". Se obtiene de la configuracion de 'business.config.json'-
        Por ejemplo: "C69"

        op_type (operation type): type(str) -> Codigo de la operacion definida por
        el usuario en los datos de entrada.

        Return
        ------
        tuple -> tupla con los valores necesarios para construir un mensaje.
        El primer valor corresponde a los datos de entrada y el segundo valor
        corresponde a la estructura de la operacion.
        Por ejemplo: (['00', '0         ', '000000080000', '00', '0'],
        ['C33', 'C40', 'C69', 'C93'])
        """
        # Se convierte en un dict para mejor manipulacion
        built_fields = dict((key, value) for key, value in built_fields)
        # Del mensaje (message) se convierten los "campos de datos"
        # en una lista de campos (["C30", "C33", ...])
        operation = list(code for code, _ in message["DATA"])
        input_values = [
            built_fields[field]
            if field in built_fields else "\x00"
            for field in operation
        ]
        if (field_code != None and field_code in operation):
            # Se reemplaza el valor del "campo" utilizado
            # para enviar el tipo de operacion
            input_values[operation.index(field_code)] = op_type
        # Se inserta el tipo de operacion en la primera posicion
        # por convenciones de uso en el software
        input_values.insert(0, op_type)
        return input_values, operation
