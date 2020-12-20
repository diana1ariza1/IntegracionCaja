# pylint: disable=superfluous-parens,broad-except,relative-import,old-style-class
# pylint: disable=deprecated-lambda,too-many-instance-attributes
"""
Clase utilizada para la manipulacion y
acceso a la configuracion del negocio
definida en 'business.config.json'.
"""
from logger import get_error_log
class BusinessConfig():
    """
    Clase utilizada para la manipulacion y
    acceso a la configuracion del negocio
    definida en 'business.config.json'.
    """

    def __init__(self, json_data):
        self._set_values(json_data)
        self._error_log = get_error_log()

    def _set_values(self, data_json):
        self._message_definition = data_json["message_definition"]
        self._values_confirm_message = data_json["values_confirm_message"]
        self._flows = data_json["flows"]
        self._data_frame = data_json["data_frame"]
        self._operations = data_json["operations"]
        self._field_structure = data_json["field_structure"]
        self._fields_definition = data_json["fields_definition"]
        return self

    def get_message_definition(self):
        """Devuelve la estructura de un mensaje"""
        return self._message_definition

    def get_understoods(self):
        """Devuelve los valores para el campo understood"""
        return [v for _, v in self._values_confirm_message.iteritems()]

    def get_understood_value(self):
        """
        Se encarga de retornar el valor para indicar
        que el mensaje fue entendido.
        """
        try:
            return self._values_confirm_message["UNDERSTOOD"]
        except KeyError as error:
            raise KeyError("99, No se encontro {} en 'values_confirm_message'".format(error))

    def get_not_understood_value(self):
        """
        Se encarga de retornar el valor para indicar
        que el mensaje no fue entendido.
        """
        try:
            return self._values_confirm_message["NOT_UNDERSTOOD"]
        except KeyError as error:
            raise KeyError("99, No se encontro {} en 'values_confirm_message'".format(error))

    def get_flow_type(self, cod_trans):
        """
        Devuelve el campo utilizado para enviar el campo
        de una operacion, ademas, devuelve si es flujo
        inificado o no unificado.
        De lo contrario retorna una excepcion indicando
        que el codigo transaccion no pertenece a un flujo.
        """
        try:
            is_unified = self._flows[cod_trans]["is_unified"]
            operation_field = self._flows[cod_trans]["operation_field"]
            return is_unified, operation_field
        except KeyError as error:
            msg = "99, No se encontro Cod. Trans. {} en 'flows'".format(error)
            raise KeyError(msg)

    def get_data_frame(self):
        """Devuelve la estructura para el 'campo de datos'"""
        return self._data_frame

    def get_operation(self, data, is_cashier_included):
        """
        Devuelve una operacion acorde a la longitud
        de los datos, tambien, elimina de una operacion
        el campo utilizado para enviar el codigo de cajero
        si este se encuentra deshabilitado.
        """
        try:
            operation_code = data[0]
            length_data = len(data[1:])
            ops = self._operations[operation_code]
            f_d = self.get_fields_definition()

            if not(is_cashier_included):
                for field in sorted(f_d):
                    if(f_d[field]["description"] == "cod_cajero"):
                        remove = lambda f, op: (op, op.remove(f)) if(f in op) else (op, None)
                        ops = [remove(field, op)[0] for op in ops]
                        break

            ops = filter(lambda op: len(op) == length_data, ops)
            if not (ops):
                msg = "99, No existe operacion para el numero de datos de entrada"
                raise IndexError(msg)

            return ops

        except KeyError as _:
            msg = "99, No se encontro operacion '{}'".format(data[0])
            raise IndexError(msg)

    def get_field_structure(self):
        """Devuelve la estructura que debecampo"""
        return self._field_structure

    def get_fields(self, fields_cod):
        """
        Apartir de una lista con los codigos de campos,
        el metodo se encarga de devolver la definicion
        por cada campo.
        """
        try:
            return [(cod, self._fields_definition[cod]) for cod in fields_cod]
        except KeyError as error:
            msg = "99, No se encontro codigo de campo {}".format(str(error))
            if(self._error_log):
                self._error_log.error(msg)
            raise KeyError(msg)

    def get_fields_definition(self):
        """Devuelve la definicion de todos los campos"""
        return self._fields_definition
