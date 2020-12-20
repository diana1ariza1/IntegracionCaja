# pylint: disable=superfluous-parens,relative-import,old-style-class,no-self-use,too-many-locals
"""
    Modulo encargado de construir un mensaje a partir
    de los datos de entrada y de la operacion seleccionada
    por el usuario, del mismo modo se recibe como parametro
    una instancia de la clase BusinessConfig para el uso
    de funciones declaradas en dicha clase
"""
from logger import get_error_log
class MessageBuilding:
    """
        Se define la clase con una serie de metodos
        que permite utilizar los datos para: pre-procesarlos,
        separarlos, armar la estructura basica, obteniendo un
        mensaje listo para enviar.

    """
    def __init__(self, business_conf):
        self._business_conf = business_conf
        self._error_log = get_error_log()

    def build_message(self, data, operation, op_type):
        """
        Encargada de construir un mensaje apartir de los datos y la estructura
        de una operacion dada. Se construye el mensaje a partir de la estructura
        definida en "business.config.json"

        Parametros
        ----------
        data: type(list) -> Datos de entrada generados por el usuario.
        Por ejemplo: ['00', '0', '80000', '0', '0', '0', '0 ']

        operation: type(list) -> Lista con los campos que corresponden a la operacion seleccionada
        por el usuario. Esta operacion es seleccionada previamente acorde al primer valor de
        los datos de entrada. En el ejemplo de arriba seria el '00'
        Por ejemplo: ['C33', 'C40', 'C41', 'C42', 'C44', 'C66']

        op_type: (str) -> Codigo de la transaccion que se realizara, esta es
        agregada en la cabecera del mensaje

        Return
        ------
        tuple -> Se retonar una tupla de dos valores, donde el primer valor (tuple[0])
        corresponde a un arreglo de tuplas (Codigo campo, Valor del campo)
        y el segundo valor (tuple[1]) corresponde al mensaje construido
        Por ejemplo:
            (
                [
                    ('C33', '0         '),
                    ('C40', '000000080000'),
                    ('C41', '000000000000'),
                    ('C42', '000000000000'),
                    ('C44', '000000000000'),
                    ('C66', '0         ')
                ],
                "...6000000000100000033..0         40..00000000001041..00000000000542"
            )
        """
        message_dict = dict()
        # Se construye el mensaje apartir de la configuracion
        message_definition = self._business_conf.get_message_definition()
        message_struc = message_definition["structure"]
        # Se construye la cabecera del mensaje
        header = self.assemble_header(cod_trans=op_type)
        # Se construye los campos con su respectivo valor
        data_fields = self.assemble_data(data[1:], operation)
        field_structure = self._business_conf.get_field_structure()
        # Se arma cada campo y se reemplaza por su respectivo valor
        data = self.replace_values(fields=data_fields[:], field_structure=field_structure)
        # Se calcula el BCD del mensaje, excluyendo STX, ETX y LRC
        data = header + data
        message_dict.update(DATA=data)
        # Se obtiene la longitud que deberia tener el campo BCD
        bcd_max_length = int(message_definition["BCD"]["max_length"])
        data_length = str(len(data))
        # Se transforma el valor a Byte.
        bcd = self.get_byte_from_hex(value=data_length, max_length=bcd_max_length, is_hexa=True)
        message_dict.update(BCD=bcd)

        stx, etx = self._get_stx_and_etx()
        message_dict.update(STX=stx)
        message_dict.update(ETX=etx)
        # Se calculo el LRC del mensaje desde BCD hasta ETX, excluyendo STX
        message = bcd + data  + etx
        lrc = self.calculate_lrc(str(message))
        message_dict.update(LRC=lrc)
        # Se obtiene el valor que indica que el mensaje fue entendido
        understood_value = self._business_conf.get_understood_value()
        # Se transforma en Hexadecimal
        understood_value = self.get_byte_from_hex(understood_value, is_hexa=True)
        message_dict.update(CONFIRM_MESSAGE=understood_value)
        message = self.assemble_structure(message_struc, message_dict)
        return data_fields, message

    def assemble_header(self, req_res="0", cod_trans="00"):
        """
        Ensambla la estructura de la cabecera (header structure), la estructura
        a ensamblar esta compuesta de el "transport header" y el "presentation header"
        el cual es extraido desde la configuracion definida en el archivo business.config.json

        Parametros
        ----------
        req_res: type(str) -> Es usado para reemplazar el valor de req_res de la estructura del
        campo "presentation header", por defecto el valor es "0" debido a que la caja
        siempre espera una respuesta.

        cod_trans: type(str) -> Es usado para reemplazar el valor de cod_trans de la estructura
        del campo "presentation header", por defecto el valor es "00".

        Return
        ------
        str -> Cabecera del mensaje (transport_header).
        Por ejemplo: "60000000001000000"

        Raises
        ------
        ValueError -> Retorna una excepcion de tipo ValueError si el valor proporcionado
        para "req_res" no se encuentra o coincide con los datos
        del archivo business.config.json
        """
        data_frame = self._business_conf.get_data_frame()
        header_structure = data_frame['header_structure']
        header_list = list()
        # Se compone el valor para cada campo definido de la estructura de la cabecera
        for field in header_structure:
            # Se valida si el campo es requerimiento/respuesta
            if(field == 'req_res'):
                if not(req_res in data_frame[field]["value"]):
                    msg = "99, Campo req_res ({}) invalido.".format(req_res)
                    if(self._error_log):
                        self._error_log.error(msg)
                    raise ValueError(msg)

                max_len = data_frame[field]["max_length"]
                value = self.valid_length(req_res, max_len)
                header_list.append(value)
            # Se valida si el campo es "Codigo de transaccion"
            elif(field == "cod_trans"):
                max_len = data_frame[field]["max_length"]
                value = self.valid_length(cod_trans, max_len)
                header_list.append(value)
            # Se valida si el campo es "Separador de Campo"
            # para transformarlo como byte, se recibe "1C", se transforma "\x1C"
            elif(field == "separador_campo"):
                separador = self.get_byte_from_hex(
                    value=data_frame[field]["value"],
                    max_length=data_frame[field]["max_length"],
                    is_hexa=True
                    )
                header_list.append(separador)
            # De lo contrario, a los demas campos se le asigna el valor definido
            # en el archivo business.config.json
            else:
                value = data_frame[field]["value"]
                max_len = data_frame[field]["max_length"]
                value = self.valid_length(value, max_len)
                header_list.append(value)
        # Se retorna el concatenado de todos los campos
        return ''.join(str(field) for field in header_list)

    def assemble_data(self, data, operation):
        """
        Ensambla la estructura de cada campo necesario para la operacion a realizar
        a partir de los datos de entrada. Cada campo de una operacion cuenta con una
        configuracion definida en el archivo business.config.json. Por lo que cada
        valor de los datos de entrada es adaptado a la configuracion de cada campo.

        Parametros
        ----------
        data: type(list) -> Corresponde a los datos de entrada.
        Por ejemplo: ["0","80000","0","0","0","0" ]

        operation: type(list) -> Corresponde a la operacion obtenida acorde
        al codigo de operacion y al numero de valores recibidos en los datos de entrada.
        Por ejemplo: [u'C33', u'C40', u'C41', u'C42', u'C44', u'C66']

        Posteriormente se convertira como el ejemplo de abajo, haciendo uso del metodo
        get_fields() de la clase BusinessConfig:

        [
            (u'C33', {u'max_length': 10, u'description': u'cod_cajero', u'data_type': u'ANS'}),
            (u'C40', {u'max_length': 12, u'description': u'monto_transaccion', u'data_type': u'N'}),
            ...
        ]

        Return
        ------
        list -> Retorna una lista con los datos adaptados a la configuracion de cada campo.
        Por ejemplo: [
            (u'C33', '0         '),
            (u'C40', '000000080000'),
            (u'C41', '000000000000'),
            ...
        ]

        Raises
        ------
        ValueError -> Retorna una excepcion de tipo ValueError si el tipo de dato
        para un campo no coincide con los establecidos en los if.
        """
        try:
            fields_operation = self._business_conf.get_fields(operation)
            for i, (code, field_structure) in enumerate(fields_operation):
                if(data[i] == "\x00"):
                    fields_operation[i] = (code, '')
                    continue

                input_len = len(data[i])
                required_len = int(field_structure['max_length'])
                if(input_len > required_len):
                    msg = "99, Longitud superada. Campo {}, valor {}".format(code, data[i])
                    raise ValueError(msg)
                padding_len = required_len - input_len

                if(field_structure['data_type'] == 'ANS'):
                    fields_operation[i] = (code, data[i] + "\x20"*padding_len)
                elif(field_structure['data_type'] == 'N'):
                    fields_operation[i] = (code, '0'*padding_len + data[i])
                else:
                    msg = "99, Tipo de dato invalido.'{}'".format(field_structure['data_type'])
                    raise ValueError(msg)

            return fields_operation
        except IndexError as _:
            data = "\nDatos:{}".format(data)
            op_type = "\nOperacion:{}".format(operation)
            msg = "99, Error, longitud de campos incosistentes.{}{}".format(data, op_type)
            raise Exception(msg)

    def assemble_structure(self, message_struc, message_dict):
        """
        Se construye toda la estructura de un mensaje de acuerdo
        a la configuracion definida.

        Parametros
        ---------
        message_struc(list) -> Es una lista con todos los componentes
        que constituyen el mensaje, se construye acorde a su posicion
        en la lista.

        message_dict(dict) -> Es el diccionario con lo necesario para
        construir el mensaje, donde el "key" es el nombre del componente
        y "value" el valor que corresponde.

        Return
        ------
        str -> Mensaje construido listo para ser enviado
        """
        message = ""
        for component in message_struc:
            message += message_dict[component]
        return str(message)


    def replace_values(self, fields, field_structure):
        """
        Cada campo esta compuesto de una serie de elementos como lo son: el codigo del campo,
        la longitud del valor del campo, el valor del campo y un separador de campo.
        Por lo que esta funcion se encarga de reemplazar los valores de cada elemento,
        con los valores recibidos y previamente procesados.

        fields: type(list) -> Es una lista de tuplas, cada tupla contiene el codigo del campo y
        el valor para ese campo.
        Por ejemplo: [
            (u'C33', '0         '),
            (u'C40', '000000080000'),
            (u'C41', '000000000000'),
            ...
        ]

        field_structure: type(dict) -> Es la estructura general que debe cumplir cada campo
        para ser de una operacion.
        Por ejemplo:{
            'field_code': {'max_length': 2, 'description': 'Codigo del campo', 'value': u''},
            'message_length': {'max_length': 2, 'description': 'Utilizado para represe....'},
            'separador_campo': {'max_length': 1, 'description': 'FS, Separador de Campo', ... },
            'structure': ['field_code', 'message_length', 'value', 'separador_campo']
        }

        Return
        ------
        str ->  Todos los campos de una operacion concatenados.
        Por ejemplo: "33  0         40  000000080000 41  ..."

        En hexadecimal vendria siendo: "33 33 00 0a 30 20 20 20 20 20 20 20 20 20 1c 34 30 ..."
        """
        structure = field_structure["structure"]
        max_length = field_structure['message_length']["max_length"]
        field_separator = field_structure['separador_campo']["value"]
        field_separator = self.get_byte_from_hex(value=field_separator, is_hexa=True)
        # last_index se usa para identificar el ultimo campo. Debido a que el ultimo campo de una
        # operacion no lleva "separador de campo (FS)"
        last_index = len(fields)-1

        for index, (code, value) in enumerate(fields):
            temp_value = ''
            for element in structure:
                if(element == "field_code"):
                    temp_value += str(code)[1:]
                elif(element == "message_length"):
                    temp_value += str(self.get_byte_from_hex(value=value, max_length=max_length))
                elif(element == "value"):
                    temp_value += value
                elif(element == "separador_campo" and index < last_index):
                    temp_value += str(field_separator)

            fields[index] = temp_value
        return ''.join(fields)

    def get_byte_from_hex(self, value, max_length=1, is_hexa=False):
        """
        Obtiene el valor en byte de un valor hexadecimal.

        Parameters
        ----------
        value: type(str) -> Valor hexadecimal que se convertira en un byte,
        hay casos en los que no siempre sera hexadecimal, sino un decimal
        acorde a la tabla ascii.

        max_length: type(int) -> Es la longitud maxima, cada valor de dos (2)
        digitos representa la longitud de uno (1) en hexadecimal.
        Por defecto el valor es "1".
        Por ejemplo:
        * El valor "02" con longitud maxima de 2 sera convertido en "\\x00\\x02"
        * El valor "0A" con longitud maxima de 1 sera convertido en "\\x0A"

        is_hexa: type(bool) -> Si el valor es False se convertira a hexadecimal
        y luego a byte, de lo contrario no hara nada. Por defecto es False.

        Return
        ------
        bytearray == str -> Valor hexadecimal en bytes
        Por ejemplo: "\\x1c"
        """
        try:
            if not(is_hexa):
                value = hex(len(value))[2:]
            value = '0'+value if(len(value) == 1) else value

            if not(len(value) == (max_length*2)):
                remaining_length = max_length*2 - len(value)
                value = '0' * remaining_length + value

            return bytearray.fromhex(value)
        except ValueError as _:
            msg = "99, Error al transformar a byte, valor:{}.".format(value)
            if(is_hexa):
                msg = "99, {} No pertenece a un hexadecimal valido.".format(value)
            if(self._error_log):
                self._error_log.error(msg)
            raise ValueError(msg)

    def valid_length(self, value, max_length):
        """Valida la longitud de cada campo perteneciente
        a la cabecera, si esta incompleto, se encarga
        de rellenar los espacios faltantes con ceros (0)."""
        if not(len(value) == max_length):
            remaining_length = max_length - len(value)
            value = value + '0' * remaining_length
        return value

    def calculate_lrc(self, data):
        """
        Calcula el LRC del mensaje con
        la operacion XOR.
        """
        lrc = ord(data[0])
        for value in data[1:]:
            lrc ^= ord(value)

        return chr(lrc)

    def _get_stx_and_etx(self):
        """Obtiene los campos STX y ETX del mensaje"""
        stx = self._business_conf.get_message_definition()["STX"]
        etx = self._business_conf.get_message_definition()["ETX"]

        stx = self.get_byte_from_hex(value=stx["value"], max_length=stx["max_length"], is_hexa=True)
        etx = self.get_byte_from_hex(value=etx["value"], max_length=etx["max_length"], is_hexa=True)

        return stx, etx
