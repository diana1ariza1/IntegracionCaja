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
        """ Prueba de la funcion de calculo LRC """
        data = "011536303030303030303030313030303030301C3333000A302020202020202020201C3430000C3030303030303038303030301C3431000C3030303030303030303030301C3432000C3030303030303030303030301C3434000C3030303030303030303030301C3636000A3020202020202020202003"
        data = unhexlify(data)
        business_conf = BusinessConfig(file_action.get_business_config_json())
        message_bldg = MessageBuilding(business_conf)
        result = hexlify(message_bldg.calculate_lrc(data)).upper()
        self.assertEqual(first=result, second='2F')

    def test_2(self):
        """ Prueba de la funcion de calculo LRC """
        data = "022336303030303030303030313130303030301C3030000230311C303100060000000000001C3330000C3432363238382A2A333038321C3333000A302020202020202020201C3334000241481C3335000A562E454C454354524F4E1C3430000C3030303030303038303030301C3431000C3030303030303030303030301C3432000C3030303030303030303030301C363500060000000000001C373700060000000000001C3738000856455249463030351C3739001730303130323033303430000000000000000000000000001C383000063139303431371C383100043130323803"
        data = unhexlify(data)
        business_conf = BusinessConfig(file_action.get_business_config_json())
        message_bldg = MessageBuilding(business_conf)
        result = hexlify(message_bldg.calculate_lrc(data)).upper()
        self.assertEqual(first=result, second='01')

    def test_3(self):
        """ Prueba de la funcion de calculo LRC """
        data = "022336303030303030303030313130303030301C3030000230311C303100060000000000001C3330000C3432363238382A2A333038321C3333000A302020202020202020201C3334000241481C3335000A562E454C454354524F4E1C3430000C3030303030303038303030301C3431000C3030303030303030303030301C3432000C3030303030303030303030301C363500060000000000001C373700060000000000001C3738000856455249463030351C3739001730303130323033303430000000000000000000000000001C383000063139303431371C383100043130323803"
        data = unhexlify(data)
        business_conf = BusinessConfig(file_action.get_business_config_json())
        message_bldg = MessageBuilding(business_conf)
        result = hexlify(message_bldg.calculate_lrc(data)).upper()
        self.assertNotEqual(first=result, second="00")

    def test_4(self):
        """ Prueba de la funcion de calculo LRC """
        data = "0602003736303030303030303030313039392020301C333300001C343000001C363900001C393300000302"
        data = unhexlify(data)
        business_conf = BusinessConfig(file_action.get_business_config_json())
        message_bldg = MessageBuilding(business_conf)
        result = hexlify(message_bldg.calculate_lrc(data)).upper()
        self.assertNotEqual(first=result, second='02')
        
    def test_5(self):
        """Prueba de la lectura del primer mensaje de flujo unificado"""
        data = "02003736303030303030303030313039392020301C333300001C343000001C363900001C393300000302"
        response = unhexlify(data)
        business_conf = BusinessConfig(file_action.get_business_config_json())
        message_bldg = MessageBuilding(business_conf)
        message_rdg = MessageReading(business_conf, message_bldg)
        response = message_rdg.read_message(response, False)
        correct_answer = {'LRC': '\x02', 'BCD': '\x007', 'DATA': [('C33', ''), ('C40', ''), ('C69', ''), ('C93', '')], 'ETX': '\x03', 'HEADER_FIELDS': {'cod_trans': '99', 'indicator': '0', 'req_res': '0', 'cod_res': '  ', 'version': '1', 'transport_header': '6000000000'}, 'STX': '\x02'}
        self.assertDictEqual(response, correct_answer)

    def test_6(self):
        """Prueba de la lectura de un mensaje con el campo '06' al inicio """
        data = "0602006936303030303030303030313030302020301C313100001C3330000C3432363238382A2A333038321C333300001C343000001C343100001C343200001C343400001C36360000035E"
        response = unhexlify(data)
        business_conf = BusinessConfig(file_action.get_business_config_json())
        message_bldg = MessageBuilding(business_conf)
        message_rdg = MessageReading(business_conf, message_bldg)
        response = message_rdg.read_message(response, True)
        correct_answer = {'LRC': '^', 'BCD': '\x00i', 'DATA': [('C11', ''), ('C30', '426288**3082'), ('C33', ''), ('C40', ''), ('C41', ''), ('C42', ''), ('C44', ''), ('C66', '')], 'ETX': '\x03', 'CONFIRM_MESSAGE': '\x06', 'HEADER_FIELDS': {'cod_trans': '00', 'indicator': '0', 'req_res': '0', 'cod_res': '  ', 'version': '1', 'transport_header': '6000000000'}, 'STX': '\x02'}
        self.assertDictEqual(response, correct_answer)
        
    def test_7(self):
        """Prueba de la lectura de un mensaje de flujo no unificado """
        data = "0602004136303030303030303030313130333030301C3333000A202020202020202020201C38340004303030300375"
        response = unhexlify(data)
        business_conf = BusinessConfig(file_action.get_business_config_json())
        message_bldg = MessageBuilding(business_conf)
        message_rdg = MessageReading(business_conf, message_bldg)
        response = message_rdg.read_message(response, True)
        correct_answer = {'LRC': 'u', 'BCD': '\x00A', 'DATA': [('C33', '          '), ('C84', '0000')], 'ETX': '\x03', 'CONFIRM_MESSAGE': '\x06', 'HEADER_FIELDS': {'cod_trans': '03', 'indicator': '0', 'req_res': '1', 'cod_res': '00', 'version': '1', 'transport_header': '6000000000'}, 'STX': '\x02'}
        self.assertDictEqual(response, correct_answer)

    def test_8(self):
        """
        Prueba orientada a la construccion de la cabecera del mensaje,
        de acuerdo a la configuracion definida en el archivo
        "business.config.json" en el apartado "header_structure"
        """
        valid_header = "36303030303030303030313030303030301c"
        business_conf = BusinessConfig(file_action.get_business_config_json())
        message_bldg = MessageBuilding(business_conf)
        header = hexlify(message_bldg.assemble_header("0", "00"))
        self.assertEqual(valid_header, header)

    def test_9(self):
        """
        Prueba orientada a la construccion de la cabecera del mensaje,
        de acuerdo a la configuracion definida en el archivo
        "business.config.json" en el apartado "header_structure"
        
        * Se envia al parametro req_res como 1
        """
        valid_header = "36303030303030303030313130303030301c"
        business_conf = BusinessConfig(file_action.get_business_config_json())
        message_bldg = MessageBuilding(business_conf)
        header = hexlify(message_bldg.assemble_header("1", "00"))
        self.assertEqual(valid_header, header)

    def test_10(self):
        """
        Prueba orientada a la construccion de la cabecera del mensaje,
        de acuerdo a la configuracion definida en el archivo
        "business.config.json" en el apartado "header_structure"
        
        * Se envia al parametro req_res como 2
        """
        valid_header = "36303030303030303030313230303030301c"
        business_conf = BusinessConfig(file_action.get_business_config_json())
        message_bldg = MessageBuilding(business_conf)
        header = hexlify(message_bldg.assemble_header("2", "00"))
        self.assertEqual(valid_header, header)

    def test_11(self):
        """
        Prueba orientada a la construccion de la cabecera del mensaje,
        de acuerdo a la configuracion definida en el archivo
        "business.config.json" en el apartado "header_structure"
        
        * Se envia al parametro req_res un valor invalido
        que no pertenece a ningun requerimiento respuesta y no esta
        incluido en el campo "req_res" del apartado "data_frame".

        Por ejemplo:
        {
            "data_frame": {
                "req_res": {
                    "max_length": 1,
                    "description": "Identifica el tipo de mensaje",
                    "value": ["0","1","2"]
                },
                ...
            }
        }
        """
        business_conf = BusinessConfig(file_action.get_business_config_json())
        message_bldg = MessageBuilding(business_conf)
        func = message_bldg.assemble_header
        with self.assertRaises(ValueError): func("3", "00")

    def test_12(self):
        """
        Prueba orientada a la construccion de la cabecera del mensaje,
        de acuerdo a la configuracion definida en el archivo
        "business.config.json" en el apartado "header_structure"

        * Se modifica la configuracion para agregar el valor "3" al campo
        "req_res" para que sea valido y puede ser creada la cabecera

        Por ejemplo:
        {
            "data_frame": {
                "req_res": {
                    "max_length": 1,
                    "description": "Identifica el tipo de mensaje",
                    "value": ["0","1","2", "3"]
                },
                ...
            }
        }
        """
        valid_header = "36303030303030303030313330303030301c"
        business_conf = BusinessConfig(file_action.get_business_config_json())
        req_res = business_conf.get_data_frame().get("req_res")
        req_res["value"].append("3")
        message_bldg = MessageBuilding(business_conf)
        header = hexlify(message_bldg.assemble_header("3", "00"))
        self.assertEqual(valid_header, header)

    def test_13(self):
        """
        Prueba orientada a la construccion de la cabecera del mensaje,
        de acuerdo a la configuracion definida en el archivo
        "business.config.json" en el apartado "header_structure"

        * Se modifica la configuracion para agregar el valor "S" al campo
        "req_res" para que sea valido y puede ser creada la cabecera

        Por ejemplo:
        {
            "data_frame": {
                "req_res": {
                    "max_length": 1,
                    "description": "Identifica el tipo de mensaje",
                    "value": ["0","1","2", "S"]
                },
                ...
            }
        }
        """
        valid_header = "36303030303030303030315330303030301c"
        business_conf = BusinessConfig(file_action.get_business_config_json())
        req_res = business_conf.get_data_frame().get("req_res")
        req_res["value"].append("S")
        message_bldg = MessageBuilding(business_conf)
        header = hexlify(message_bldg.assemble_header("S", "00"))
        self.assertEqual(valid_header, header)

    def test_14(self):
        """
        Prueba orientada a la construccion de la cabecera del mensaje,
        de acuerdo a la configuracion definida en el archivo
        "business.config.json" en el apartado "header_structure"

        * Se comparan dos cabecera totalmente distintas

        """
        valid_header = "3600000000000000000000001c"
        business_conf = BusinessConfig(file_action.get_business_config_json())
        message_bldg = MessageBuilding(business_conf)
        header = hexlify(message_bldg.assemble_header("0", "00"))
        self.assertNotEqual(valid_header, header)

    def test_15(self):
        """
        Prueba orientada a la construccion de la cabecera del mensaje,
        de acuerdo a la configuracion definida en el archivo
        "business.config.json" en el apartado "header_structure"

        * Se modifica la configuracion para cambiar el valor "1C" por
        "3B" (valor hexadecimal) al campo "separador_campo"

        Por ejemplo:
        {
            "data_frame": {
                "separador_campo": {
                    "max_length": 1,
                    "description": "FS, Separador de Campo",
                    "value": "3B"
                },
                ...
            }
        }

        """
        valid_header = "36303030303030303030313030303030303b"
        business_conf = BusinessConfig(file_action.get_business_config_json())
        separador_campo = business_conf.get_data_frame().get("separador_campo")
        separador_campo["value"] = "3b"
        message_bldg = MessageBuilding(business_conf)
        header = hexlify(message_bldg.assemble_header("0", "00"))
        self.assertEqual(valid_header, header)

    def test_16(self):
        """
        Prueba orientada a la construccion de la cabecera del mensaje,
        de acuerdo a la configuracion definida en el archivo
        "business.config.json" en el apartado "header_structure"

        * Se modifica la configuracion para cambiar el valor "1C" por
        "PP" (valor no hexadecimal) al campo "separador_campo"

        Por ejemplo:
        {
            "data_frame": {
                "separador_campo": {
                    "max_length": 1,
                    "description": "FS, Separador de Campo",
                    "value": "PP"
                },
                ...
            }
        }
        """
        business_conf = BusinessConfig(file_action.get_business_config_json())
        separador_campo = business_conf.get_data_frame().get("separador_campo")
        separador_campo["value"] = "PP"
        message_bldg = MessageBuilding(business_conf)
        func = message_bldg.assemble_header
        with self.assertRaises(ValueError): func ("0", "00")

    def test_17(self):
        """
        Prueba orientada a la construccion de la cabecera del mensaje,
        de acuerdo a la configuracion definida en el archivo
        "business.config.json" en el apartado "header_structure"

        * Se modifica la configuracion para cambiar el valor "1C" por
        "PP" (valor no hexadecimal) al campo "separador_campo"

        Por ejemplo:
        {
            "data_frame": {
                "separador_campo": {
                    "max_length": 1,
                    "description": "FS, Separador de Campo",
                    "value": "PP"
                },
                ...
            }
        }
        """
        valid_header = "36303030303030303030313030303030303b"
        business_conf = BusinessConfig(file_action.get_business_config_json())
        separador_campo = business_conf.get_data_frame().get("separador_campo")
        separador_campo["value"] = "3b"
        message_bldg = MessageBuilding(business_conf)
        header = hexlify(message_bldg.assemble_header("0", "00"))
        self.assertEqual(valid_header, header)

    def test_18(self):
        """
        Prueba orientada a la construccion de la cabecera del mensaje,
        de acuerdo a la configuracion definida en el archivo
        "business.config.json" en el apartado "header_structure"

        * Se modifica la configuracion para cambiar de longitud "1" por
        "5" al campo "separador_campo"

        Por ejemplo:
        {
            "data_frame": {
                "separador_campo": {
                    "max_length": 5,
                    "description": "FS, Separador de Campo",
                    "value": "1C"
                },
                ...
            }
        }
        """
        valid_header = "3630303030303030303031303030303030000000001c"
        business_conf = BusinessConfig(file_action.get_business_config_json())
        separador_campo = business_conf.get_data_frame().get("separador_campo")
        separador_campo["max_length"] = 5
        message_bldg = MessageBuilding(business_conf)
        header = hexlify(message_bldg.assemble_header("0", "00"))
        self.assertEqual(valid_header, header)

    def test_19(self):
        """
        Prueba orientada a la construccion de la cabecera del mensaje,
        de acuerdo a la configuracion definida en el archivo
        "business.config.json" en el apartado "header_structure"

        * Se modifica la configuracion para cambiar valor "6000000000" por
        "11" al campo "transport_header" y el programa debe rellenar
        el resto de la longitud con ceros (0).
        Por ejemplo:
        {
            "data_frame": {
                "transport_header": {
                    "max_length": 10,
                    "description": "Cabecera principal del mensaje",
                    "value": "11"
                },
                ...
            }
        }
        """
        valid_header = "31313030303030303030313030303030301c"
        business_conf = BusinessConfig(file_action.get_business_config_json())
        transport_header = business_conf.get_data_frame().get("transport_header")
        transport_header["value"] = "11"
        message_bldg = MessageBuilding(business_conf)
        header = hexlify(message_bldg.assemble_header("0", "00"))
        self.assertEqual(valid_header, header)

    def test_20(self):
        """
        Prueba orientada a la construccion de la cabecera del mensaje,
        de acuerdo a la configuracion definida en el archivo
        "business.config.json" en el apartado "header_structure"

        * Se modifica la configuracion para:
            - Cambiar valor "6000000000" por "600061" al campo "transport_header"
            - Cambiar valor "1" por "30" y la longitud "1" a "2 en el campo
            "version"
            - Cambiar la longitud de "1" a "5" al campo "indicador"
            - Cambiar el valor ["0", "1", "2"] a ["3", "4", "5"] para el campo
            "req_res"
            - Para el campo "req_res" se envia "0" (invalido).

        Por ejemplo:
        {
            "data_frame": {
                "transport_header": {
                    "value": "600061"
                },
                "version": {
                    "max_length": 2,
                    "value": "30"
                },
                "indicador": {
                    "max_length": 5,
                },
                "req_res": {
                    "value": ["3", "4", "5"],
                },
                ...
            }
        }
        """
        business_conf = BusinessConfig(file_action.get_business_config_json())

        transport_header = business_conf.get_data_frame().get("transport_header")
        transport_header["value"] = "600061"

        version = business_conf.get_data_frame().get("version")
        version["max_length"] = 2
        version["value"] = "30"

        indicator = business_conf.get_data_frame().get("indicator")
        indicator["max_length"] = 5

        req_res = business_conf.get_data_frame().get("req_res")
        req_res["value"] = ["3", "4", "5"]

        message_bldg = MessageBuilding(business_conf)
        func = message_bldg.assemble_header
        with self.assertRaises(ValueError): func("0", "00")

    def test_21(self):
        """
        Prueba orientada a la construccion de la cabecera del mensaje,
        de acuerdo a la configuracion definida en el archivo
        "business.config.json" en el apartado "header_structure"

        * Se modifica la configuracion para:
            - Cambiar valor "6000000000" por "600061" al campo "transport_header"
            - Cambiar valor "1" por "30" y la longitud "1" a "2 en el campo
            "version"
            - Cambiar la longitud de "1" a "5" al campo "indicador"
            - Cambiar el valor ["0", "1", "2"] a ["3", "4", "5"] para el campo
            "req_res"
            - Para el campo "req_res" se envia "3" (valido).

        Por ejemplo:
        {
            "data_frame": {
                "transport_header": {
                    "value": "600061"
                },
                "version": {
                    "max_length": 2,
                    "value": "30"
                },
                "indicador": {
                    "max_length": 5,
                },
                "req_res": {
                    "value": ["3", "4", "5"],
                },
                ...
            }
        }
        """
        valid_header = "363030303631303030303939333030303030303030302f"
        business_conf = BusinessConfig(file_action.get_business_config_json())

        transport_header = business_conf.get_data_frame().get("transport_header")
        transport_header["value"] = "600061"

        version = business_conf.get_data_frame().get("version")
        version["max_length"] = 2
        version["value"] = "99"

        indicator = business_conf.get_data_frame().get("indicator")
        indicator["max_length"] = 5

        req_res = business_conf.get_data_frame().get("req_res")
        req_res["value"] = ["3", "4", "5"]

        separador_campo = business_conf.get_data_frame().get("separador_campo")
        separador_campo["value"] = "2f"

        message_bldg = MessageBuilding(business_conf)
        header = hexlify(message_bldg.assemble_header("3", "00"))
        self.assertEqual(valid_header, header)

    def test_22(self):
        """
        Prueba orientada a la construccion de la cabecera del mensaje,
        de acuerdo a la configuracion definida en el archivo
        "business.config.json" en el apartado "header_structure"

        * La variable "valid_header" se asigna con la configuracion
        por defecto del campo "header_structure"

        * Se modifica la configuracion para:
            - Cambiar valor "6000000000" por "600061" al campo "transport_header"
            - Cambiar valor "1" por "30" y la longitud "1" a "2 en el campo
            "version"
            - Cambiar la longitud de "1" a "5" al campo "indicador"
            - Cambiar la estructura de la cabecera, es decir esto:
                "header_structure": ["transport_header","version", "req_res",
                "cod_trans", "cod_res","indicator", "separador_campo"] 
                
                por esto: 
                "header_structure": ["req_res", "cod_trans", "transport_header",
                "version", "separador_campo","indicator", "cod_res"] 

                "header_structure": ["transport_header","version", "req_res",
                "cod_trans", "cod_res","indicator", "separador_campo"] 

        Por ejemplo:
        {
            "data_frame": {
                "header_structure": ["req_res", "cod_trans", "transport_header",
                    "version", "separador_campo","indicator", "cod_res"],
                "transport_header": {
                    "value": "600061"
                },
                "version": {
                    "max_length": 2,
                    "value": "30"
                },
                "indicador": {
                    "max_length": 5,
                },
                "req_res": {
                    "value": ["3", "4", "5"],
                },
                ...
            }
        }
        """
        valid_header = "3630303030303030303031030303030301c"
        business_conf = BusinessConfig(file_action.get_business_config_json())
        struc = business_conf.get_data_frame().get("header_structure")
        struc[0], struc[2] = struc[2], struc[0]
        struc[1], struc[3] = struc[3], struc[1]
        struc[4], struc[6] = struc[6], struc[4]

        transport_header = business_conf.get_data_frame().get("transport_header")
        transport_header["value"] = "600061"

        version = business_conf.get_data_frame().get("version")
        version["max_length"] = 2
        version["value"] = "99"

        indicator = business_conf.get_data_frame().get("indicator")
        indicator["max_length"] = 5

        message_bldg = MessageBuilding(business_conf)
        header = hexlify(message_bldg.assemble_header("0", "00"))
        self.assertNotEqual(valid_header, header)

    def test_23(self):
        """
        Prueba orientada a la construccion de la cabecera del mensaje,
        de acuerdo a la configuracion definida en el archivo
        "business.config.json" en el apartado "header_structure"

        * La variable "valid_header" se asigna con la configuracion
        cambiada del campo "header_structure"

        * Se modifica la configuracion para:
            - Cambiar valor "6000000000" por "600061" al campo "transport_header"
            - Cambiar valor "1" por "30" y la longitud "1" a "2 en el campo
            "version"
            - Cambiar la longitud de "1" a "5" al campo "indicador"
            - Cambiar la estructura de la cabecera, es decir esto:
                "header_structure": ["transport_header","version", "req_res",
                "cod_trans", "cod_res","indicator", "separador_campo"] 
                
                por esto: 
                "header_structure": ["req_res", "cod_trans", "transport_header",
                "version", "separador_campo","indicator", "cod_res"] 

                "header_structure": ["transport_header","version", "req_res",
                "cod_trans", "cod_res","indicator", "separador_campo"] 

        Por ejemplo:
        {
            "data_frame": {
                "header_structure": ["req_res", "cod_trans", "transport_header",
                    "version", "separador_campo","indicator", "cod_res"],
                "transport_header": {
                    "value": "600061"
                },
                "version": {
                    "max_length": 2,
                    "value": "30"
                },
                "indicador": {
                    "max_length": 5,
                },
                "req_res": {
                    "value": ["3", "4", "5"],
                },
                ...
            }
        }
        """
        valid_header = "3030303630303036313030303039391c30303030303030"
        business_conf = BusinessConfig(file_action.get_business_config_json())
        struc = business_conf.get_data_frame().get("header_structure")
        struc[0], struc[2] = struc[2], struc[0]
        struc[1], struc[3] = struc[3], struc[1]
        struc[4], struc[6] = struc[6], struc[4]

        transport_header = business_conf.get_data_frame().get("transport_header")
        transport_header["value"] = "600061"

        version = business_conf.get_data_frame().get("version")
        version["max_length"] = 2
        version["value"] = "99"

        indicator = business_conf.get_data_frame().get("indicator")
        indicator["max_length"] = 5

        message_bldg = MessageBuilding(business_conf)
        header = hexlify(message_bldg.assemble_header("0", "00"))
        self.assertEqual(valid_header, header)

    def test_24(self):
        """
        Prueba orientada a la construccion del campo de datos del mensaje,
        de acuerdo a la configuracion definida en el archivo
        "business.config.json" en el apartado "operations" y los campos
        correspondientes en el apartado "fields_definition"
        
        * Se crea un conjunto de datos para una operacion de flujo unificado
        * Se toma una operacion de flujo unificado del archivo "business.config.json"

        """
        input_data = ["Cajero1", "10000", "1500", "0", "1000", "FACTURA1"]
        operation = ["C33", "C40", "C41", "C42", "C44", "C66"]
        valid_header = [('C33', 'Cajero1   '), ('C40', '000000010000'), ('C41', '000000001500'), ('C42', '000000000000'), ('C44', '000000001000'), ('C66', 'FACTURA1  ')]
        business_conf = BusinessConfig(file_action.get_business_config_json())
        message_bldg = MessageBuilding(business_conf)
        result = message_bldg.assemble_data(input_data, operation)
        self.assertEqual(valid_header, result)

    def test_25(self):
        """
        Prueba orientada a la construccion del campo de datos del mensaje,
        de acuerdo a la configuracion definida en el archivo
        "business.config.json" en el apartado "operations" y los campos
        correspondientes en el apartado "fields_definition"

        Si se mandan los campos vacios, se retorna la estructura rellenada
        con los caracteres dependiendo del tipo de dato "0" para "N" y 
        "\x20" (Espacio en blanco) para "ANS" acorde a lo definido en 
        "business.config.json".

        * Se crea un conjunto de datos vacio para una operacion de flujo unificado
        * Se toma una operacion de flujo unificado del archivo "business.config.json"

        """
        input_data = ["", "", "", "", "", ""]
        operation = ["C33", "C40", "C41", "C42", "C44", "C66"]
        valid_header = [('C33', '          '), ('C40', '000000000000'), ('C41', '000000000000'), ('C42', '000000000000'), ('C44', '000000000000'), ('C66', '          ')]
        business_conf = BusinessConfig(file_action.get_business_config_json())
        message_bldg = MessageBuilding(business_conf)
        result = message_bldg.assemble_data(input_data, operation)
        self.assertEqual(valid_header, result)

    def test_26(self):
        """
        Prueba orientada a la construccion del campo de datos del mensaje,
        de acuerdo a la configuracion definida en el archivo
        "business.config.json" en el apartado "operations" y los campos
        correspondientes en el apartado "fields_definition"

        Se cambia la estructura de una operacion para validar
        que el metodo construye la operacion cambiando el orden, es 
        necesario que para cada cambio se asigne el "valor" que corresponde
        es decir si "C33" esta en la primera posicion, el valor en la entrada
        de datos debe estar en la primera posicion.

        """
        input_data = ["FACTURA1", "2000", "1000", "0", "15000", "Cajero1"]
        operation = ["C66", "C44", "C41", "C42", "C40", "C33"]
        valid_result = [('C66', 'FACTURA1  '), ('C44', '000000002000'), ('C41', '000000001000'), ('C42', '000000000000'), ('C40', '000000015000'), ('C33', 'Cajero1   ')]
        business_conf = BusinessConfig(file_action.get_business_config_json())
        message_bldg = MessageBuilding(business_conf)
        result = message_bldg.assemble_data(input_data, operation)
        self.assertEqual(valid_result, result)

    def test_27(self):
        """
        Prueba orientada a la construccion del campo de datos del mensaje,
        de acuerdo a la configuracion definida en el archivo
        "business.config.json" en el apartado "operations" y los campos
        correspondientes en el apartado "fields_definition"

        La misma operacion pero se agrega el campo "C95" que corresponde
        al descuento transaccion para validar que el metodo construye
        el "campo de datos" siempre y cuando la operacion y los datos 
        de entrada tengan la misma longitud de campos

        """
        input_data = ["Cajero1", "15000", "1500", "1000", "0", "FACTURA1", "1500"]
        operation = ["C33", "C40", "C41", "C42", "C44", "C66", "C95"]
        valid_result = [('C33', 'Cajero1   '), ('C40', '000000015000'), ('C41', '000000001500'), ('C42', '000000001000'), ('C44', '000000000000'), ('C66', 'FACTURA1  '), ('C95', '1500        ')]
        business_conf = BusinessConfig(file_action.get_business_config_json())
        message_bldg = MessageBuilding(business_conf)
        result = message_bldg.assemble_data(input_data, operation)
        self.assertEqual(valid_result, result)

    def test_28(self):
        """
        Prueba orientada a la construccion del campo de datos del mensaje,
        de acuerdo a la configuracion definida en el archivo
        "business.config.json" en el apartado "operations" y los campos
        correspondientes en el apartado "fields_definition"

        La misma operacion pero se agrega el campo "C95" que corresponde
        al descuento transaccion para validar que el metodo construye
        el "campo de datos" siempre y cuando la operacion y los datos 
        de entrada tengan la misma longitud de campos

        """
        input_data = ["Cajero1", "15000", "1500", "1000", "0", "FACTURA1"]
        operation = ["C33", "C40", "C41", "C42", "C44", "C66", "C95"]
        business_conf = BusinessConfig(file_action.get_business_config_json())
        message_bldg = MessageBuilding(business_conf)
        func = message_bldg.assemble_data
        with self.assertRaises(Exception): func(input_data, operation)

    def test_29(self):
        """
        Prueba orientada a la construccion del campo de datos del mensaje,
        de acuerdo a la configuracion definida en el archivo
        "business.config.json" en el apartado "operations" y los campos
        correspondientes en el apartado "fields_definition"

        Se modifica la configuracion para los tipo de dato de los campos:
            - "C33" de "ANS" a "N"
            - "C40" de "N" a "ANS"
            - "C66" de "ANS" a "N"

        """
        input_data = ["Cajero1", "15000", "1500", "1000", "0", "FACTURA1"]
        operation = ["C33", "C40", "C41", "C42", "C44", "C66"]
        valid_result = [('C33', '000Cajero1'), ('C40', '15000       '), ('C41', '000000001500'), ('C42', '000000001000'), ('C44', '000000000000'), ('C66', '00FACTURA1')]
        business_conf = BusinessConfig(file_action.get_business_config_json())
        fields = business_conf.get_fields_definition()
        fields["C33"]["data_type"] = "N"
        fields["C40"]["data_type"] = "ANS"
        fields["C66"]["data_type"] = "N"
        message_bldg = MessageBuilding(business_conf)
        result = message_bldg.assemble_data(input_data, operation)
        self.assertEqual(valid_result, result)

    def test_30(self):
        """
        Prueba orientada a la construccion del campo de datos del mensaje,
        de acuerdo a la configuracion definida en el archivo
        "business.config.json" en el apartado "operations" y los campos
        correspondientes en el apartado "fields_definition"

        Se modifica la configuracion para los tipo de dato de los campos:
            - "C33" de "ANS" a "INVALIDO"
        """
        input_data = ["Cajero1", "15000", "1500", "1000", "0", "FACTURA1"]
        operation = ["C33", "C40", "C41", "C42", "C44", "C66"]
        business_conf = BusinessConfig(file_action.get_business_config_json())
        fields = business_conf.get_fields_definition()
        fields["C33"]["data_type"] = "INVALIDO"
        message_bldg = MessageBuilding(business_conf)
        func = message_bldg.assemble_data
        with self.assertRaises(ValueError): func(input_data, operation)

    def test_31(self):
        """
        Prueba orientada a la construccion del campo de datos del mensaje,
        de acuerdo a la configuracion definida en el archivo
        "business.config.json" en el apartado "operations" y los campos
        correspondientes en el apartado "fields_definition"

        Se modifica la configuracion para los tipo de dato de los campos:
            - "C33" de "ANS" a "ans"
        """
        input_data = ["Cajero1", "15000", "1500", "1000", "0", "FACTURA1"]
        operation = ["C33", "C40", "C41", "C42", "C44", "C66"]
        business_conf = BusinessConfig(file_action.get_business_config_json())
        fields = business_conf.get_fields_definition()
        fields["C33"]["data_type"] = "ans"
        message_bldg = MessageBuilding(business_conf)
        func = message_bldg.assemble_data
        with self.assertRaises(ValueError): func(input_data, operation)

    def test_32(self):
        """
        Prueba orientada a la construccion del campo de datos del mensaje,
        de acuerdo a la configuracion definida en el archivo
        "business.config.json" en el apartado "operations" y los campos
        correspondientes en el apartado "fields_definition"

        Se modifica la configuracion para los tipo de dato de los campos:
            - "C40" de "N" a "n"
        """
        input_data = ["Cajero1", "15000", "1500", "1000", "0", "FACTURA1"]
        operation = ["C33", "C40", "C41", "C42", "C44", "C66"]
        business_conf = BusinessConfig(file_action.get_business_config_json())
        fields = business_conf.get_fields_definition()
        fields["C33"]["data_type"] = "ans"
        message_bldg = MessageBuilding(business_conf)
        func = message_bldg.assemble_data
        with self.assertRaises(ValueError): func(input_data, operation)

    def test_33(self):
        """
        Prueba orientada a la construccion del campo de datos del mensaje,
        de acuerdo a la configuracion definida en el archivo
        "business.config.json" en el apartado "operations" y los campos
        correspondientes en el apartado "fields_definition"

        Para el campo 'C33' se envia un valor con una longitud que supera
        la definida para ese campo en el archivo 'business.config.json'
        """
        input_data = ["Cajeroxxx1101001000000", "15000", "1500", "1000", "0", "FACTURA1"]
        operation = ["C33", "C40", "C41", "C42", "C44", "C66"]
        business_conf = BusinessConfig(file_action.get_business_config_json())
        message_bldg = MessageBuilding(business_conf)
        func = message_bldg.assemble_data
        with self.assertRaises(ValueError): func(input_data, operation)

    def test_34(self):
        """
        Prueba orientada a la construccion del campo de datos del mensaje,
        de acuerdo a la configuracion definida en el archivo
        "business.config.json" en el apartado "operations" y los campos
        correspondientes en el apartado "fields_definition"

        Una vez se tenga la estructura del mensaje, solo queda concatenar
        toda los campos que la constituyen para obtener el "campo de datos".

        """
        input_data = ["Cajero1", "15000", "1500", "1000", "0", "FACTURA1"]
        operation = ["C33", "C40", "C41", "C42", "C44", "C66"]
        valid_data_fields = [('C33', 'Cajero1   '), ('C40', '000000015000'), ('C41', '000000001500'), ('C42', '000000001000'), ('C44', '000000000000'), ('C66', 'FACTURA1  ')]
        valid_result = "3333000a43616a65726f312020201c3430000c3030303030303031353030301c3431000c3030303030303030313530301c3432000c3030303030303030313030301c3434000c3030303030303030303030301c3636000a46414354555241312020"
        business_conf = BusinessConfig(file_action.get_business_config_json())
        field_structure = business_conf.get_field_structure()
        message_bldg = MessageBuilding(business_conf)
        data_fields = message_bldg.assemble_data(input_data, operation)
        self.assertEqual(valid_data_fields, data_fields)
        result = hexlify(message_bldg.replace_values(data_fields, field_structure))
        self.assertEqual(valid_result, result)

    def test_35(self):
        """
        Prueba orientada a la construccion del campo de datos del mensaje,
        de acuerdo a la configuracion definida en el archivo
        "business.config.json" en el apartado "operations" y los campos
        correspondientes en el apartado "fields_definition"

        Una vez se tenga la estructura del mensaje, solo queda concatenar
        toda los campos que la constituyen para obtener el "campo de datos".

        * Se cambia la estructura del apartado "field_structure" con la finalidad
        de modificar las posiciones de cada campo de la estrucutra.
            - De esto "structure": ["field_code", "message_length", "value", "separador_campo"]
            - A esto "structure": ["value", "message_length", "separador_campo", "field_code"],

        """
        input_data = ["Cajero1", "15000", "1500", "1000", "0", "FACTURA1"]
        operation = ["C33", "C40", "C41", "C42", "C44", "C66"]
        valid_data_fields = [('C33', 'Cajero1   '), ('C40', '000000015000'), ('C41', '000000001500'), ('C42', '000000001000'), ('C44', '000000000000'), ('C66', 'FACTURA1  ')]
        valid_result = "3333000a43616a65726f312020201c3430000c3030303030303031353030301c3431000c3030303030303030313530301c3432000c3030303030303030313030301c3434000c3030303030303030303030301c3636000a46414354555241312020"
        business_conf = BusinessConfig(file_action.get_business_config_json())
        fs = business_conf.get_field_structure()
        struc = fs["structure"]
        struc[0], struc[2], struc[3] = struc[2], struc[3], struc[0]
        message_bldg = MessageBuilding(business_conf)
        data_fields = message_bldg.assemble_data(input_data, operation)
        self.assertEqual(valid_data_fields, data_fields)
        result = hexlify(message_bldg.replace_values(data_fields, fs))
        self.assertNotEqual(valid_result, result)

    def test_36(self):
        """
        Prueba orientada a la construccion del campo de datos del mensaje,
        de acuerdo a la configuracion definida en el archivo
        "business.config.json" en el apartado "operations" y los campos
        correspondientes en el apartado "fields_definition"

        Una vez se tenga la estructura del mensaje, solo queda concatenar
        toda los campos que la constituyen para obtener el "campo de datos".

        * Se cambia la estructura del apartado "field_structure" con la finalidad
        de modificar las posiciones de cada campo de la estrucutra.
            - De esto "structure": ["field_code", "message_length", "value", "separador_campo"]
            - A esto "structure": ["value", "message_length", "field_code", "separador_campo"]

        """
        input_data = ["Cajero1", "15000", "1500", "1000", "0", "FACTURA1"]
        operation = ["C33", "C40", "C41", "C42", "C44", "C66"]
        valid_data_fields = [('C33', 'Cajero1   '), ('C40', '000000015000'), ('C41', '000000001500'), ('C42', '000000001000'), ('C44', '000000000000'), ('C66', 'FACTURA1  ')]
        valid_result = "43616a65726f31202020000a33331c303030303030303135303030000c34301c303030303030303031353030000c34311c303030303030303031303030000c34321c303030303030303030303030000c34341c46414354555241312020000a3636"
        business_conf = BusinessConfig(file_action.get_business_config_json())
        fs = business_conf.get_field_structure()
        struc = fs["structure"]
        struc[0], struc[2] = struc[2], struc[0]
        message_bldg = MessageBuilding(business_conf)
        data_fields = message_bldg.assemble_data(input_data, operation)
        self.assertEqual(valid_data_fields, data_fields)
        result = hexlify(message_bldg.replace_values(data_fields, fs))
        self.assertEqual(valid_result, result)

    def test_37(self):
        """
        Prueba orientada a la construccion del campo de datos del mensaje,
        de acuerdo a la configuracion definida en el archivo
        "business.config.json" en el apartado "operations" y los campos
        correspondientes en el apartado "fields_definition"

        Una vez se tenga la estructura del mensaje, solo queda concatenar
        toda los campos que la constituyen para obtener el "campo de datos".

        * Se cambia la estructura del apartado "field_structure" con la finalidad
        de modificar las posiciones de cada campo de la estrucutra.
            - De esto "structure": ["field_code", "message_length", "value", "separador_campo"]
            - A esto "structure": ["value", "message_length", "field_code", "separador_campo"]

        * Se cambia la maxima longitud ("message_length"), parte de la estructura
        para indica la longitud del valor de un campo.

        """
        input_data = ["Cajero1", "15000", "1500", "1000", "0", "FACTURA1"]
        operation = ["C33", "C40", "C41", "C42", "C44", "C66"]
        valid_data_fields = [('C33', 'Cajero1   '), ('C40', '000000015000'), ('C41', '000000001500'), ('C42', '000000001000'), ('C44', '000000000000'), ('C66', 'FACTURA1  ')]
        valid_result = "43616a65726f31202020000000000a33331c303030303030303135303030000000000c34301c303030303030303031353030000000000c34311c303030303030303031303030000000000c34321c303030303030303030303030000000000c34341c46414354555241312020000000000a3636"
        business_conf = BusinessConfig(file_action.get_business_config_json())
        fs = business_conf.get_field_structure()
        fs["message_length"]["max_length"] = 5
        struc = fs["structure"]
        struc[0], struc[2] = struc[2], struc[0]
        message_bldg = MessageBuilding(business_conf)
        data_fields = message_bldg.assemble_data(input_data, operation)
        self.assertEqual(valid_data_fields, data_fields)
        result = hexlify(message_bldg.replace_values(data_fields, fs))
        self.assertEqual(valid_result, result)

    def test_38(self):
        """
        Prueba orientada a la construccion del campo de datos del mensaje,
        de acuerdo a la configuracion definida en el archivo
        "business.config.json" en el apartado "operations" y los campos
        correspondientes en el apartado "fields_definition"

        Una vez se tenga la estructura del mensaje, solo queda concatenar
        toda los campos que la constituyen para obtener el "campo de datos".

        * Se mantiene la estructura definida en el archivo "business.config.json"

        * Se cambia la maxima longitud ("message_length"), parte de la estructura
        para indica la longitud del valor de un campo.

        """
        input_data = ["Cajero1", "15000", "1500", "1000", "0", "FACTURA1"]
        operation = ["C33", "C40", "C41", "C42", "C44", "C66"]
        valid_data_fields = [('C33', 'Cajero1   '), ('C40', '000000015000'), ('C41', '000000001500'), ('C42', '000000001000'), ('C44', '000000000000'), ('C66', 'FACTURA1  ')]
        valid_result = "3333000000000a43616a65726f312020201c3430000000000c3030303030303031353030301c3431000000000c3030303030303030313530301c3432000000000c3030303030303030313030301c3434000000000c3030303030303030303030301c3636000000000a46414354555241312020"
        business_conf = BusinessConfig(file_action.get_business_config_json())
        fs = business_conf.get_field_structure()
        fs["message_length"]["max_length"] = 5
        message_bldg = MessageBuilding(business_conf)
        data_fields = message_bldg.assemble_data(input_data, operation)
        self.assertEqual(valid_data_fields, data_fields)
        result = hexlify(message_bldg.replace_values(data_fields, fs))
        self.assertEqual(valid_result, result)

    def test_39(self):
        """
        Prueba orientada a la construccion del campo de datos del mensaje,
        de acuerdo a la configuracion definida en el archivo
        "business.config.json" en el apartado "operations" y los campos
        correspondientes en el apartado "fields_definition"

        Una vez se tenga la estructura del mensaje, solo queda concatenar
        toda los campos que la constituyen para obtener el "campo de datos".

        * Se elimina de la estructura "message_length" y field_code, es decir:
            - De esto "structure": ["field_code", "message_length", "value", "separador_campo"]
            - A esto "structure": ["value", "separador_campo"]
        
        * Se cambia el valor para separar los campos por uno invalido, es decir:
            - De "separador_campo": {"value": "1C", "max_length": 1, ...}
            - A "separador_campo": {"value": "SEPARADOR", "max_length": 1, ...}


        """
        input_data = ["Cajero1", "15000", "1500", "1000", "0", "FACTURA1"]
        operation = ["C33", "C40", "C41", "C42", "C44", "C66"]
        valid_data_fields = [('C33', 'Cajero1   '), ('C40', '000000015000'), ('C41', '000000001500'), ('C42', '000000001000'), ('C44', '000000000000'), ('C66', 'FACTURA1  ')]
        business_conf = BusinessConfig(file_action.get_business_config_json())
        fs = business_conf.get_field_structure()
        struc = fs["structure"]
        struc.remove("message_length")
        struc.remove("field_code")
        fs["separador_campo"]["value"] = "SEPARADOR"

        message_bldg = MessageBuilding(business_conf)
        data_fields = message_bldg.assemble_data(input_data, operation)
        self.assertEqual(valid_data_fields, data_fields)
        func = message_bldg.replace_values
        with self.assertRaises(ValueError): func(data_fields, fs)

    def test_40(self):
        """
        Prueba orientada a la construccion del campo de datos del mensaje,
        de acuerdo a la configuracion definida en el archivo
        "business.config.json" en el apartado "operations" y los campos
        correspondientes en el apartado "fields_definition"

        Una vez se tenga la estructura del mensaje, solo queda concatenar
        toda los campos que la constituyen para obtener el "campo de datos".

        * Se elimina de la estructura "message_length" y field_code, es decir:
            - De esto "structure": ["field_code", "message_length", "value", "separador_campo"]
            - A esto "structure": ["value", "separador_campo"]
        
        * Se cambia el valor para separar los campos por uno invalido, es decir:
            - De "separador_campo": {"value": "1C", "max_length": 1, ...}
            - A "separador_campo": {"value": "2f", "max_length": 1, ...}
        """
        input_data = ["Cajero1", "15000", "1500", "1000", "0", "FACTURA1"]
        operation = ["C33", "C40", "C41", "C42", "C44", "C66"]
        valid_data_fields = [('C33', 'Cajero1   '), ('C40', '000000015000'), ('C41', '000000001500'), ('C42', '000000001000'), ('C44', '000000000000'), ('C66', 'FACTURA1  ')]
        valid_result = "43616a65726f312020202f3030303030303031353030302f3030303030303030313530302f3030303030303030313030302f3030303030303030303030302f46414354555241312020"
        business_conf = BusinessConfig(file_action.get_business_config_json())
        fs = business_conf.get_field_structure()
        struc = fs["structure"]
        struc.remove("message_length")
        struc.remove("field_code")
        fs["separador_campo"]["value"] = "2F"

        message_bldg = MessageBuilding(business_conf)
        data_fields = message_bldg.assemble_data(input_data, operation)
        self.assertEqual(valid_data_fields, data_fields)
        result = hexlify(message_bldg.replace_values(data_fields, fs))
        self.assertEqual(valid_result, result)

    def test_41(self):
        """Creacion de mensaje de flujo unificado"""
        input_data = ["00", "Cajero1", "15000", "1500", "1000", "0", "FACTURA1"]
        operation = ["C33", "C40", "C41", "C42", "C44", "C66"]
        valid_result = "0602011536303030303030303030313030303030301c3333000a43616a65726f312020201c3430000c3030303030303031353030301c3431000c3030303030303030313530301c3432000c3030303030303030313030301c3434000c3030303030303030303030301c3636000a464143545552413120200360"
        business_conf = BusinessConfig(file_action.get_business_config_json())
        message_bldg = MessageBuilding(business_conf)
        fields, msg = message_bldg.build_message(input_data, operation, "00")
        result = hexlify(msg)
        self.assertEqual(valid_result, result)

    def test_42(self):
        """Creacion de mensaje de flujo unificado
        Validaciones:
            * Se debe crear una mensaje solo con el cod_cajero, monto
            y nro_factura.
        """
        input_data = ["00", "Cajero1", "15000","FACTURA1"]
        operation = ["C33", "C40", "C66"]
        valid_result = "0602006436303030303030303030313030303030301c3333000a43616a65726f312020201c3430000c3030303030303031353030301c3636000a464143545552413120200306"
        business_conf = BusinessConfig(file_action.get_business_config_json())
        message_bldg = MessageBuilding(business_conf)
        fields, msg = message_bldg.build_message(input_data, operation, "00")
        result = hexlify(msg)
        self.assertEqual(valid_result, result)

    def test_43(self):
        """Creacion de mensaje de flujo unificado
        Validaciones:
            * Se debe crear una mensaje solo con monto.
        """
        input_data = ["00","15000"]
        operation = ["C40"]
        valid_result = "0602003436303030303030303030313030303030301c3430000c3030303030303031353030300310"
        business_conf = BusinessConfig(file_action.get_business_config_json())
        message_bldg = MessageBuilding(business_conf)
        fields, msg = message_bldg.build_message(input_data, operation, "00")
        result = hexlify(msg)
        self.assertEqual(valid_result, result)

    def test_44(self):
        """Creacion de mensaje de flujo unificado
        Validaciones:
            * Se debe intentar crear una mensaje con la estructura
            definida en "operation" donde se incluyen los siguientes valores:
                * C40 = Monto
                * C11 = Referencia Movil
                * C44 = Impuesto Consumo
                * C66 = Nro. Factura
                * C43 = Propina
            * Debe lanzar una excepcion de tipo:
                ValueError: 99, Longitud superada. Campo C11, valor ReferenciaMovil.
        """
        input_data = ["00","15000", "ReferenciaMovil", "1500", "Factura", "1500"]
        operation = ["C40", "C11", "C44", "C66", "C43"]
        business_conf = BusinessConfig(file_action.get_business_config_json())
        message_bldg = MessageBuilding(business_conf)
        func = message_bldg.build_message
        with self.assertRaises(ValueError): func(input_data, operation, "00")

    def test_45(self):
        """Creacion de mensaje de flujo unificado
        Validaciones:
            * Se debe intentar crear una mensaje con la estructura
            definida en "operation" donde se incluyen los siguientes valores:
                * C40 = Monto
                * C11 = Referencia Movil
                * C44 = Impuesto Consumo
                * C66 = Nro. Factura
                * C43 = Propina
        """
        input_data = ["00","15000", "ReferMovil", "1500", "Factura", "1500"]
        operation = ["C40", "C11", "C44", "C66", "C43"]
        valid_result = "0602009836303030303030303030313030303030301c3430000c3030303030303031353030301c3131000a52656665724d6f76696c1c3434000c3030303030303030313530301c3636000a466163747572612020201c3433000c30303030303030303135303003da"
        business_conf = BusinessConfig(file_action.get_business_config_json())
        message_bldg = MessageBuilding(business_conf)
        fields, msg = message_bldg.build_message(input_data, operation, "00")
        result = hexlify(msg)
        self.assertEqual(valid_result, result)

    def test_45(self):
        """Creacion de mensaje de flujo unificado
        Validaciones:
            * Se valida que "result" sea diferente
            a "valid_result" debido al cambio de estructura
        """
        input_data = ["00","15000", "ReferMovil", "1500", "Factura", "1500"]
        operation = ["C40", "C11", "C44", "C66", "C43"]
        valid_result = "0602009836303030303030303030313030303030301c3430000c3030303030303031353030301c3131000a52656665724d6f76696c1c3434000c3030303030303030313530301c3636000a466163747572612020201c3433000c30303030303030303135303003da"
        business_conf = BusinessConfig(file_action.get_business_config_json())
        struct = business_conf.get_message_definition()["structure"]
        struct[0], struct[2] = struct[2], struct[0]
        message_bldg = MessageBuilding(business_conf)
        fields, msg = message_bldg.build_message(input_data, operation, "00")
        result = hexlify(msg)
        self.assertNotEqual(valid_result, result)

    def test_45(self):
        """Creacion de mensaje de flujo unificado
        Validaciones:
            * Se valida que "result" sea diferente
            a "valid_result" debido al cambio de estructura
        """
        input_data = ["00","15000", "ReferMovil", "1500", "Factura", "1500"]
        operation = ["C40", "C11", "C44", "C66", "C43"]
        valid_result = "0098020636303030303030303030313030303030301c3430000c3030303030303031353030301c3131000a52656665724d6f76696c1c3434000c3030303030303030313530301c3636000a466163747572612020201c3433000c30303030303030303135303003da"
        business_conf = BusinessConfig(file_action.get_business_config_json())
        struct = business_conf.get_message_definition()["structure"]
        struct[0], struct[2] = struct[2], struct[0]
        message_bldg = MessageBuilding(business_conf)
        fields, msg = message_bldg.build_message(input_data, operation, "00")
        result = hexlify(msg)
        self.assertEqual(valid_result, result)

    def test_45(self):
        """Creacion de mensaje de flujo unificado
            Se cambia la estructura y el mensaje debe ser interpretado igual
                * Estructura originas = [CONFIRM_MESSAGE',STX','BCD','DATA','ETX', 'LRC']
                * Estructura modificada = ['BCD','STX','CONFIRM_MESSAGE','DATA','ETX','LRC']
        Validaciones:
            * Se valida que la estructura de "result"
            haya sido cambiada acorde a los cambios y
            no a la estructura definida en "business.config.json".
        """
        input_data = ["00","15000", "ReferMovil", "1500", "Factura", "1500"]
        operation = ["C40", "C11", "C44", "C66", "C43"]
        valid_result = "0098020636303030303030303030313030303030301c3430000c3030303030303031353030301c3131000a52656665724d6f76696c1c3434000c3030303030303030313530301c3636000a466163747572612020201c3433000c30303030303030303135303003da"
        business_conf = BusinessConfig(file_action.get_business_config_json())
        struct = business_conf.get_message_definition()["structure"]
        struct[0], struct[2] = struct[2], struct[0]
        message_bldg = MessageBuilding(business_conf)
        fields, msg = message_bldg.build_message(input_data, operation, "00")
        result = hexlify(msg)
        self.assertEqual(valid_result, result)

    def test_46(self):
        """Creacion de mensaje de flujo unificado
            Se cambia la estructura y el mensaje debe ser interpretado igual
                * Estructura originas = [CONFIRM_MESSAGE',STX','BCD','DATA','ETX', 'LRC']
                * Estructura modificada = ['STX','CONFIRM_MESSAGE','BCD','DATA','ETX','LRC']
        Validaciones:
            * Se valida que la estructura de "result"
            haya sido cambiada acorde a los cambios y
            no a la estructura definida en "business.config.json".
        """
        input_data = ["00","15000", "ReferMovil", "1500", "Factura", "1500"]
        operation = ["C40", "C11", "C44", "C66", "C43"]
        valid_result = "0206009836303030303030303030313030303030301c3430000c3030303030303031353030301c3131000a52656665724d6f76696c1c3434000c3030303030303030313530301c3636000a466163747572612020201c3433000c30303030303030303135303003da"
        business_conf = BusinessConfig(file_action.get_business_config_json())
        struct = business_conf.get_message_definition()["structure"]
        struct[0], struct[1] = struct[1], struct[0]
        message_bldg = MessageBuilding(business_conf)
        fields, msg = message_bldg.build_message(input_data, operation, "00")
        result = hexlify(msg)
        self.assertEqual(valid_result, result)

    def test_47(self):
        """Creacion de mensaje de flujo unificado
            Se cambia la estructura y el mensaje debe ser interpretado igual
                * Estructura originas = [CONFIRM_MESSAGE',STX','BCD','DATA','ETX', 'LRC']
                * Estructura modificada = ['BCD','STX','CONFIRM_MESSAGE','DATA','ETX','LRC']
        Validaciones:
            * Se valida que la estructura de "result"
            haya sido cambiada acorde a los cambios y
            no a la estructura definida en "business.config.json".
        """
        input_data = ["00","15000", "ReferMovil", "1500", "Factura", "1500"]
        operation = ["C40", "C11", "C44", "C66", "C43"]
        valid_result = "0200980636303030303030303030313030303030301c3430000c3030303030303031353030301c3131000a52656665724d6f76696c1c3434000c3030303030303030313530301c3636000a466163747572612020201c3433000c30303030303030303135303003da"
        business_conf = BusinessConfig(file_action.get_business_config_json())
        struct = business_conf.get_message_definition()["structure"]
        struct[0], struct[1], struct[2] = struct[1], struct[2], struct[0]
        message_bldg = MessageBuilding(business_conf)
        fields, msg = message_bldg.build_message(input_data, operation, "00")
        result = hexlify(msg)
        self.assertEqual(valid_result, result)

    def test_48(self):
        """Creacion de mensaje de flujo unificado
            Se cambia la estructura y el mensaje debe ser interpretado igual
                * Estructura originas = [CONFIRM_MESSAGE',STX','BCD','DATA','ETX', 'LRC']
                * Estructura modificada = ['BCD','STX','CONFIRM_MESSAGE','DATA','ETX','LRC']

            Se cambia la estructura de la cabecera del mensaje
                * Estructura original = ["transport_header","version", "req_res",
                    "cod_trans", "cod_res", "indicator", "separador_campo"]

                * Estructura modificada = ["indicator","version", "req_res",
                    "cod_trans", "cod_res", "transport_header", "separador_campo"]

        Validaciones:
            * Se valida que la estructura de "result"
            haya sido cambiada acorde a los cambios y
            no a la estructura definida en "business.config.json".
        """
        input_data = ["00","15000", "ReferMovil", "1500", "Factura", "1500"]
        operation = ["C40", "C11", "C44", "C66", "C43"]
        valid_result = "0200980630313030303030363030303030303030301c3430000c3030303030303031353030301c3131000a52656665724d6f76696c1c3434000c3030303030303030313530301c3636000a466163747572612020201c3433000c30303030303030303135303003da"
        business_conf = BusinessConfig(file_action.get_business_config_json())
        struct = business_conf.get_message_definition()["structure"]
        struct[0], struct[1], struct[2] = struct[1], struct[2], struct[0]
        data_structure = business_conf.get_data_frame()
        head_struc = data_structure["header_structure"]
        head_struc[0], head_struc[5] = head_struc[5], head_struc[0]

        message_bldg = MessageBuilding(business_conf)
        fields, msg = message_bldg.build_message(input_data, operation, "00")
        result = hexlify(msg)
        self.assertEqual(valid_result, result)

    def test_49(self):
        """Creacion de mensaje de flujo unificado
            Se cambia la estructura y el mensaje debe ser interpretado igual
                * Estructura originas = [CONFIRM_MESSAGE',STX','BCD','DATA','ETX', 'LRC']
                * Estructura modificada = ['BCD','STX','CONFIRM_MESSAGE','DATA','ETX','LRC']

            Se cambia la estructura de la cabecera del mensaje
                * Estructura original = ["transport_header","version", "req_res",
                    "cod_trans", "cod_res", "indicator", "separador_campo"]

                * Estructura modificada = ["indicator","version", "req_res",
                    "cod_trans", "cod_res", "transport_header", "separador_campo"]

        Validaciones:
            * Se valida que la estructura de "result"
            haya sido cambiada acorde a los cambios y
            no a la estructura definida en "business.config.json".
        """
        input_data = ["00","15000", "ReferMovil", "1500", "Factura", "1500"]
        operation = ["C40", "C11", "C44", "C66", "C43"]
        valid_result = "0200980630303130303030363030303030303030301c3430000c3030303030303031353030301c3131000a52656665724d6f76696c1c3434000c3030303030303030313530301c3636000a466163747572612020201c3433000c30303030303030303135303003da"
        business_conf = BusinessConfig(file_action.get_business_config_json())
        struct = business_conf.get_message_definition()["structure"]
        struct[0], struct[1], struct[2] = struct[1], struct[2], struct[0]
        data_structure = business_conf.get_data_frame()
        head_struc = data_structure["header_structure"]
        head_struc[0], head_struc[5], head_struc[3] = head_struc[3], head_struc[0], head_struc[5]

        message_bldg = MessageBuilding(business_conf)
        fields, msg = message_bldg.build_message(input_data, operation, "00")
        result = hexlify(msg)
        self.assertEqual(valid_result, result)

    def test_50(self):
        """Creacion de mensaje de flujo unificado
            Se cambia la estructura y el mensaje debe ser interpretado igual
                * Estructura originas = [CONFIRM_MESSAGE',STX','BCD','DATA','ETX', 'LRC']
                * Estructura modificada = ['BCD','STX','CONFIRM_MESSAGE','DATA','ETX','LRC']

            Se cambia la estructura de la cabecera del mensaje
                * Estructura original = ["transport_header","version", "req_res",
                    "cod_trans", "cod_res", "indicator", "separador_campo"]

                * Estructura modificada = ["transport_header", "indicator", "cod_res",
                    "cod_trans", "req_res", "version", "separador_campo"]

        Validaciones:
            * Se valida que la estructura de "result"
            haya sido cambiada acorde a los cambios y
            no a la estructura definida en "business.config.json".
        """
        input_data = ["00","15000", "ReferMovil", "1500", "Factura", "1500"]
        operation = ["C40", "C11", "C44", "C66", "C43"]
        valid_result = "0200980636303030303030303030303030303030311c3430000c3030303030303031353030301c3131000a52656665724d6f76696c1c3434000c3030303030303030313530301c3636000a466163747572612020201c3433000c30303030303030303135303003da"
        business_conf = BusinessConfig(file_action.get_business_config_json())
        struct = business_conf.get_message_definition()["structure"]
        struct[0], struct[1], struct[2] = struct[1], struct[2], struct[0]
        data_structure = business_conf.get_data_frame()
        head_struc = data_structure["header_structure"]
        head_struc[1], head_struc[5] = head_struc[5], head_struc[1]
        head_struc[2], head_struc[4] = head_struc[4], head_struc[2]
        message_bldg = MessageBuilding(business_conf)
        fields, msg = message_bldg.build_message(input_data, operation, "00")
        result = hexlify(msg)
        self.assertEqual(valid_result, result)

if __name__ == '__main__':
    file_action = FileActions(current_path)
    # Run the TestCase, main function is the unittest package
    main()


