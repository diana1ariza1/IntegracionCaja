from unittest import TestCase, main
import logging
from binascii import unhexlify, hexlify
from os import sys, path 
# It's necessary to add the current path to the entry path to help the import process
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from redeco_core.utils import FileActions, BusinessConfig, MessageBuilding, MessageReading

current_path = sys.path[-1]
file_action = None
business_conf = None
message_bldg = None
message_rdg = None

class TestMessageBuilding(TestCase):
    """
    Clase encargada de probar todas las funcionalidades pertenecientes
    a la clase MessageBuilding
    """

    def test_1(self):
        """ Interpretacion del primer mensaje del flujo unificado sin agregar lo siguiente:
                * Campo "CONFIRM_MESSAGE".
                * Se indica al metodo "read_message" que no se incluye campo "CONFIRM_MESSAGE".
            Validaciones:
                * Se valida que la cabecera ("HEADER_FIELDS") sea la misma.
                * Se valida que los campos de datos ("DATA") sean los esperados.
        """
        data = "02003736303030303030303030313039392020301c333300001c343000001c363900001c393300000302"
        data = unhexlify(data)
        result_valid = {'LRC': '\x02', u'BCD': '\x007', u'STX': '\x02', 'ETX': '\x03', 'HEADER_FIELDS': {u'cod_trans': '99', u'indicator': '0', u'req_res': '0', u'cod_res': '  ', u'version': '1', u'transport_header': '6000000000'}, 'DATA': [('C33', ''), ('C40', ''), ('C69', ''), ('C93', '')]}
        business_conf = BusinessConfig(file_action.get_business_config_json())
        message_bldg = MessageBuilding(business_conf)
        message_rdg = MessageReading(business_conf, message_bldg)
        result = message_rdg.read_message(data, False)
        self.assertEqual(result_valid["HEADER_FIELDS"], result["HEADER_FIELDS"])
        self.assertEqual(result_valid["DATA"], result["DATA"])

    def test_2(self):
        """ Interpretacion del primer mensaje del flujo unificado agregando lo siguiente:
                * Campo "CONFIRM_MESSAGE", el primer valor "06" de la variable "data"
                * Se indica al metodo "read_message" que se incluye campo "CONFIRM_MESSAGE".
            Validaciones:
                * Se valida que el campo "CONFIRM_MESSAGE" interpretado sea igual a "\x06".
                * Se valida que le mensaje sea igual a "result_valid".
        """
        data = "0602003736303030303030303030313039392020301c333300001c343000001c363900001c393300000302"
        data = unhexlify(data)
        result_valid = {
            'LRC': '\x02', u'BCD': '\x007',
            'DATA': [('C33', ''), ('C40', ''), ('C69', ''), ('C93', '')],
            'ETX': '\x03', u'CONFIRM_MESSAGE': '\x06', u'STX': '\x02',
            'HEADER_FIELDS': {u'cod_trans': '99', u'indicator': '0', u'req_res': '0', u'cod_res': '  ', u'version': '1', u'transport_header': '6000000000'}}
        business_conf = BusinessConfig(file_action.get_business_config_json())
        message_bldg = MessageBuilding(business_conf)
        message_rdg = MessageReading(business_conf, message_bldg)
        result = message_rdg.read_message(data, True)
        self.assertEqual(result["CONFIRM_MESSAGE"], "\x06")
        self.assertEqual(result_valid, result)

    def test_3(self):
        """ Interpretacion del primer mensaje del flujo unificado agregando lo siguiente:
                * Campo "CONFIRM_MESSAGE", el primer valor "99" de la variable "data"
                * Se indica al metodo "read_message" que se incluye el campo "CONFIRM_MESSAGE".
            Validaciones:
                * Se valida que el campo "CONFIRM_MESSAGE" interpretado sea igual a "\x99".
                * Se valida que en el campo "C69" venga el valor "00001"
                * Se valida que en el campo "C33" venga el valor "Cajero1"
                * Se valida que en el campo "C93" no venga el valor "Cajero1" y "00001"
                * Se valida que le mensaje sea igual a "result_valid".
        """
        data = "9902003736303030303030303030313039392020301c3333000743616a65726f311c343000001c3639000530303030311c393300000302"
        data = unhexlify(data)
        result_valid = {
            'LRC': '\x02', u'BCD': '\x007',
            'DATA': [('C33', 'Cajero1'), ('C40', ''), ('C69', '00001'), ('C93', '')],
            'ETX': '\x03', u'CONFIRM_MESSAGE': '\x99', u'STX': '\x02',
            'HEADER_FIELDS': {u'cod_trans': '99', u'indicator': '0', u'req_res': '0', u'cod_res': '  ', u'version': '1', u'transport_header': '6000000000'}}
        business_conf = BusinessConfig(file_action.get_business_config_json())
        message_bldg = MessageBuilding(business_conf)
        message_rdg = MessageReading(business_conf, message_bldg)
        result = message_rdg.read_message(data, True)
        self.assertEqual(result["CONFIRM_MESSAGE"], "\x99")
        self.assertEqual(result["DATA"][2], ('C69', '00001'))
        self.assertEqual(result["DATA"][0], ('C33', 'Cajero1'))
        self.assertNotEqual(result["DATA"][3], ('C93', 'Cajero1'))
        self.assertNotEqual(result["DATA"][3], ('C93', '00001'))
        self.assertEqual(result_valid, result)

    def test_4(self):
        """ Interpretacion del primer mensaje del flujo unificado sin agregar lo siguiente:
                * Campo "CONFIRM_MESSAGE"
                * Se indica al metodo "read_message" que se incluye el campo "CONFIRM_MESSAGE".
            Validaciones:
                * Se valida que el resultado sea una excepcion
        """
        data = "02003736303030303030303030313039392020301c333300001c343000001c363900001c393300000302"
        data = unhexlify(data)
        business_conf = BusinessConfig(file_action.get_business_config_json())
        message_bldg = MessageBuilding(business_conf)
        message_rdg = MessageReading(business_conf, message_bldg)
        func = message_rdg.read_message
        with self.assertRaises(Exception):  func(data, True)

    def test_5(self):
        """ Interpretacion un mensaje de flujo unificado:
                * Campo "CONFIRM_MESSAGE"
                * Se indica al metodo "read_message" que se incluye el campo "CONFIRM_MESSAGE".
            Validaciones:
                * Se valida que el campo "C33" venga el valor 'kesus@26  '
                * Se valida que el campo "C40" venga el valor '000000015000'
                * Se valida que el campo "C69" venga el valor '00'
                * Se valida que el campo "C93" venga el valor ''
        """
        data = "0602006136303030303030303030313030303030301c3333000a6b6573757340323620201c3430000c3030303030303031353030301c3639000230301c39330000036a"
        data = unhexlify(data)
        result_valid = {'LRC': 'j', u'BCD': '\x00a',
            'DATA': [('C33', 'kesus@26  '), ('C40', '000000015000'), ('C69', '00'), ('C93', '')],
            'ETX': '\x03', u'CONFIRM_MESSAGE': '\x06', u'STX': '\x02',
            'HEADER_FIELDS': {u'cod_trans': '00', u'indicator': '0', u'req_res': '0', u'cod_res': '00', u'version': '1', u'transport_header': '6000000000'}}
        business_conf = BusinessConfig(file_action.get_business_config_json())
        message_bldg = MessageBuilding(business_conf)
        message_rdg = MessageReading(business_conf, message_bldg)
        result = message_rdg.read_message(data, True)
        self.assertTupleEqual(result["DATA"][0],('C33', 'kesus@26  '))
        self.assertTupleEqual(result["DATA"][1],('C40', '000000015000'))
        self.assertTupleEqual(result["DATA"][2],('C69', '00'))
        self.assertTupleEqual(result["DATA"][3],('C93', ''))
        self.assertDictEqual(result_valid, result)

    def test_6(self):
        """ Interpretacion un mensaje de flujo unificado:
                * Campo "CONFIRM_MESSAGE"
                * Se indica al metodo "read_message" que se incluye el campo "CONFIRM_MESSAGE".
            Validaciones:
                * Se valida que el campo "C33" venga el valor 'jesus@26  '
                * Se valida que el campo "C40" venga el valor '000000015000'
                * Se valida que el campo "C69" venga el valor '00'
                * Se valida que el campo "C93" venga el valor ''
        """
        data = "0602006136303030303030303030313030303030301c3333000a6a6573757340323620201c3430000c3030303030303031353030301c3639000230301c39330000036a"
        data = unhexlify(data)
        result_valid = {'LRC': 'j', u'BCD': '\x00a',
            'DATA': [('C33', 'jesus@26  '), ('C40', '000000015000'), ('C69', '00'), ('C93', '')],
            'ETX': '\x03', u'CONFIRM_MESSAGE': '\x06', u'STX': '\x02',
            'HEADER_FIELDS': {u'cod_trans': '00', u'indicator': '0', u'req_res': '0', u'cod_res': '00', u'version': '1', u'transport_header': '6000000000'}}
        business_conf = BusinessConfig(file_action.get_business_config_json())
        message_bldg = MessageBuilding(business_conf)
        message_rdg = MessageReading(business_conf, message_bldg)
        result = message_rdg.read_message(data, True)
        self.assertTupleEqual(result["DATA"][0],('C33', 'jesus@26  '))
        self.assertTupleEqual(result["DATA"][1],('C40', '000000015000'))
        self.assertTupleEqual(result["DATA"][2],('C69', '00'))
        self.assertTupleEqual(result["DATA"][3],('C93', ''))
        self.assertDictEqual(result_valid, result)

    def test_7(self):
        """ Interpretacion un mensaje de flujo unificado:
                * Campo "CONFIRM_MESSAGE"
                * Se indica al metodo "read_message" que se incluye el campo "CONFIRM_MESSAGE".
            Validaciones:
                * Se valida que el campo "C30" venga el valor '430366**8180'
                * Se valida que el campo "C40" venga el valor '000000015000'
                * Se valida que el campo "C81" venga el valor '1152'
                * Por ultimo se valida todo el mensaje
        """
        data = "0602022336303030303030303030313130303030301c3030000230311c303100060000000000001c3330000c3433303336362a2a383138301c3333000a6a6573757340323620201c3334000243521c3335000a564953412020202020201c3430000c3030303030303031353030301c3431000c3030303030303030323430301c3432000c3030303030303132333435361c363500060000000000001c373700060000000000001c3738000854414253303031361c3739001730303130323033303430000000000000000000000000001c383000063230303431331c38310004313135320333"
        data = unhexlify(data)
        result_valid = {'LRC': '3', u'BCD': '\x02#',
            'DATA': [('C00', '01'), ('C01', '\x00\x00\x00\x00\x00\x00'), ('C30', '430366**8180'), ('C33', 'jesus@26  '),
                    ('C34', 'CR'), ('C35', 'VISA      '), ('C40', '000000015000'), ('C41', '000000002400'), ('C42', '000000123456'),
                    ('C65', '\x00\x00\x00\x00\x00\x00'), ('C77', '\x00\x00\x00\x00\x00\x00'), ('C78', 'TABS0016'),
                    ('C79', '0010203040\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'), ('C80', '200413'), ('C81', '1152')],
            'ETX': '\x03', u'CONFIRM_MESSAGE': '\x06', u'STX': '\x02',
            'HEADER_FIELDS': {u'cod_trans': '00', u'indicator': '0', u'req_res': '1', u'cod_res': '00', u'version': '1', u'transport_header': '6000000000'}}
        business_conf = BusinessConfig(file_action.get_business_config_json())
        message_bldg = MessageBuilding(business_conf)
        message_rdg = MessageReading(business_conf, message_bldg)
        result = message_rdg.read_message(data, True)
        self.assertTupleEqual(result["DATA"][2], ('C30', '430366**8180'))
        self.assertTupleEqual(result["DATA"][6], ('C40', '000000015000'))
        self.assertTupleEqual(result["DATA"][-1], ('C81', '1152'))
        self.assertDictEqual(result_valid, result)

    def test_8(self):
        """ Interpretacion un mensaje de flujo unificado:
                * Campo "CONFIRM_MESSAGE"
                * Se indica al metodo "read_message" que se incluye el campo "CONFIRM_MESSAGE".
                * Se cambian el valor 'STX' por '00'
            Validaciones:
                * Se valida que el metodo envie una excepcion.
        """
        data = "0600022336303030303030303030313130303030301c3030000230311c303100060000000000001c3330000c3433303336362a2a383138301c3333000a6a6573757340323620201c3334000243521c3335000a564953412020202020201c3430000c3030303030303031353030301c3431000c3030303030303030323430301c3432000c3030303030303132333435361c363500060000000000001c373700060000000000001c3738000854414253303031361c3739001730303130323033303430000000000000000000000000001c383000063230303431331c38310004313135320333"
        data = unhexlify(data)
        business_conf = BusinessConfig(file_action.get_business_config_json())
        message_bldg = MessageBuilding(business_conf)
        message_rdg = MessageReading(business_conf, message_bldg)
        func = message_rdg.read_message
        with self.assertRaises(ValueError): func(data, True)

    def test_9(self):
        """ Interpretacion un mensaje de flujo unificado:
                * Campo "CONFIRM_MESSAGE"
                * Se indica al metodo "read_message" que se incluye el campo "CONFIRM_MESSAGE".
                * Se cambian el valor 'ETX' por '00'
            Validaciones:
                * Se valida que el metodo envie una excepcion.
        """
        data = "0600022336303030303030303030313130303030301c3030000230311c303100060000000000001c3330000c3433303336362a2a383138301c3333000a6a6573757340323620201c3334000243521c3335000a564953412020202020201c3430000c3030303030303031353030301c3431000c3030303030303030323430301c3432000c3030303030303132333435361c363500060000000000001c373700060000000000001c3738000854414253303031361c3739001730303130323033303430000000000000000000000000001c383000063230303431331c38310004313135320033"
        data = unhexlify(data)
        business_conf = BusinessConfig(file_action.get_business_config_json())
        message_bldg = MessageBuilding(business_conf)
        message_rdg = MessageReading(business_conf, message_bldg)
        func = message_rdg.read_message
        with self.assertRaises(ValueError): func(data, True)

    def test_10(self):
        """ Interpretacion un mensaje de flujo unificado:
            Validaciones:
                * Se valida que los diccionarios sean iguales
        """
        data = "0602006136303030303030303030313030303030301c3333000a313032323334352020201c3430000c3030303030303031303030301c3639000230301c393300000342"
        data = unhexlify(data)
        result_valid = {'LRC': 'B', u'BCD': '\x00a', u'STX': '\x02',
        'DATA': [('C33', '1022345   '), ('C40', '000000010000'), ('C69', '00'), ('C93', '')],
        'ETX': '\x03', u'CONFIRM_MESSAGE': '\x06', 'HEADER_FIELDS': {u'cod_trans': '00', u'indicator': '0', u'req_res': '0', u'cod_res': '00', u'version': '1', u'transport_header': '6000000000'}}
        business_conf = BusinessConfig(file_action.get_business_config_json())
        message_bldg = MessageBuilding(business_conf)
        message_rdg = MessageReading(business_conf, message_bldg)
        result = message_rdg.read_message(data, True)
        self.assertDictEqual(result_valid, result)

    def test_11(self):
        """ Interpretacion un mensaje de flujo unificado:
            Validaciones:
                * Se valida que los diccionarios no sean iguales
        """
        data = "0602007436303030303030303030313030302020301c313100001c3330000c3630363037362a2a303331351c333300001c343000001c343100001c343200001c343300001c343400001c363600000355"
        data = unhexlify(data)
        result_valid = {'LRC': 'B', u'BCD': '\x00a', u'STX': '\x02',
        'DATA': [('C33', '1022345   '), ('C40', '000000010000'), ('C69', '00'), ('C93', '')],
        'ETX': '\x03', u'CONFIRM_MESSAGE': '\x06', 'HEADER_FIELDS': {u'cod_trans': '00', u'indicator': '0', u'req_res': '0', u'cod_res': '00', u'version': '1', u'transport_header': '6000000000'}}
        business_conf = BusinessConfig(file_action.get_business_config_json())
        message_bldg = MessageBuilding(business_conf)
        message_rdg = MessageReading(business_conf, message_bldg)
        result = message_rdg.read_message(data, True)
        self.assertNotEqual(result, result_valid)

    def test_12(self):
        """ Interpretacion un mensaje de flujo unificado:
            Validaciones:
                * Se valida que los diccionarios sean iguales
        """
        data = "0602007436303030303030303030313030302020301c313100001c3330000c3630363037362a2a303331351c333300001c343000001c343100001c343200001c343300001c343400001c363600000355"
        data = unhexlify(data)
        result_valid = {'LRC': 'U', u'BCD': '\x00t',
        'DATA': [('C11', ''), ('C30', '606076**0315'), ('C33', ''), ('C40', ''), ('C41', ''), ('C42', ''), ('C43', ''), ('C44', ''), ('C66', '')],
        'ETX': '\x03', u'CONFIRM_MESSAGE': '\x06', u'STX': '\x02',
        'HEADER_FIELDS': {u'cod_trans': '00', u'indicator': '0', u'req_res': '0', u'cod_res': '  ', u'version': '1', u'transport_header': '6000000000'}
        }
        business_conf = BusinessConfig(file_action.get_business_config_json())
        message_bldg = MessageBuilding(business_conf)
        message_rdg = MessageReading(business_conf, message_bldg)
        result = message_rdg.read_message(data, True)
        self.assertDictEqual(result, result_valid)

    def test_13(self):
        """ Interpretacion un mensaje de flujo unificado:
            Validaciones:
                * Se valida que los diccionarios sean iguales
        """
        data = "0602013036303030303030303030313030303030301c313100001c333000001c3333000a313032323334352020201c3430000c3030303030303031303030301c3431000c3030303030303030303030301c3432000c3030303030303030303030301c343300001c3434000c3030303030303030303030301c3636000a4641435430310a2020200333"
        data = unhexlify(data)
        result_valid = {'LRC': '3', u'BCD': '\x010',
        'DATA': [('C11', ''), ('C30', ''), ('C33', '1022345   '), ('C40', '000000010000'), ('C41', '000000000000'), ('C42', '000000000000'), ('C43', ''), ('C44', '000000000000'), ('C66', 'FACT01\n   ')],
        'ETX': '\x03', u'CONFIRM_MESSAGE': '\x06', u'STX': '\x02',
        'HEADER_FIELDS': {u'cod_trans': '00', u'indicator': '0', u'req_res': '0', u'cod_res': '00', u'version': '1', u'transport_header': '6000000000'}}
        business_conf = BusinessConfig(file_action.get_business_config_json())
        message_bldg = MessageBuilding(business_conf)
        message_rdg = MessageReading(business_conf, message_bldg)
        result = message_rdg.read_message(data, True)
        self.assertDictEqual(result, result_valid)

    def test_14(self):
        """ Interpretacion un mensaje de flujo unificado:
            Validaciones:
                * Se valida que los diccionarios sean iguales
        """
        data = "0602022336303030303030303030313130303030301c3030000230311c303100060000000000001c3330000c3630363037362a2a303331351c3333000a313032323334352020201c3334000241481c3335000a534f4445584f202020201c3430000c3030303030303031303030301c3431000c3030303030303030303030301c3432000c3030303030303030303030301c363500060000000000001c373700060000000000001c3738000854414253303031361c3739001730303130323033303430000000000000000000000000001c383000063230303431341c3831000430393337030b"
        data = unhexlify(data)
        result_valid = {'LRC': '\x0b', u'BCD': '\x02#',
        'DATA': [('C00', '01'), ('C01', '\x00\x00\x00\x00\x00\x00'), ('C30', '606076**0315'), ('C33', '1022345   '), ('C34', 'AH'), ('C35', 'SODEXO    '), ('C40', '000000010000'), ('C41', '000000000000'), ('C42', '000000000000'), ('C65', '\x00\x00\x00\x00\x00\x00'), ('C77', '\x00\x00\x00\x00\x00\x00'), ('C78', 'TABS0016'), ('C79', '0010203040\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'), ('C80', '200414'), ('C81', '0937')],
        'ETX': '\x03', u'CONFIRM_MESSAGE': '\x06', u'STX': '\x02',
        'HEADER_FIELDS': {u'cod_trans': '00', u'indicator': '0', u'req_res': '1', u'cod_res': '00', u'version': '1', u'transport_header': '6000000000'}}
        business_conf = BusinessConfig(file_action.get_business_config_json())
        message_bldg = MessageBuilding(business_conf)
        message_rdg = MessageReading(business_conf, message_bldg)
        result = message_rdg.read_message(data, True)
        self.assertDictEqual(result, result_valid)

    def test_15(self):
        """ Interpretacion un mensaje de flujo unificado:
            Validaciones:
                * Se valida que los diccionarios no sean iguales
        """
        data = "0602022336303030303030303030313130303030301c3030000230311c303100060000000000001c3330000c3630363037362a2a303331351c3333000a313032323334352020201c3334000241481c3335000a534f4445584f202020201c3430000c3030303030303031303030301c3431000c3030303030303030303030301c3432000c3030303030303030303030301c363500060000000000001c373700060000000000001c3738000854414253303031361c3739001730303130323033303430000000000000000000000000001c383000063230303431341c3831000430393337030b"
        data = unhexlify(data)
        business_conf = BusinessConfig(file_action.get_business_config_json())
        message_bldg = MessageBuilding(business_conf)
        message_rdg = MessageReading(business_conf, message_bldg)
        func = message_rdg.read_message
        with self.assertRaises(ValueError): func(data, False)

    def test_16(self):
        """ Interpretacion un mensaje de flujo unificado:
            Validaciones:
                * Se valida que los diccionarios sean iguales
        """
        data = "0602006136303030303030303030313030303030301c3333000a323220202020202020201c3430000c3030303030303031353030301c3639000230301c393300000354"
        data = unhexlify(data)
        result_valid = {'LRC': 'T', u'BCD': '\x00a',
        'DATA': [('C33', '22        '), ('C40', '000000015000'), ('C69', '00'), ('C93', '')],
        'ETX': '\x03', u'CONFIRM_MESSAGE': '\x06', u'STX': '\x02',
        'HEADER_FIELDS': {u'cod_trans': '00', u'indicator': '0', u'req_res': '0', u'cod_res': '00', u'version': '1', u'transport_header': '6000000000'}}
        business_conf = BusinessConfig(file_action.get_business_config_json())
        message_bldg = MessageBuilding(business_conf)
        message_rdg = MessageReading(business_conf, message_bldg)
        result = message_rdg.read_message(data, True)
        self.assertDictEqual(result, result_valid)

    def test_17(self):
        """ Interpretacion un mensaje de flujo unificado:
            Validaciones:
                * Se valida que los diccionarios sean iguales
        """
        data = "0602013036303030303030303030313030303030301c313100001c333000001c3333000a323220202020202020201c3430000c3030303030303031353030301c3431000c3030303030303030303030301c3432000c3030303030303030303030301c343300001c3434000c3030303030303030303030301c3636000a4641435430310a2020200325"
        data = unhexlify(data)
        result_valid = {'LRC': '%', u'BCD': '\x010',
        'DATA': [('C11', ''), ('C30', ''), ('C33', '22        '), ('C40', '000000015000'), ('C41', '000000000000'), ('C42', '000000000000'), ('C43', ''), ('C44', '000000000000'), ('C66', 'FACT01\n   ')],
        'ETX': '\x03', u'CONFIRM_MESSAGE': '\x06', u'STX': '\x02',
        'HEADER_FIELDS': {u'cod_trans': '00', u'indicator': '0', u'req_res': '0', u'cod_res': '00', u'version': '1', u'transport_header': '6000000000'}}
        business_conf = BusinessConfig(file_action.get_business_config_json())
        message_bldg = MessageBuilding(business_conf)
        message_rdg = MessageReading(business_conf, message_bldg)
        result = message_rdg.read_message(data, True)
        self.assertDictEqual(result, result_valid)

    def test_18(self):
        """ Interpretacion un mensaje de flujo unificado:
            Validaciones:
                * Se valida que los diccionarios sean iguales
        """
        data = "0602022336303030303030303030313130303030301c3030000230311c303100060000000000001c3330000c3433303336362a2a383138301c3333000a323220202020202020201c3334000243521c3335000a564953412020202020201c3430000c3030303030303031353030301c3431000c3030303030303030303030301c3432000c3030303030303030303030301c363500060000000000001c373700060000000000001c3738000854414253303031361c3739001730303130323033303430000000000000000000000000001c383000063230303431341c3831000431313534030d"
        data = unhexlify(data)
        result_valid = {'LRC': '\r', u'BCD': '\x02#',
        'DATA': [('C00', '01'), ('C01', '\x00\x00\x00\x00\x00\x00'), ('C30', '430366**8180'), ('C33', '22        '), ('C34', 'CR'), ('C35', 'VISA      '), ('C40', '000000015000'), ('C41', '000000000000'), ('C42', '000000000000'), ('C65', '\x00\x00\x00\x00\x00\x00'), ('C77', '\x00\x00\x00\x00\x00\x00'), ('C78', 'TABS0016'), ('C79', '0010203040\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'), ('C80', '200414'), ('C81', '1154')], 
        'ETX': '\x03', u'CONFIRM_MESSAGE': '\x06',u'STX': '\x02',
        'HEADER_FIELDS': {u'cod_trans': '00', u'indicator': '0', u'req_res': '1', u'cod_res': '00', u'version': '1', u'transport_header': '6000000000'}}
        business_conf = BusinessConfig(file_action.get_business_config_json())
        message_bldg = MessageBuilding(business_conf)
        message_rdg = MessageReading(business_conf, message_bldg)
        result = message_rdg.read_message(data, True)
        self.assertDictEqual(result, result_valid)

    def test_19(self):
        """ Interpretacion un mensaje de flujo unificado:
            Validaciones:
                * Se valida que los diccionarios sean iguales
        """
        data = "0602022336303030303030303030313130303030301c3030000230311c303100060000000000001c3330000c3433303336362a2a383138301c3333000a323220202020202020201c3334000243521c3335000a564953412020202020201c3430000c3030303030303031353030301c3431000c3030303030303030313230301c3432000c3030303030303030303030301c363500060000000000001c373700060000000000001c3738000854414253303031361c3739001730303130323033303430000000000000000000000000001c383000063230303431341c3831000431323332030d"
        data = unhexlify(data)
        result_valid = {'LRC': '\r', u'BCD': '\x02#',
        'DATA': [('C00', '01'), ('C01', '\x00\x00\x00\x00\x00\x00'), ('C30', '430366**8180'), ('C33','22        '), ('C34', 'CR'), ('C35', 'VISA      '), ('C40', '000000015000'), ('C41', '000000001200'), ('C42', '000000000000'), ('C65', '\x00\x00\x00\x00\x00\x00'), ('C77', '\x00\x00\x00\x00\x00\x00'), ('C78', 'TABS0016'), ('C79', '0010203040\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'), ('C80', '200414'), ('C81', '1232')],
        'ETX': '\x03', u'CONFIRM_MESSAGE': '\x06', u'STX': '\x02',
        'HEADER_FIELDS': {u'cod_trans':'00', u'indicator': '0', u'req_res': '1', u'cod_res': '00', u'version': '1', u'transport_header': '6000000000'}}
        business_conf = BusinessConfig(file_action.get_business_config_json())
        message_bldg = MessageBuilding(business_conf)
        message_rdg = MessageReading(business_conf, message_bldg)
        result = message_rdg.read_message(data, True)
        self.assertDictEqual(result, result_valid)

    def test_20(self):
        """ Interpretacion un mensaje de flujo unificado:
            Validaciones:
                * Se valida que los diccionarios sean iguales
        """
        data = "0602013036303030303030303030313030303030301c313100001c333000001c3333000a323220202020202020201c3430000c3030303030303031353030301c3431000c3030303030303030313230301c3432000c3030303030303030303030301c343300001c3434000c3030303030303030303030301c3636000a4641435430310a2020200326"
        data = unhexlify(data)
        result_valid = {'LRC': '&', u'BCD': '\x010',
        'DATA': [('C11', ''), ('C30', ''), ('C33', '22        '), ('C40', '000000015000'), ('C41', '000000001200'), ('C42', '000000000000'), ('C43', ''), ('C44', '000000000000'), ('C66', 'FACT01\n   ')],
        'ETX': '\x03', u'CONFIRM_MESSAGE': '\x06', u'STX': '\x02',
        'HEADER_FIELDS': {u'cod_trans': '00', u'indicator': '0', u'req_res': '0', u'cod_res': '00', u'version': '1', u'transport_header': '6000000000'}}
        business_conf = BusinessConfig(file_action.get_business_config_json())
        message_bldg = MessageBuilding(business_conf)
        message_rdg = MessageReading(business_conf, message_bldg)
        result = message_rdg.read_message(data, True)
        self.assertDictEqual(result, result_valid)

    def test_21(self):
        """ Interpretacion un mensaje de flujo unificado:
            Validaciones:
                * Se valida que los diccionarios sean iguales
        """
        data = "0602013036303030303030303030313030303030301c313100001c333000001c3333000a323220202020202020201c3430000c3030303030303031353030301c3431000c3030303030303030303030301c3432000c3030303030303030303030301c343300001c3434000c3030303030303030303630301c3636000a4641435430310a2020200323"
        data = unhexlify(data)
        result_valid = {'LRC': '#', u'BCD': '\x010',
        'DATA': [('C11', ''), ('C30', ''), ('C33', '22        '), ('C40', '000000015000'), ('C41', '000000000000'), ('C42', '000000000000'), ('C43', ''), ('C44', '000000000600'), ('C66', 'FACT01\n   ')],
        'ETX': '\x03', u'CONFIRM_MESSAGE': '\x06', u'STX': '\x02',
        'HEADER_FIELDS': {u'cod_trans': '00', u'indicator': '0', u'req_res': '0', u'cod_res': '00', u'version': '1', u'transport_header': '6000000000'}}
        business_conf = BusinessConfig(file_action.get_business_config_json())
        message_bldg = MessageBuilding(business_conf)
        message_rdg = MessageReading(business_conf, message_bldg)
        result = message_rdg.read_message(data, True)
        self.assertDictEqual(result, result_valid)

    def test_22(self):
        """ Interpretacion un mensaje de flujo unificado:
            Validaciones:
                * Se valida que los diccionarios sean iguales
        """
        data = "0602022336303030303030303030313130303030301c3030000230311c303100060000000000001c3330000c3433303336362a2a383138301c3333000a323220202020202020201c3334000243521c3335000a564953412020202020201c3430000c3030303030303031353030301c3431000c3030303030303030303030301c3432000c3030303030303030303030301c363500060000000000001c373700060000000000001c3738000854414253303031361c3739001730303130323033303430000000000000000000000000001c383000063230303431341c38310004313235330309"
        data = unhexlify(data)
        result_valid = {'LRC': '\t', u'BCD': '\x02#',
        'DATA': [('C00', '01'), ('C01', '\x00\x00\x00\x00\x00\x00'), ('C30', '430366**8180'), ('C33', '22        '), ('C34', 'CR'), ('C35', 'VISA      '), ('C40', '000000015000'), ('C41', '000000000000'), ('C42', '000000000000'), ('C65', '\x00\x00\x00\x00\x00\x00'), ('C77', '\x00\x00\x00\x00\x00\x00'), ('C78', 'TABS0016'), ('C79', '0010203040\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'), ('C80', '200414'), ('C81', '1253')],
        'ETX': '\x03', u'CONFIRM_MESSAGE': '\x06', u'STX': '\x02',
        'HEADER_FIELDS': {u'cod_trans': '00', u'indicator': '0', u'req_res': '1', u'cod_res': '00', u'version': '1', u'transport_header': '6000000000'}}
        business_conf = BusinessConfig(file_action.get_business_config_json())
        message_bldg = MessageBuilding(business_conf)
        message_rdg = MessageReading(business_conf, message_bldg)
        result = message_rdg.read_message(data, True)
        self.assertDictEqual(result, result_valid)

    def test_22(self):
        """ Interpretacion un mensaje de flujo unificado:
            Validaciones:
                * Se valida que los diccionarios sean iguales
        """
        data = "0602013036303030303030303030313030303030301c313100001c333000001c3333000a323220202020202020201c3430000c3030303030303033303030301c3431000c3030303030303030313230301c3432000c3030303030303030383230301c343300001c3434000c3030303030303030303630301c3636000a4641435430310a202020032d"
        data = unhexlify(data)
        result_valid = {'LRC': '-', u'BCD': '\x010', 
        'DATA': [('C11', ''), ('C30', ''), ('C33', '22        '), ('C40', '000000030000'), ('C41', '000000001200'), ('C42', '000000008200'), ('C43', ''), ('C44', '000000000600'), ('C66', 'FACT01\n   ')],
        'ETX': '\x03', u'CONFIRM_MESSAGE': '\x06', u'STX': '\x02',
        'HEADER_FIELDS': {u'cod_trans': '00', u'indicator': '0', u'req_res': '0', u'cod_res': '00', u'version': '1', u'transport_header': '6000000000'}}
        business_conf = BusinessConfig(file_action.get_business_config_json())
        message_bldg = MessageBuilding(business_conf)
        message_rdg = MessageReading(business_conf, message_bldg)
        result = message_rdg.read_message(data, True)
        self.assertDictEqual(result, result_valid)

    def test_23(self):
        """ Interpretacion un mensaje de flujo unificado:
            Validaciones:
                * Se valida que los diccionarios sean iguales
        """
        data = "0602022336303030303030303030313130303030301c3030000230311c303100060000000000001c3330000c3433303336362a2a383138301c3333000a323220202020202020201c3334000230301c3335000a564953412020202020201c3430000c3030303030303033303030301c3431000c3030303030303132303030301c3432000c3030303030303832303030301c363500063030303134331c373700060000000000001c3738000854414253303031361c3739001730303130323033303430000000000000000000000000001c383000063230303431341c38310004313331310317"
        data = unhexlify(data)
        result_valid = {'LRC': '\x17', u'BCD': '\x02#',
        'DATA': [('C00', '01'), ('C01', '\x00\x00\x00\x00\x00\x00'), ('C30', '430366**8180'), ('C33', '22        '), ('C34', '00'), ('C35', 'VISA      '), ('C40', '000000030000'), ('C41', '000000120000'), ('C42', '000000820000'), ('C65', '000143'), ('C77', '\x00\x00\x00\x00\x00\x00'), ('C78', 'TABS0016'), ('C79', '0010203040\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'), ('C80', '200414'), ('C81', '1311')],
        'ETX': '\x03', u'CONFIRM_MESSAGE': '\x06', u'STX': '\x02',
        'HEADER_FIELDS': {u'cod_trans': '00', u'indicator': '0', u'req_res': '1', u'cod_res': '00', u'version': '1', u'transport_header': '6000000000'}}
        business_conf = BusinessConfig(file_action.get_business_config_json())
        message_bldg = MessageBuilding(business_conf)
        message_rdg = MessageReading(business_conf, message_bldg)
        result = message_rdg.read_message(data, True)
        self.assertDictEqual(result, result_valid)

    def test_24(self):
        """ Interpretacion un mensaje de flujo unificado:
            Validaciones:
                * Se valida que los diccionarios sean iguales
        """
        data = "0602013036303030303030303030313030303030301c313100001c333000001c3333000a323220202020202020201c3430000c3030303030323030303030311c3431000c3030303030303030313230301c3432000c3030303030303030383230301c343300001c3434000c3030303030303030303630301c3636000a4641435430310a202020032d"
        data = unhexlify(data)
        result_valid = {'LRC': '-', u'BCD': '\x010',
        'DATA': [('C11', ''), ('C30', ''), ('C33', '22        '), ('C40', '000002000001'), ('C41', '000000001200'), ('C42', '000000008200'), ('C43', ''), ('C44', '000000000600'), ('C66', 'FACT01\n   ')],
        'ETX': '\x03', u'CONFIRM_MESSAGE': '\x06', u'STX': '\x02',
        'HEADER_FIELDS': {u'cod_trans': '00', u'indicator': '0', u'req_res': '0', u'cod_res': '00', u'version': '1', u'transport_header': '6000000000'}}
        business_conf = BusinessConfig(file_action.get_business_config_json())
        message_bldg = MessageBuilding(business_conf)
        message_rdg = MessageReading(business_conf, message_bldg)
        result = message_rdg.read_message(data, True)
        self.assertDictEqual(result, result_valid)

    def test_25(self):
        """ Interpretacion un mensaje de flujo unificado:
            Validaciones:
                * Se valida que los diccionarios sean iguales
        """
        data = "0602022336303030303030303030313130303030301c3030000230311c303100060000000000001c3330000c3433303336362a2a383138301c3333000a323220202020202020201c3334000230301c3335000a564953412020202020201c3430000c3030303030323030303030311c3431000c3030303030303132303030301c3432000c3030303030303832303030301c363500063030303134341c373700060000000000001c3738000854414253303031361c3739001730303130323033303430000000000000000000000000001c383000063230303431341c38310004313332350317"
        data = unhexlify(data)
        result_valid = {'LRC': '\x17', u'BCD': '\x02#',
        'DATA': [('C00', '01'), ('C01', '\x00\x00\x00\x00\x00\x00'), ('C30', '430366**8180'), ('C33', '22        '), ('C34', '00'), ('C35', 'VISA      '), ('C40', '000002000001'), ('C41', '000000120000'), ('C42', '000000820000'), ('C65', '000144'), ('C77', '\x00\x00\x00\x00\x00\x00'), ('C78', 'TABS0016'), ('C79', '0010203040\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'), ('C80', '200414'), ('C81', '1325')],
        'ETX': '\x03', u'CONFIRM_MESSAGE': '\x06', u'STX': '\x02',
        'HEADER_FIELDS': {u'cod_trans': '00', u'indicator': '0', u'req_res': '1', u'cod_res': '00', u'version': '1', u'transport_header': '6000000000'}}
        business_conf = BusinessConfig(file_action.get_business_config_json())
        message_bldg = MessageBuilding(business_conf)
        message_rdg = MessageReading(business_conf, message_bldg)
        result = message_rdg.read_message(data, True)
        self.assertDictEqual(result, result_valid)

    def test_26(self):
        """ Interpretacion un mensaje de flujo unificado:
            Validaciones:
                * Se valida que los diccionarios sean iguales
        """
        data = "0602014236303030303030303030313030303030301c313100001c333000001c3333000a43616a65726f312020201c3430000c3030303030303031303030301c3431000c3030303030303030313230301c3432000c3030303030303030303830301c3433000c3030303030303030313030301c3434000c3030303030303030323030301c3636000a32303030202020202020034e"
        data = unhexlify(data)
        result_valid = {'LRC': 'N', u'BCD': '\x01B',
        'DATA': [('C11', ''), ('C30', ''), ('C33', 'Cajero1   '), ('C40', '000000010000'), ('C41', '000000001200'), ('C42', '000000000800'), ('C43', '000000001000'), ('C44', '000000002000'), ('C66', '2000      ')],
        'ETX': '\x03', u'CONFIRM_MESSAGE': '\x06', u'STX': '\x02',
        'HEADER_FIELDS': {u'cod_trans': '00', u'indicator': '0', u'req_res': '0', u'cod_res': '00', u'version': '1', u'transport_header': '6000000000'}}
        business_conf = BusinessConfig(file_action.get_business_config_json())
        message_bldg = MessageBuilding(business_conf)
        message_rdg = MessageReading(business_conf, message_bldg)
        result = message_rdg.read_message(data, True)
        self.assertDictEqual(result, result_valid)

    def test_27(self):
        """ Interpretacion un mensaje de flujo unificado:
            Validaciones:
                * Se valida que los diccionarios sean iguales
        """
        data = "0602024036303030303030303030313130303030301c3030000230311c303100060000000000001c3330000c3430393835312a2a323238311c3333000a43616a65726f312020201c3334000243431c3335000a562e454c454354524f4e1c3430000c3030303030303031303030301c3431000c3030303030303030313230301c3432000c3030303030303030303830301c3433000c3030303030303030313030301c363500060000000000001c373700060000000000001c3738000854414253303031361c3739001730303130323033303430000000000000000000000000001c383000063230303431341c38310004313832380334"
        data = unhexlify(data)
        result_valid = {'LRC': '4', u'BCD': '\x02@',
        'DATA': [('C00', '01'), ('C01', '\x00\x00\x00\x00\x00\x00'), ('C30', '409851**2281'), ('C33', 'Cajero1   '), ('C34', 'CC'), ('C35', 'V.ELECTRON'), ('C40', '000000010000'), ('C41', '000000001200'), ('C42', '000000000800'), ('C43', '000000001000'), ('C65', '\x00\x00\x00\x00\x00\x00'), ('C77', '\x00\x00\x00\x00\x00\x00'), ('C78', 'TABS0016'), ('C79', '0010203040\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'), ('C80', '200414'), ('C81', '1828')],
        'ETX': '\x03', u'CONFIRM_MESSAGE': '\x06', u'STX': '\x02',
        'HEADER_FIELDS': {u'cod_trans': '00', u'indicator': '0', u'req_res': '1', u'cod_res': '00', u'version': '1', u'transport_header': '6000000000'}}
        business_conf = BusinessConfig(file_action.get_business_config_json())
        message_bldg = MessageBuilding(business_conf)
        message_rdg = MessageReading(business_conf, message_bldg)
        result = message_rdg.read_message(data, True)
        self.assertDictEqual(result, result_valid)

    def test_28(self):
        """ Interpretacion un mensaje de flujo unificado:
            Validaciones:
                * Se valida que los diccionarios sean iguales
        """
        data = "0602005136303030303030303030313030303030301c333300001c3430000c3030303030303030383030301c3639000230301c393300000362"
        data = unhexlify(data)
        result_valid = {'LRC': 'b', u'BCD': '\x00Q',
        'DATA': [('C33', ''), ('C40', '000000008000'), ('C69', '00'), ('C93', '')],
        'ETX': '\x03', u'CONFIRM_MESSAGE': '\x06',u'STX': '\x02',
        'HEADER_FIELDS': {u'cod_trans': '00', u'indicator': '0', u'req_res': '0', u'cod_res': '00', u'version': '1', u'transport_header': '6000000000'}}
        business_conf = BusinessConfig(file_action.get_business_config_json())
        message_bldg = MessageBuilding(business_conf)
        message_rdg = MessageReading(business_conf, message_bldg)
        result = message_rdg.read_message(data, True)
        self.assertDictEqual(result, result_valid)

    def test_29(self):
        """ Interpretacion un mensaje de flujo unificado:
            Validaciones:
                * Se valida que los diccionarios sean iguales
        """
        data = "0602007436303030303030303030313030302020301c313100001c3330000c3430393835312a2a323238311c333300001c343000001c343100001c343200001c343300001c343400001c36360000035b"
        data = unhexlify(data)
        result_valid = {'LRC': '[', u'BCD': '\x00t',
        'DATA': [('C11', ''), ('C30', '409851**2281'), ('C33', ''), ('C40', ''), ('C41', ''), ('C42', ''), ('C43', ''), ('C44', ''), ('C66', '')],
        'ETX': '\x03', u'CONFIRM_MESSAGE': '\x06', u'STX': '\x02',
        'HEADER_FIELDS': {u'cod_trans': '00', u'indicator': '0', u'req_res': '0', u'cod_res': '  ', u'version': '1', u'transport_header': '6000000000'}}
        business_conf = BusinessConfig(file_action.get_business_config_json())
        message_bldg = MessageBuilding(business_conf)
        message_rdg = MessageReading(business_conf, message_bldg)
        result = message_rdg.read_message(data, True)
        self.assertDictEqual(result, result_valid)

    def test_30(self):
        """ Interpretacion un mensaje de flujo unificado:
            Validaciones:
                * Se valida que los diccionarios sean iguales
        """
        data = "0602012036303030303030303030313030303030301c313100001c333000001c333300001c3430000c3030303030303030383030301c3431000c3030303030303030313230301c3432000c3030303030303030303830301c343300001c3434000c3030303030303030313030301c3636000a46414354555241310a20034f"
        data = unhexlify(data)
        result_valid = {'LRC': 'O', u'BCD': '\x01 ',
        'DATA': [('C11', ''), ('C30', ''), ('C33', ''), ('C40', '000000008000'), ('C41', '000000001200'), ('C42', '000000000800'), ('C43', ''), ('C44', '000000001000'), ('C66', 'FACTURA1\n ')],
        'ETX': '\x03', u'CONFIRM_MESSAGE': '\x06', u'STX': '\x02',
        'HEADER_FIELDS': {u'cod_trans': '00', u'indicator': '0', u'req_res': '0', u'cod_res': '00', u'version': '1', u'transport_header': '6000000000'}}
        business_conf = BusinessConfig(file_action.get_business_config_json())
        message_bldg = MessageBuilding(business_conf)
        message_rdg = MessageReading(business_conf, message_bldg)
        result = message_rdg.read_message(data, True)
        self.assertDictEqual(result, result_valid)

    def test_31(self):
        """ Interpretacion un mensaje de flujo unificado:
            Validaciones:
                * Se valida que los diccionarios sean iguales
        """
        data = "0602022336303030303030303030313130303030301c3030000230311c303100060000000000001c3330000c3430393835312a2a323238311c3333000a202020202020202020201c3334000241481c3335000a562e454c454354524f4e1c3430000c3030303030303030383030301c3431000c3030303030303030313230301c3432000c3030303030303030303830301c363500060000000000001c373700060000000000001c3738000854414253303031361c3739001730303130323033303430000000000000000000000000001c383000063230303431341c3831000431393136036c"
        data = unhexlify(data)
        result_valid = {'LRC': 'l', u'BCD': '\x02#',
        'DATA': [('C00', '01'), ('C01', '\x00\x00\x00\x00\x00\x00'), ('C30', '409851**2281'), ('C33', '          '), ('C34', 'AH'), ('C35', 'V.ELECTRON'), ('C40', '000000008000'), ('C41', '000000001200'), ('C42', '000000000800'), ('C65', '\x00\x00\x00\x00\x00\x00'), ('C77', '\x00\x00\x00\x00\x00\x00'), ('C78', 'TABS0016'), ('C79', '0010203040\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'), ('C80', '200414'), ('C81', '1916')],
        'ETX': '\x03', u'CONFIRM_MESSAGE': '\x06', u'STX': '\x02',
        'HEADER_FIELDS': {u'cod_trans': '00', u'indicator': '0', u'req_res': '1', u'cod_res': '00', u'version': '1', u'transport_header': '6000000000'}}
        business_conf = BusinessConfig(file_action.get_business_config_json())
        message_bldg = MessageBuilding(business_conf)
        message_rdg = MessageReading(business_conf, message_bldg)
        result = message_rdg.read_message(data, True)
        self.assertDictEqual(result, result_valid)

    def test_32(self):
        """ Interpretacion un mensaje de flujo unificado:
            Validaciones:
                * Se valida que los diccionarios sean iguales
        """
        data = "0602014036303030303030303030313030303030301c3131000a52656665724d6f76696c1c333000001c3333000a43616a65726f312020201c3430000c3030303030303031303030301c3431000c3030303030303030313230301c3432000c3030303030303030303830301c343300001c3434000c3030303030303030323030301c3636000a464143545552413120200339"
        data = unhexlify(data)
        result_valid = {'LRC': '9', u'BCD': '\x01@',
        'DATA': [('C11', 'ReferMovil'), ('C30', ''), ('C33', 'Cajero1   '), ('C40', '000000010000'), ('C41', '000000001200'), ('C42', '000000000800'), ('C43', ''), ('C44', '000000002000'), ('C66', 'FACTURA1  ')],
        'ETX': '\x03', u'CONFIRM_MESSAGE': '\x06', u'STX': '\x02',
        'HEADER_FIELDS': {u'cod_trans': '00', u'indicator': '0', u'req_res': '0', u'cod_res': '00', u'version': '1', u'transport_header': '6000000000'}}
        business_conf = BusinessConfig(file_action.get_business_config_json())
        message_bldg = MessageBuilding(business_conf)
        message_rdg = MessageReading(business_conf, message_bldg)
        result = message_rdg.read_message(data, True)
        self.assertDictEqual(result, result_valid)

    def test_33(self):
        """ Interpretacion un mensaje de flujo unificado:
            Validaciones:
                * Se valida que los diccionarios sean iguales
        """
        data = "0602022336303030303030303030313130303030301c3030000230311c303100060000000000001c3330000c3430393835312a2a323238311c3333000a43616a65726f312020201c3334000241481c3335000a562e454c454354524f4e1c3430000c3030303030303031303030301c3431000c3030303030303030313230301c3432000c3030303030303030303830301c363500060000000000001c373700060000000000001c3738000854414253303031361c3739001730303130323033303430000000000000000000000000001c383000063230303431351c38310004303632390347"
        data = unhexlify(data)
        result_valid = {'LRC': 'G', u'BCD': '\x02#',
        'DATA': [('C00', '01'), ('C01', '\x00\x00\x00\x00\x00\x00'), ('C30', '409851**2281'), ('C33', 'Cajero1   '), ('C34', 'AH'), ('C35', 'V.ELECTRON'), ('C40', '000000010000'), ('C41', '000000001200'), ('C42', '000000000800'), ('C65', '\x00\x00\x00\x00\x00\x00'), ('C77', '\x00\x00\x00\x00\x00\x00'), ('C78', 'TABS0016'), ('C79', '0010203040\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'), ('C80', '200415'), ('C81', '0629')],
        'ETX': '\x03', u'CONFIRM_MESSAGE': '\x06', u'STX': '\x02',
        'HEADER_FIELDS': {u'cod_trans': '00', u'indicator': '0', u'req_res': '1', u'cod_res': '00', u'version': '1', u'transport_header': '6000000000'}}
        business_conf = BusinessConfig(file_action.get_business_config_json())
        message_bldg = MessageBuilding(business_conf)
        message_rdg = MessageReading(business_conf, message_bldg)
        result = message_rdg.read_message(data, True)
        self.assertDictEqual(result, result_valid)

    def test_34(self):
        """ Interpretacion un mensaje de flujo unificado:
            Validaciones:
                * Se valida que los diccionarios sean iguales
        """
        data = "0602013036303030303030303030313030303030301c3131000a52656665724d6f76696c1c333000001c333300001c3430000c3030303030303031303030301c3431000c3030303030303030313230301c3432000c3030303030303030303830301c343300001c3434000c3030303030303030323030301c3636000a464143545552413120200362"
        data = unhexlify(data)
        result_valid = {'LRC': 'b', u'BCD': '\x010',
        'DATA': [('C11', 'ReferMovil'), ('C30', ''), ('C33', ''), ('C40', '000000010000'), ('C41', '000000001200'), ('C42', '000000000800'), ('C43', ''), ('C44', '000000002000'), ('C66', 'FACTURA1  ')],
        'ETX': '\x03', u'CONFIRM_MESSAGE': '\x06', u'STX': '\x02',
        'HEADER_FIELDS': {u'cod_trans': '00', u'indicator': '0', u'req_res': '0', u'cod_res': '00', u'version': '1', u'transport_header': '6000000000'}}
        business_conf = BusinessConfig(file_action.get_business_config_json())
        message_bldg = MessageBuilding(business_conf)
        message_rdg = MessageReading(business_conf, message_bldg)
        result = message_rdg.read_message(data, True)
        self.assertDictEqual(result, result_valid)

    def test_35(self):
        """ Interpretacion un mensaje de flujo unificado:
            Validaciones:
                * Se valida que los diccionarios sean iguales
        """
        data = "0602022336303030303030303030313130303030301c3030000230311c303100060000000000001c3330000c3430393835312a2a323238311c3333000a202020202020202020201c3334000241481c3335000a562e454c454354524f4e1c3430000c3030303030303031303030301c3431000c3030303030303030313230301c3432000c3030303030303030303830301c363500060000000000001c373700060000000000001c3738000854414253303031361c3739001730303130323033303430000000000000000000000000001c383000063230303431351c38310004303634300369"
        data = unhexlify(data)
        result_valid = {'LRC': 'i', u'BCD': '\x02#',
        'DATA': [('C00', '01'), ('C01', '\x00\x00\x00\x00\x00\x00'), ('C30', '409851**2281'), ('C33', '          '), ('C34', 'AH'), ('C35', 'V.ELECTRON'), ('C40', '000000010000'), ('C41', '000000001200'), ('C42', '000000000800'), ('C65', '\x00\x00\x00\x00\x00\x00'), ('C77', '\x00\x00\x00\x00\x00\x00'), ('C78', 'TABS0016'), ('C79', '0010203040\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'), ('C80', '200415'), ('C81', '0640')],
        'ETX': '\x03', u'CONFIRM_MESSAGE': '\x06', u'STX': '\x02',
        'HEADER_FIELDS': {u'cod_trans': '00', u'indicator': '0', u'req_res': '1', u'cod_res': '00', u'version': '1', u'transport_header': '6000000000'}}
        business_conf = BusinessConfig(file_action.get_business_config_json())
        message_bldg = MessageBuilding(business_conf)
        message_rdg = MessageReading(business_conf, message_bldg)
        result = message_rdg.read_message(data, True)
        self.assertDictEqual(result, result_valid)

    def test_36(self):
        """ Interpretacion un mensaje de flujo unificado:
            Validaciones:
                * Se valida que los diccionarios sean iguales
        """
        data = "0602024036303030303030303030313130303030301c3030000230311c303100060000000000001c3330000c3430393835312a2a323238311c3333000a43616a65726f312020201c3334000241481c3335000a562e454c454354524f4e1c3430000c3030303030303031303030301c3431000c3030303030303030333030301c3432000c3030303030303030303030301c3433000c30303030303030313030300a1c363500060000000000001c373700060000000000001c3738000854414253303031361c3739001730303130323033303430000000000000000000000000001c383000063230303431351c3831000430373034030e"
        data = unhexlify(data)
        result_valid = {'LRC': '\x0e', u'BCD': '\x02@',
        'DATA': [('C00', '01'), ('C01', '\x00\x00\x00\x00\x00\x00'), ('C30', '409851**2281'), ('C33', 'Cajero1   '), ('C34', 'AH'), ('C35', 'V.ELECTRON'), ('C40', '000000010000'), ('C41', '000000003000'), ('C42', '000000000000'), ('C43', '00000001000\n'), ('C65', '\x00\x00\x00\x00\x00\x00'), ('C77', '\x00\x00\x00\x00\x00\x00'), ('C78', 'TABS0016'), ('C79', '0010203040\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'), ('C80', '200415'), ('C81', '0704')],
        'ETX': '\x03', u'CONFIRM_MESSAGE': '\x06', u'STX': '\x02',
        'HEADER_FIELDS': {u'cod_trans': '00', u'indicator': '0', u'req_res': '1', u'cod_res': '00', u'version': '1', u'transport_header': '6000000000'}}
        business_conf = BusinessConfig(file_action.get_business_config_json())
        message_bldg = MessageBuilding(business_conf)
        message_rdg = MessageReading(business_conf, message_bldg)
        result = message_rdg.read_message(data, True)
        self.assertDictEqual(result, result_valid)

    def test_37(self):
        """ Interpretacion un mensaje de flujo unificado:
            Validaciones:
                * Se valida que los diccionarios sean iguales
        """
        data = "0602013036303030303030303030313030303030301c313100001c333000001c3333000a43616a65726f312020201c3430000c3030303030303030383030301c3431000c3030303030303030313230301c3432000c3030303030303030303830301c343300001c3434000c3030303030303030313030301c3636000a46414354555241310a200374"
        data = unhexlify(data)
        result_valid = {'LRC': 't', u'BCD': '\x010',
        'DATA': [('C11', ''), ('C30', ''), ('C33', 'Cajero1   '), ('C40', '000000008000'), ('C41', '000000001200'), ('C42', '000000000800'), ('C43', ''), ('C44', '000000001000'), ('C66', 'FACTURA1\n ')],
        'ETX': '\x03', u'CONFIRM_MESSAGE': '\x06', u'STX': '\x02',
        'HEADER_FIELDS': {u'cod_trans': '00', u'indicator': '0', u'req_res': '0', u'cod_res': '00', u'version': '1', u'transport_header': '6000000000'}}
        business_conf = BusinessConfig(file_action.get_business_config_json())
        message_bldg = MessageBuilding(business_conf)
        message_rdg = MessageReading(business_conf, message_bldg)
        result = message_rdg.read_message(data, True)
        self.assertDictEqual(result, result_valid)

    def test_38(self):
        """ Interpretacion un mensaje de flujo unificado:
            Validaciones:
                * Se valida que los diccionarios sean iguales
        """
        data = "0602022336303030303030303030313130303030301c3030000230311c303100060000000000001c3330000c3430393835312a2a323238311c3333000a43616a65726f312020201c3334000241481c3335000a562e454c454354524f4e1c3430000c3030303030303030383030301c3431000c3030303030303030313230301c3432000c3030303030303030303830301c363500060000000000001c373700060000000000001c3738000854414253303031361c3739001730303130323033303430000000000000000000000000001c383000063230303431351c38310004303735360347"
        data = unhexlify(data)
        result_valid = {'LRC': 'G', u'BCD': '\x02#',
        'DATA': [('C00', '01'), ('C01', '\x00\x00\x00\x00\x00\x00'), ('C30', '409851**2281'), ('C33', 'Cajero1   '), ('C34', 'AH'), ('C35', 'V.ELECTRON'), ('C40', '000000008000'), ('C41', '000000001200'), ('C42', '000000000800'), ('C65', '\x00\x00\x00\x00\x00\x00'), ('C77', '\x00\x00\x00\x00\x00\x00'), ('C78', 'TABS0016'), ('C79', '0010203040\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'), ('C80', '200415'), ('C81', '0756')],
        'ETX': '\x03', u'CONFIRM_MESSAGE': '\x06', u'STX': '\x02',
        'HEADER_FIELDS': {u'cod_trans': '00', u'indicator': '0', u'req_res': '1', u'cod_res': '00', u'version': '1', u'transport_header': '6000000000'}}
        business_conf = BusinessConfig(file_action.get_business_config_json())
        message_bldg = MessageBuilding(business_conf)
        message_rdg = MessageReading(business_conf, message_bldg)
        result = message_rdg.read_message(data, True)
        self.assertDictEqual(result, result_valid)

    def test_39(self):
        """ Interpretacion un mensaje de flujo unificado:
            Se cambia la estructura y el mensaje debe ser interpretado igual
                * Estructura originas = ['CONFIRM_MESSAGE',STX','BCD','DATA','ETX', 'LRC']
                * Estructura modificada = ['BCD','STX','CONFIRM_MESSAGE','DATA','ETX','LRC']
            Validaciones:
                * Se valida que los diccionarios sean iguales
        """
        data = "0098020636303030303030303030313030303030301c3430000c3030303030303031353030301c3131000a52656665724d6f76696c1c3434000c3030303030303030313530301c3636000a466163747572612020201c3433000c30303030303030303135303003da"
        data = unhexlify(data)
        result_valid = {'LRC': '\xda', u'BCD': '\x00\x98',
        'DATA': [('C40', '000000015000'), ('C11', 'ReferMovil'), ('C44', '000000001500'), ('C66', 'Factura   '), ('C43', '000000001500')],
        'ETX': '\x03', u'CONFIRM_MESSAGE': '\x06', u'STX': '\x02',
        'HEADER_FIELDS': {u'cod_trans': '00', u'indicator': '0', u'req_res': '0', u'cod_res': '00', u'version': '1', u'transport_header': '6000000000'}}
        business_conf = BusinessConfig(file_action.get_business_config_json())
        struct = business_conf.get_message_definition()["structure"]
        struct[0], struct[2] = struct[2], struct[0]
        message_bldg = MessageBuilding(business_conf)
        message_rdg = MessageReading(business_conf, message_bldg)
        result = message_rdg.read_message(data, True)
        self.assertDictEqual(result, result_valid)

    def test_40(self):
        """ Interpretacion un mensaje de flujo unificado:
            Se cambia la estructura y el mensaje debe ser interpretado igual
                * Estructura originas = ['CONFIRM_MESSAGE',STX','BCD','DATA','ETX', 'LRC']
            Validaciones:
                * Se valida que los diccionarios sean iguales
        """
        data = "0206009836303030303030303030313030303030301c3430000c3030303030303031353030301c3131000a52656665724d6f76696c1c3434000c3030303030303030313530301c3636000a466163747572612020201c3433000c30303030303030303135303003da"
        data = unhexlify(data)
        result_valid = {'LRC': '\xda', u'BCD': '\x00\x98',
        'DATA': [('C40', '000000015000'), ('C11', 'ReferMovil'), ('C44', '000000001500'), ('C66', 'Factura   '), ('C43', '000000001500')],
        'ETX': '\x03', u'CONFIRM_MESSAGE': '\x06', u'STX': '\x02',
        'HEADER_FIELDS': {u'cod_trans': '00', u'indicator': '0', u'req_res': '0', u'cod_res': '00', u'version': '1', u'transport_header': '6000000000'}}
        business_conf = BusinessConfig(file_action.get_business_config_json())
        struct = business_conf.get_message_definition()["structure"]
        struct[0], struct[1] = struct[1], struct[0]
        message_bldg = MessageBuilding(business_conf)
        message_rdg = MessageReading(business_conf, message_bldg)
        result = message_rdg.read_message(data, True)
        self.assertDictEqual(result, result_valid)

    def test_41(self):
        """ Interpretacion un mensaje de flujo unificado:
            Se cambia la estructura y el mensaje debe ser interpretado igual
                * Estructura originas = ['CONFIRM_MESSAGE',STX','BCD','DATA','ETX', 'LRC']
            Validaciones:
                * Se valida que los diccionarios sean iguales
        """
        data = "0200980636303030303030303030313030303030301c3430000c3030303030303031353030301c3131000a52656665724d6f76696c1c3434000c3030303030303030313530301c3636000a466163747572612020201c3433000c30303030303030303135303003da"
        data = unhexlify(data)
        result_valid = {'LRC': '\xda', u'BCD': '\x00\x98',
        'DATA': [('C40', '000000015000'), ('C11', 'ReferMovil'), ('C44', '000000001500'), ('C66', 'Factura   '), ('C43', '000000001500')],
        'ETX': '\x03', u'CONFIRM_MESSAGE': '\x06', u'STX': '\x02',
        'HEADER_FIELDS': {u'cod_trans': '00', u'indicator': '0', u'req_res': '0', u'cod_res': '00', u'version': '1', u'transport_header': '6000000000'}}
        business_conf = BusinessConfig(file_action.get_business_config_json())
        struct = business_conf.get_message_definition()["structure"]
        struct[0], struct[1], struct[2] = struct[1], struct[2], struct[0]
        message_bldg = MessageBuilding(business_conf)
        message_rdg = MessageReading(business_conf, message_bldg)
        result = message_rdg.read_message(data, True)
        self.assertDictEqual(result, result_valid)

    def test_42(self):
        """ Interpretacion un mensaje de flujo unificado:
            Se cambia la estructura y el mensaje debe ser interpretado igual
                * Estructura originas = ['CONFIRM_MESSAGE',STX','BCD','DATA','ETX', 'LRC']

            Se cambia la estructura de la cabecera del mensaje
                * Estructura original = ["transport_header","version", "req_res",
                    "cod_trans", "cod_res", "indicator", "separador_campo"]

                * Estructura modificada = ["indicator","version", "req_res",
                    "cod_trans", "cod_res", "transport_header", "separador_campo"]

            Validaciones:
                * Se valida que los diccionarios sean iguales
        """
        data = "0200980630313030303030363030303030303030301c3430000c3030303030303031353030301c3131000a52656665724d6f76696c1c3434000c3030303030303030313530301c3636000a466163747572612020201c3433000c30303030303030303135303003da"
        data = unhexlify(data)
        result_valid = {'LRC': '\xda', u'BCD': '\x00\x98',
        'DATA': [('C40', '000000015000'), ('C11', 'ReferMovil'), ('C44', '000000001500'), ('C66', 'Factura   '), ('C43', '000000001500')],
        'ETX': '\x03', u'CONFIRM_MESSAGE': '\x06', u'STX': '\x02',
        'HEADER_FIELDS': {u'cod_trans': '00', u'indicator': '0', u'req_res': '0', u'cod_res': '00', u'version': '1', u'transport_header': '6000000000'}}
        business_conf = BusinessConfig(file_action.get_business_config_json())
        struct = business_conf.get_message_definition()["structure"]
        struct[0], struct[1], struct[2] = struct[1], struct[2], struct[0]
        data_structure = business_conf.get_data_frame()
        head_struc = data_structure["header_structure"]
        head_struc[0], head_struc[5] = head_struc[5], head_struc[0]

        message_bldg = MessageBuilding(business_conf)
        message_rdg = MessageReading(business_conf, message_bldg)
        result = message_rdg.read_message(data, True)
        self.assertDictEqual(result, result_valid)

    def test_43(self):
        """ Interpretacion un mensaje de flujo unificado:
            Se cambia la estructura y el mensaje debe ser interpretado igual
                * Estructura originas = ['CONFIRM_MESSAGE',STX','BCD','DATA','ETX', 'LRC']

            Se cambia la estructura de la cabecera del mensaje
                * Estructura original = ["transport_header","version", "req_res",
                    "cod_trans", "cod_res", "indicator", "separador_campo"]

                * Estructura modificada = ["indicator","version", "req_res",
                    "cod_trans", "cod_res", "transport_header", "separador_campo"]

            Validaciones:
                * Se valida que los diccionarios sean iguales
        """
        data = "0200980630303130303030363030303030303030301c3430000c3030303030303031353030301c3131000a52656665724d6f76696c1c3434000c3030303030303030313530301c3636000a466163747572612020201c3433000c30303030303030303135303003da"
        data = unhexlify(data)
        result_valid = {'LRC': '\xda', u'BCD': '\x00\x98',
        'DATA': [('C40', '000000015000'), ('C11', 'ReferMovil'), ('C44', '000000001500'), ('C66', 'Factura   '), ('C43', '000000001500')],
        'ETX': '\x03', u'CONFIRM_MESSAGE': '\x06', u'STX': '\x02',
        'HEADER_FIELDS': {u'cod_trans': '00', u'indicator': '0', u'req_res': '0', u'cod_res': '00', u'version': '1', u'transport_header': '6000000000'}}
        business_conf = BusinessConfig(file_action.get_business_config_json())
        struct = business_conf.get_message_definition()["structure"]
        struct[0], struct[1], struct[2] = struct[1], struct[2], struct[0]
        data_structure = business_conf.get_data_frame()
        head_struc = data_structure["header_structure"]
        head_struc[0], head_struc[5], head_struc[3] = head_struc[3], head_struc[0], head_struc[5]

        message_bldg = MessageBuilding(business_conf)
        message_rdg = MessageReading(business_conf, message_bldg)
        result = message_rdg.read_message(data, True)
        self.assertDictEqual(result, result_valid)

    def test_44(self):
        """ Interpretacion un mensaje de flujo unificado:
            Se cambia la estructura y el mensaje debe ser interpretado igual
                * Estructura originas = ['CONFIRM_MESSAGE','STX','BCD','DATA','ETX', 'LRC']
                * Estructura modificada = ['BCD','STX','CONFIRM_MESSAGE','DATA','ETX','LRC']

            Se cambia la estructura de la cabecera del mensaje
                * Estructura original = ["transport_header","version", "req_res",
                    "cod_trans", "cod_res", "indicator", "separador_campo"]

                * Estructura modificada = ["separador_campo", "indicator", "cod_res",
                    "cod_trans", "req_res", "version", "transport_header"]

            Validaciones:
                * Se valida que los diccionarios sean iguales
        """
        data = "0200980636303030303030303030303030303030311c3430000c3030303030303031353030301c3131000a52656665724d6f76696c1c3434000c3030303030303030313530301c3636000a466163747572612020201c3433000c30303030303030303135303003da"
        data = unhexlify(data)
        result_valid = {'LRC': '\xda', u'BCD': '\x00\x98',
        'DATA': [('C40', '000000015000'), ('C11', 'ReferMovil'), ('C44', '000000001500'), ('C66', 'Factura   '), ('C43', '000000001500')],
        'ETX': '\x03', u'CONFIRM_MESSAGE': '\x06', u'STX': '\x02',
        'HEADER_FIELDS': {u'cod_trans': '00', u'indicator': '0', u'req_res': '0', u'cod_res': '00', u'version': '1', u'transport_header': '6000000000'}}
        business_conf = BusinessConfig(file_action.get_business_config_json())
        struct = business_conf.get_message_definition()["structure"]
        struct[0], struct[1], struct[2] = struct[1], struct[2], struct[0]
        data_structure = business_conf.get_data_frame()
        head_struc = data_structure["header_structure"]
        head_struc[1], head_struc[5] = head_struc[5], head_struc[1]
        head_struc[2], head_struc[4] = head_struc[4], head_struc[2]

        message_bldg = MessageBuilding(business_conf)
        message_rdg = MessageReading(business_conf, message_bldg)
        result = message_rdg.read_message(data, True)
        self.assertDictEqual(result, result_valid)


if __name__ == '__main__':
    file_action = FileActions(current_path)
    # Run the TestCase, main function is the unittest package
    main()


