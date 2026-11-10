import unittest
from src.expresiones import validar_agrupacion, infija_a_postfija, evaluar, ErrorExpresion
from src.compilador import Compilador, ErrorCompilacion
from src.simpletron import Simpletron, ErrorSimpletron, leer_sml, escribir_sml


class PruebasProyecto(unittest.TestCase):
    def ejecutar(self, memoria, entradas=()):
        valores = iter(map(str, entradas))
        salidas = []
        maquina = Simpletron(lector=lambda mensaje: next(valores), escritor=salidas.append)
        maquina.cargar(memoria)
        maquina.ejecutar()
        return salidas, maquina

    def compilar_ejecutar(self, programa, entradas=()):
        return self.ejecutar(Compilador().compilar(programa), entradas)

    def test_agrupacion(self):
        self.assertTrue(validar_agrupacion('[2+{3*(1+2)}]'))
        self.assertFalse(validar_agrupacion('([)]'))

    def test_postfija(self):
        self.assertEqual(infija_a_postfija('2+3*(4+1)'), ['2','3','4','1','+','*','+'])

    def test_precedencia(self):
        self.assertEqual(evaluar('2+3*(4+1)^2'), 77)
        self.assertEqual(evaluar('-2^2'), -4)
        self.assertEqual(evaluar('2^3^2'), 512)
        self.assertEqual(evaluar('a*2', {'a':7}), 14)

    def test_division_entera(self):
        self.assertEqual(evaluar('-7/2'), -3)
        with self.assertRaises(ErrorExpresion):
            evaluar('8/0')

    def test_suma_sml(self):
        memoria = leer_sml('+1090\n+1091\n+2090\n+3091\n+2192\n+1192\n+4300')
        salidas, maquina = self.ejecutar(memoria, [7,8])
        self.assertEqual(salidas, ['15'])
        self.assertIn('REGISTROS', maquina.volcado())

    def test_cadenas(self):
        salidas, maquina = self.ejecutar([1390,1490,1200,4300], ['hola'])
        self.assertEqual(salidas, ['hola', ''])
        self.assertEqual(maquina.strings[90], 'hola')

    def test_mod_y_potencia(self):
        memoria = leer_sml('00 ? +2090\n01 ? +3591\n02 ? +2192\n03 ? +1192\n04 ? +2092\n05 ? +3493\n06 ? +2194\n07 ? +1194\n08 ? +4300\n90 ? +0002\n91 ? +0005\n93 ? +0003')
        salidas, _ = self.ejecutar(memoria)
        self.assertEqual(salidas, ['32','2'])

    def test_division_cero_sml(self):
        memoria = [2090,3291,4300] + [0]*87 + [12,0]
        with self.assertRaisesRegex(ErrorSimpletron,'División entre cero'):
            self.ejecutar(memoria)

    def test_opcode_invalido(self):
        with self.assertRaisesRegex(ErrorSimpletron,'Opcode inválido'):
            self.ejecutar([9900])

    def test_overflow(self):
        memoria = [2090,3091,4300] + [0]*87 + [9999,1]
        with self.assertRaisesRegex(ErrorSimpletron,'fuera del rango'):
            self.ejecutar(memoria)

    def test_salto_infinito(self):
        m = Simpletron()
        m.cargar([4000])
        with self.assertRaisesRegex(ErrorSimpletron,'Límite de instrucciones'):
            m.ejecutar(max_pasos=10)

    def test_compilar_suma(self):
        programa = '10 input a\n20 input b\n30 let c = a + b\n40 print c\n50 end'
        self.assertEqual(self.compilar_ejecutar(programa,[7,8])[0], ['15'])

    def test_factorial(self):
        programa = ('10 input n\n20 let f = 1\n30 if n <= 1 goto 70\n'
                    '40 let f = f * n\n50 let n = n - 1\n'
                    '60 goto 30\n70 print f\n80 end')
        self.assertEqual(self.compilar_ejecutar(programa,[5])[0], ['120'])

    def test_condiciones(self):
        programa = ('10 input a\n20 if a < 0 goto 60\n30 if a == 0 goto 80\n'
                    '40 print 1\n50 goto 90\n60 print -1\n70 goto 90\n'
                    '80 print 0\n90 end')
        for entrada, salida in [(-3,'-1'), (0,'0'), (8,'1')]:
            self.assertEqual(self.compilar_ejecutar(programa,[entrada])[0], [salida])

    def test_referencias_adelante(self):
        self.assertEqual(self.compilar_ejecutar('10 goto 30\n20 print 9\n30 print 7\n40 end')[0],['7'])

    def test_sintaxis_simple(self):
        with self.assertRaises(ErrorCompilacion):
            Compilador().compilar('20 print a\n10 end')
        with self.assertRaises(ErrorCompilacion):
            Compilador().compilar('10 goto 90\n20 end')
        with self.assertRaises(ErrorCompilacion):
            Compilador().compilar('10 INPUT a\n20 end')

    def test_roundtrip_sml(self):
        memoria = Compilador().compilar('10 let a = 7\n20 print a\n30 end')
        self.assertEqual(leer_sml(escribir_sml(memoria)), memoria)

    def test_comparaciones(self):
        for comparacion in ('<','<=','>','>=','==','!='):
            for a,b in [(1,2),(2,2),(4,2)]:
                fuente = f'10 let a = {a}\n20 let b = {b}\n30 if a {comparacion} b goto 60\n40 print 0\n50 goto 70\n60 print 1\n70 end'
                respuesta = '1' if eval(f'{a}{comparacion}{b}') else '0'
                self.assertEqual(self.compilar_ejecutar(fuente)[0], [respuesta])


if __name__ == '__main__':
    unittest.main()
