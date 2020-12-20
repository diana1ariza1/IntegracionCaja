# pylint: disable=superfluous-parens,relative-import,old-style-class,useless-else-on-loop
# pylint: disable=too-many-locals
"""
Clase usada como controlador de comunicacion
"""
from time import  sleep
from binascii import unhexlify
from logger import transa_log

def previa_decorator(function):
    """
    Funcion decorador para obtener cual es el codigo
    de campo en el que se envia/recibe la tarjeta.
    Con la finalidad de reducir costo de procesamiento
    unicamente se realiza una vez antes de iniciar el flujo.
    """
    def wrapper(*args, **kwargs):
        """
        Como toda funcion decorador, es necesario un wrapper;
        obtiene cual es el codigo de campo para enviar/recibir
        el nro de tarjeta.
        """
        controller = list(args).pop()
        business_conf = controller.business_conf
        if(controller.previa_activated):
            fields = business_conf.get_fields_definition()
            card_field = [k for k, v in fields.iteritems() if v['description'] == 'tarjeta'].pop()
            kwargs.update(card_field=card_field)
        return function(*args, **kwargs)
    return wrapper

class CommnController:
    """
    Clase encargada de enviar y recibir la comunicacion con
    el datafono.
    """
    def __init__(self, **kwargs):
        self.message_rdg = kwargs.get('message_rdg')
        self.message_bldg = kwargs.get('message_bldg')
        self.business_conf = kwargs.get('business_conf')
        self.user_conf = kwargs.get('user_conf')
        self.file_action = kwargs.get('file_action')
        self.previa_activated = self.user_conf.get_previa()
        self.connection = None

    def initializer(self, connection, data):
        """
        Metodo que inicializa la comunicacion con el datafono,
        * Recibe los mensajes enviados por el datafono
        * Valida el tipo de flujo (Unificado o no unificado)
        * Envia los mensajes al datafono

        Parametros
        ----------

        connection: type(COMConnection) -> Instancia del tipo de comunicacion definida.
        """
        result = None
        built_fields = self.built_fields(data)
        self.connection = connection
        understood = self.business_conf.get_understood_value()
        understood = self.message_bldg.get_byte_from_hex(understood, is_hexa=True)
        not_understood = self.business_conf.get_not_understood_value()
        not_understood = self.message_bldg.get_byte_from_hex(not_understood, is_hexa=True)
        transa_log("INICIO TRANSACCION")
        transa_log("CONFIGURACION", user_conf=self.user_conf)
        # Se obtiene los datos enviados por el datafono
        dataphone_msg = self.connection.read(who_send="DATAFONO")
        # Si hubo respuesta se procesa el mensaje
        if(dataphone_msg != ''):
            try:
            # para enviar el codigo de operacion
            # Si es flujo unificado, obtiene cual es el campo utilizado
                is_unified, field_code, disassembled_msg = self.identify_flow(dataphone_msg)
                if(is_unified):
                # Transmision de mensajes para flujo unificado
                # Retorna los ultimos valores enviados por el datafono
                    kwargs = dict()
                    kwargs.update([('message', disassembled_msg), ('op_type', data[0])])
                    kwargs.update([('field_code', field_code), ('built_fields', built_fields)])
                    kwargs.update(understood=understood, not_understood=not_understood)
                    result = self.unified_flow(**kwargs)
                    transa_log("TRANSACCION COMPLETADA")
                else:
                    cod = disassembled_msg["HEADER_FIELDS"]["cod_trans"]
                    msg = "99, Flujo no unificado sin implementar. Cod. Trans '{}'".format(cod)
                    self.connection.write(not_understood, is_hexa=True, who_send="CAJA")
                    transa_log(msg)
                    transa_log("TRANSACCION COMPLETADA")
                    raise Exception(msg)
            except (Exception, ValueError) as error:
                transa_log(error)
                transa_log("FIN TRANSACCION")
                raise error
        else:
            # Si se agota el tiempo de espera y no hubo respuesta se interrumpe la ejecucion
            err_msg = "99, No se establecio conexion con el datafono. Tiempo de espera agotado"
            transa_log(err_msg)
            transa_log("FIN TRANSACCION")
            raise Exception(err_msg)

        return result

    @previa_decorator
    def unified_flow(self, **kwargs):
        """
            Funcion que corresponde a la secuencia de una transaccion
            con flujo unificado. Esta secuenca de transmision de mensajes
            termina cuando el datafono responde con el valor "1" en el campo
            req_res.

            Parametros (kwargs):
            --------------------
            message: type(dict) -> Mensaje recibido por el datafono desensamblado.
            Por ejemplo: {
                'LRC': '\\x02',
                'BCD': '\\x007',
                'DATA': [('C33', ''), ('C40', ''), ('C69', ''), ('C93', '')],
                'ETX': '\\x03',
                'CONFIRM_MESSAGE': '\\x06',
                'HEADER_FIELDS': {u'cod_trans': '99', u'indicator': '0', ...},
                'STX': '\\x02'
            }

            built_fields: type(list) -> Datos de entrada previamente procesados.
            Cada campo cumple con una longitud y tipo de dato especifico, definido
            en el archivo de configuracion del negocio.
            Por ejemplo:
            [
                ('C33', 'cajero1   '),
                ('C40', '000000080000'),
                ('C41', '000000000000'),
                ...
            ]
            field_code: type(str) -> Corresponde al campo el cual sera utilizado
            para enviar el tipo de operacion.
            Por ejemplo: "C69"

            op_type: type(str) -> Tipo de operacion a realizar.
            Por ejemplo: "00"

            card_field: type(str) -> (*Opcional) Codigo de campo en el que se recibe
            la tarjeta, el decorador "previa_decorator" aniade el campo si el "Descuento
            con BIN" esta activado.

            understood: type(Bytearray) -> Valor hexadecimal para indicar que el mensaje
            fue entendido.

            not_understood: type(Bytearray) -> Valor hexadecimal para indicar que el mensaje
            no fue entendido.
        """
        dataphone_msg = kwargs.get('message')
        card_field = kwargs.get('card_field', None)
        understood = kwargs.pop("understood")
        not_understood = kwargs.pop("not_understood")

        kwargs.pop("card_field", None)
        # Mientras la respuesta del datafono no sea 1, se ejecutara lo siguiente
        while dataphone_msg["HEADER_FIELDS"]["req_res"] == '0':
            if(self.previa_activated and card_field != None):
                msg_fields = dataphone_msg["DATA"]
                card_value = [value for field, value in msg_fields if card_field == field]
                if(card_value):
                    card_value = card_value.pop()
                    kwargs['built_fields'] = self.bin_discount(card_value)

            data_values, operation = self.message_rdg.generate_inputs(**kwargs)
            op_type = kwargs.get("op_type")
            _, message = self.message_bldg.build_message(data_values, operation, op_type)
            # Envia el mensaje y registra en el log
            self.connection.write(message, is_hexa=True, who_send="CAJA")
            # Recibe el mensaje y registra en el log
            dataphone_res = self.connection.read(who_send="DATAFONO")

            if(len(dataphone_res) <= 1):
                msg = "99, Transaccion incompleta, tiempo de espera agotado."
                self.connection.write(not_understood, is_hexa=True, who_send="CAJA")
                raise Exception(msg)

            have_field = self.have_field_understood(dataphone_res)
            dataphone_msg = self.message_rdg.read_message(dataphone_res, have_field)
            kwargs['message'] = dataphone_msg
        else:
            if(dataphone_msg["HEADER_FIELDS"]["req_res"] == '1'):
                self.connection.write(understood, is_hexa=True, who_send="CAJA")
                return dataphone_msg["DATA"]

    def identify_flow(self, dataphone_msg):
        """
        Identifica el tipo de flujo a partir de un mensaje recibido.

        Parametros
        ----------
        dataphone_msg: type(str) -> Mensaje sin procesar enviado por el datafono.
        Por ejemplo: "..760000000001099..033..40..69..93..."

        Return
        ------
        tuple (bool, str, dict) -> El primer valor representa si es flujo unificado,
        el segundo valor regresa cual es el campo para indicar el tipo de operacion
        (es usado unicamente cuando es flujo unificado), el tercer valor representa
        el mensaje enviado por el datafono pero desensamblado.
        Por ejemplo:
        (
            True, -> es flujo unificado
            "C69", -> campo utilizado para enviar el tipo de operacion
            dict -> {
            'LRC': '\\x02',
            'BCD': '\\x007',
            'DATA': ['33\\x00\\x00', ...],
            'HEADER_FIELDS': ...
        )

        """
        try:
            # Se evalua si el mensaje contiene el campo "CONFIRM_MESSAGE",
            have_field = self.have_field_understood(dataphone_msg)
            disassembled_msg = self.message_rdg.read_message(dataphone_msg, have_field)
        except ValueError as error:
            raise ValueError(str(error))
        # Se ejecuta si no se presenta ningun error.
        else:
            # Se obtiene el cod_trans del desensamble
            cod_transaction = disassembled_msg["HEADER_FIELDS"]["cod_trans"]
            # Del campo cod_trans se conoce si es flujo unificado o no.
            is_unified, field_code = self.business_conf.get_flow_type(cod_transaction)
            return is_unified, field_code, disassembled_msg

    def have_field_understood(self, dataphone_msg):
        """
            Funcion que identifica si el mensaje contiene el campo "CONFIRM_MESSAGE".

            Parametros
            ----------
            dataphone_msg: type(str) -> Mensaje sin procesar enviado por el datafono

            Return
            ------
            bool -> Retorna verdadero (True) si el mensaje cuenta con el campo "CONFIRM_MESSAGE",
            de lo contrario retornara falso (False)
        """
        message_definition = self.business_conf.get_message_definition()
        understoods_items = self.business_conf.get_understoods()
        # Se convierten valores como "06" en hexa "\x06".
        understoods_items = [unhexlify(value) for value in understoods_items]
        structure = message_definition["structure"]
        us_idx = structure.index("CONFIRM_MESSAGE")
        min_idx = sum([message_definition[f]["max_length"]  for f in structure[0:us_idx]])
        max_idx = min_idx + message_definition["CONFIRM_MESSAGE"]["max_length"]
        understood_value = dataphone_msg[min_idx: max_idx]
        return understood_value in understoods_items

    def built_fields(self, data):
        """
        Funcion encargada de relacionar los datos
        de entrada con los campos de una operacion.
        Esto ocurre con todas las operaciones que hagan
        match con la logintud de campos de entrada.

        data: type(list) -> Lista de datos que componen una operacion.

        Return
        ------
        list -> Datos de entrada previamente procesados.
        Cada campo cumple con una longitud y tipo de dato especifico, definido
        en el archivo de configuracion del negocio.
            Por ejemplo:
            [
                ('C33', 'cajero1   '),
                ('C40', '000000080000'),
                ('C41', '000000000000'),
                ...
            ]
        """
        is_cashier_incl = self.user_conf.get_cashier_flag()
        # Se obtiene la operacion enviada por la caja
        operation = self.business_conf.get_operation(data, is_cashier_incl)
        is_list_of_lists = [isinstance(oper, list) for oper in operation].pop()
        # Se construye los campos posibles a enviar
        if(is_list_of_lists):
            temp = list()
            for oper in operation:
                built_fields, _ = self.message_bldg.build_message(data, oper, data[0])
                temp += built_fields
            built_fields = temp
        else:
            built_fields, _ = self.message_bldg.build_message(data, operation, data[0])

        return set(built_fields)

    def bin_discount(self, card_value):
        """
        Funcion utilizada para el descuento bin, se encarga
        de escribir el nro de la tarjeta (card_value) en el
        archivo de salida, espera el tiempo definido en las config.
        de usuario y vuelve a leer los datos de entrada.

        Antes de realizar el return construye los datos de entrada
        con el codigo de campo correspondiente a una operacion.
        """
        input_file = self.user_conf.get_input_file_name()
        output_file = self.user_conf.get_output_file_name()
        time_sleep = self.user_conf.get_sleep_time()
        self.file_action.write_output_data(card_value, output_file)
        sleep(time_sleep)
        data = self.file_action.get_input_data(input_file)
        return self.built_fields(data)
