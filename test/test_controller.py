from unittest import TestCase, main
from binascii import unhexlify, hexlify
from os import sys, path 
# It's necessary to add the current path to the entry path to help the import process
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
current_path = sys.path[-1]
from redeco_core.utils import FileActions, BusinessConfig, CommnController  
from redeco_core.utils import MessageBuilding, MessageReading, UserConfig

class TestMessageBuilding(TestCase):
    """
    Clase encargada de probar todas las funcionalidades pertenecientes
    a la clase CommnController
    """

    def test_1(self):
        """ 
        Prueba de la funcion que valida si esta presente el campo 'CONFIRM_MESSAGE'
        Test 1 -> No se incluye el campo CONFIRM_MESSAGE
        """
        kwargs = generate_kwargs()
        controller = CommnController(**kwargs)

        data = "02003736303030303030303030313039392020301c333300001c343000001c363900001c393300000302"
        data = unhexlify(data)
        result = controller.have_field_understood(data)
        self.assertFalse(result)

    def test_2(self):
        """ 
        Prueba de la funcion que valida si esta presente el campo 'CONFIRM_MESSAGE'
        Test 2 -> Se incluye el campo CONFIRM_MESSAGE, con el valor valido 06
        """
        kwargs = generate_kwargs()
        controller = CommnController(**kwargs)

        data = "0602003736303030303030303030313039392020301c333300001c343000001c363900001c393300000302"
        data = unhexlify(data)
        result = controller.have_field_understood(data)
        self.assertTrue(result)

    def test_3(self):
        """ 
        Prueba de la funcion que valida si esta presente el campo 'CONFIRM_MESSAGE'
        Test 3 -> Se incluye el campo CONFIRM_MESSAGE, con el valor valido 15
        """
        kwargs = generate_kwargs()
        controller = CommnController(**kwargs)

        data = "1502003736303030303030303030313039392020301c333300001c343000001c363900001c393300000302"
        data = unhexlify(data)
        result = controller.have_field_understood(data)
        self.assertTrue(result)

    def test_4(self):
        """ 
        Prueba de la funcion que valida si esta presente el campo 'CONFIRM_MESSAGE'
        Test 4 -> Se incluye el campo CONFIRM_MESSAGE, con el valor invalido 99
        """
        kwargs = generate_kwargs()
        controller = CommnController(**kwargs)

        data = "9902003736303030303030303030313039392020301c333300001c343000001c363900001c393300000302"
        data = unhexlify(data)
        result = controller.have_field_understood(data)
        self.assertFalse(result)

    def test_5(self):
        """ 
        Prueba de la funcion que valida si esta presente el campo 'CONFIRM_MESSAGE'.
        Test 5 -> Se incluye el campo CONFIRM_MESSAGE, con el valor valido 06,
                pero con cambio en la estructura.
        """
        kwargs = generate_kwargs()
        business_conf = kwargs.get('business_conf')
        controller = CommnController(**kwargs)
        structure = business_conf.get_message_definition()["structure"]
        # structure before [u'CONFIRM_MESSAGE', u'STX', u'BCD', u'DATA', u'ETX', u'LRC']
        structure[0], structure[1] = structure[1], structure[0]
        # structure after [u'STX', u'CONFIRM_MESSAGE', u'BCD', u'DATA', u'ETX', u'LRC']

        data = "0206003736303030303030303030313039392020301c333300001c343000001c363900001c393300000302"
        data = unhexlify(data)
        result = controller.have_field_understood(data)
        self.assertTrue(result)

    def test_6(self):
        """ 
        Prueba de la funcion que valida si esta presente el campo 'CONFIRM_MESSAGE'.
        Test 6 -> Se incluye el campo CONFIRM_MESSAGE, con el valor valido 15,
                pero con cambio en la estructura.
        """
        kwargs = generate_kwargs()
        business_conf = kwargs.get('business_conf')
        controller = CommnController(**kwargs)
        structure = business_conf.get_message_definition()["structure"]
        # structure before [u'CONFIRM_MESSAGE', u'STX', u'BCD', u'DATA', u'ETX', u'LRC']
        structure[0], structure[2] = structure[2], structure[0]
        # structure after [u'BCD', u'STX', u'CONFIRM_MESSAGE', u'DATA', u'ETX', u'LRC']

        data = "0037021536303030303030303030313039392020301c333300001c343000001c363900001c393300000302"
        data = unhexlify(data)
        result = controller.have_field_understood(data)
        self.assertTrue(result)

    def test_7(self):
        """ 
        Prueba de la funcion que valida si esta presente el campo 'CONFIRM_MESSAGE'.
        Test 7 -> Se incluye el campo CONFIRM_MESSAGE, con el valor invalido 99,
                pero con cambio en la estructura.
        """
        kwargs = generate_kwargs()
        business_conf = kwargs.get('business_conf')
        controller = CommnController(**kwargs)
        structure = business_conf.get_message_definition()["structure"]
        # structure before [u'CONFIRM_MESSAGE', u'STX', u'BCD', u'DATA', u'ETX', u'LRC']
        structure[0], structure[2] = structure[2], structure[0]
        # structure after [u'BCD', u'STX', u'CONFIRM_MESSAGE', u'DATA', u'ETX', u'LRC']

        data = "0037029936303030303030303030313039392020301c333300001c343000001c363900001c393300000302"
        data = unhexlify(data)
        result = controller.have_field_understood(data)
        self.assertFalse(result)

    def test_8(self):
        """
        Prueba de la funcion que identifica el tipo de flujo a
        partir de un mensaje recibido.

        Test 8 -> Se envia un mensaje de log Transaccional
        y se envia la operacion "00" de compra estandar.
        """
        data = "02003736303030303030303030313039392020301c333300001c343000001c363900001c393300000302"
        data = unhexlify(data)
        kwargs = generate_kwargs()
        controller = CommnController(**kwargs)
        is_unified, field_code, _  = controller.identify_flow(data)
        self.assertTrue(is_unified)
        self.assertEqual(field_code, "C69")

    def test_9(self):
        """
        Prueba de la funcion que identifica el tipo de flujo a
        partir de un mensaje recibido.

        Test 9 -> Se envia un mensaje de log Transaccional
        y se envia la operacion "00" de compra estandar.
        """
        data = "0602009136303030303030303030313030303030301c3333000a6a6573757340323620201c3430000c3030303030303031353030301c3639000230301c3933001e3020202020202020202020202020202020202020202020202020202020200394"
        data = unhexlify(data)
        kwargs = generate_kwargs()
        controller = CommnController(**kwargs)
        is_unified, field_code, _  = controller.identify_flow(data)
        self.assertFalse(is_unified)
        self.assertNotEqual(field_code, "C69")

    def test_10(self):
        """
        Prueba de la funcion que identifica el tipo de flujo a
        partir de un mensaje recibido.

        Test 10 -> Se envia un mensaje de log Transaccional
        y se envia la operacion "00" de compra estandar.
        """
        data = "0602009136303030303030303030313030303030301c3333000a6a6573757340323620201c3430000c3030303030303031353030301c3639000230301c3933001e3020202020202020202020202020202020202020202020202020202020200394"
        data = unhexlify(data)
        kwargs = generate_kwargs()
        controller = CommnController(**kwargs)
        is_unified, field_code, _  = controller.identify_flow(data)
        self.assertFalse(is_unified)
        self.assertNotEqual(field_code, "C69")

    def test_11(self):
        """
        Prueba de la funcion que identifica el tipo de flujo a
        partir de un mensaje recibido.

        Test 11 -> Se envia un mensaje de log transaccional
        incompleto y se envia la operacion "00" de compra estandar.
        """
        data = "0030313039392020301c333300001c343000001c363900001c393300000302"
        data = unhexlify(data)
        kwargs = generate_kwargs()
        controller = CommnController(**kwargs)
        func = controller.identify_flow
        with self.assertRaises(ValueError): func(data)

    def test_12(self):
        """
        Prueba de la funcion que identifica el tipo de flujo a
        partir de un mensaje recibido.

        Test 12 -> Solo envia un la cabecera del mensaje, es decir
        un mensaje incompleto.
        """
        data = "02003736303030303030303030313039392020301c"
        data = unhexlify(data)
        kwargs = generate_kwargs()
        controller = CommnController(**kwargs)
        func = controller.identify_flow
        with self.assertRaises(ValueError): func(data)
        
    def test_13(self):
        """
        Prueba de la funcion que identifica el tipo de flujo a
        partir de un mensaje recibido.

        Test 13 -> Se envia un mensaje con el valor "11" en el
        campo cod_trans
        """
        data = "02003736303030303030303030313031312020301c333300001c343000001c363900001c393300000302"
        data = unhexlify(data)
        kwargs = generate_kwargs()
        controller = CommnController(**kwargs)
        func = controller.identify_flow
        with self.assertRaises(KeyError): func(data)

    def test_14(self):
        """
        Prueba de la funcion que identifica el tipo de flujo a
        partir de un mensaje recibido.

        Test 14 -> Se modifica la estructura del archivo de configuracion
        para agregar un nuevo tipo de operacion que se enviaria en el
        campo "cod_trans" para posteriormente enviar un mensaje con el valor
        "11" en el campo "cod_trans" y obtener el campo "C100" donde se 
        enviaria el tipo de transaccion selecionada por el usuario.
        """
        data = "02003736303030303030303030313031312020301c333300001c343000001c363900001c393300000302"
        data = unhexlify(data)
        kwargs = generate_kwargs()
        business_conf = kwargs.get('business_conf')
        flows = business_conf._flows
        flows['11'] = {'is_unified': True, 'operation_field': 'C100'}
        controller = CommnController(**kwargs)
        is_unified, field_code, _  = controller.identify_flow(data)
        self.assertTrue(is_unified)
        self.assertEqual(field_code, "C100")

    def test_15(self):
        """
        Prueba de la funcion que identifica el tipo de flujo a
        partir de un mensaje recibido.

        Test 15 -> Este caso es igual que el "Test 14",
        excepto que para el campo "is_unified", se asigna False,
        indicando que no es flujo unificado.
        """
        data = "02003736303030303030303030313031312020301c333300001c343000001c363900001c393300000302"
        data = unhexlify(data)
        kwargs = generate_kwargs()
        business_conf = kwargs.get('business_conf')
        flows = business_conf._flows
        flows['11'] = {'is_unified': False, 'operation_field': 'C0001'}
        controller = CommnController(**kwargs)
        is_unified, field_code, _  = controller.identify_flow(data)
        self.assertFalse(is_unified)
        self.assertEqual(field_code, "C0001")

def generate_kwargs():
    business_conf = BusinessConfig(file_action.get_business_config_json())
    message_bldg = MessageBuilding(business_conf)
    message_rdg = MessageReading(business_conf, message_bldg)
    business_conf = BusinessConfig(file_action.get_business_config_json())

    kwargs = dict(message_rdg=message_rdg, business_conf=business_conf)
    kwargs.update(message_bldg=message_bldg, user_conf=user_conf)
    kwargs.update(file_action=file_action)
    return kwargs

if __name__ == '__main__':
    file_action = FileActions(current_path)
    user_conf = UserConfig(file_action.get_user_config_json())
    # Run the TestCase, main function is the unittest package
    main()


