import re
from .expresiones import infija_a_postfija, ErrorExpresion
from .simpletron import ErrorSimpletron, Simpletron


class ErrorCompilacion(ValueError):
    pass


class Compilador:
    ARITMETICA = {'+': 30, '-': 31, '/': 32, '*': 33, '^': 35}

    def __init__(self, tamano=100):
        self.tamano = tamano
        self.codigo = []
        self.etiquetas = {}
        self.datos = {}
        self.tabla_simbolos = {}
        self.contador_temporal = 0

    def variable(self, nombre):
        if not re.fullmatch('[a-z]', nombre):
            raise ErrorCompilacion('Las variables deben ser una sola letra minúscula')
        referencia = ('var', nombre)
        self.datos.setdefault(referencia, 0)
        return referencia

    def constante(self, numero):
        numero = int(numero)
        if not -9999 <= numero <= 9999:
            raise ErrorCompilacion('Constante fuera del rango SML')
        referencia = ('const', numero)
        self.datos.setdefault(referencia, numero)
        return referencia

    def temporal(self):
        self.contador_temporal += 1
        referencia = ('tmp', self.contador_temporal)
        self.datos[referencia] = 0
        return referencia

    def emitir(self, codigo, referencia=0):
        self.codigo.append((codigo, referencia))

    def compilar_expresion(self, expresion):
        try:
            postfija = infija_a_postfija(expresion)
        except ErrorExpresion as error:
            raise ErrorCompilacion(str(error)) from error
        pila = []
        for token in postfija:
            if token.isdigit():
                pila.append(self.constante(token))
            elif token in ('u+', 'u-'):
                if not pila:
                    raise ErrorCompilacion('Operando incompleto')
                a = pila.pop()
                if token == 'u-':
                    resultado = self.temporal()
                    self.emitir(20, self.constante(0))
                    self.emitir(31, a)
                    self.emitir(21, resultado)
                    pila.append(resultado)
                else:
                    pila.append(a)
            elif token in self.ARITMETICA:
                if len(pila) < 2:
                    raise ErrorCompilacion('Expresión incompleta')
                b = pila.pop()
                a = pila.pop()
                resultado = self.temporal()
                self.emitir(20, a)
                self.emitir(self.ARITMETICA[token], b)
                self.emitir(21, resultado)
                pila.append(resultado)
            else:
                pila.append(self.variable(token))
        if len(pila) != 1:
            raise ErrorCompilacion('Expresión inválida')
        return pila.pop()

    def condicion(self, texto):
        patron = r'^if\s+(.+?)\s*(<=|>=|==|!=|<|>)\s*(.+?)\s+goto\s+(\d+)\s*$'
        encontrada = re.fullmatch(patron, texto)
        if not encontrada:
            raise ErrorCompilacion('Condición inválida: if a < b goto 40')
        izquierda, comparacion, derecha, destino = encontrada.groups()
        a = self.compilar_expresion(izquierda)
        b = self.compilar_expresion(derecha)
        if comparacion in ('>', '>='):
            a, b = b, a
        self.emitir(20, a)
        self.emitir(31, b)
        destino = ('linea', int(destino))
        if comparacion in ('<', '>'):
            self.emitir(41, destino)
        elif comparacion in ('<=', '>='):
            self.emitir(41, destino)
            self.emitir(42, destino)
        elif comparacion == '==':
            self.emitir(42, destino)
        else:
            self.emitir(42, len(self.codigo) + 2)
            self.emitir(40, destino)

    def sentencia(self, texto):
        if re.fullmatch(r'rem(?:\s+.*)?', texto):
            return
        if texto != texto.lower():
            raise ErrorCompilacion('Solo se aceptan minúsculas en el lenguaje Simple')
        entrada = re.fullmatch(r'input\s+([a-z])', texto)
        if entrada:
            self.emitir(10, self.variable(entrada.group(1)))
            return
        asignacion = re.fullmatch(r'let\s+([a-z])\s*=\s*(.+)', texto)
        if asignacion:
            destino = self.variable(asignacion.group(1))
            valor = self.compilar_expresion(asignacion.group(2))
            self.emitir(20, valor)
            self.emitir(21, destino)
            return
        impresion = re.fullmatch(r'print\s+(.+)', texto)
        if impresion:
            valor = self.compilar_expresion(impresion.group(1))
            self.emitir(11, valor)
            return
        salto = re.fullmatch(r'goto\s+(\d+)', texto)
        if salto:
            self.emitir(40, ('linea', int(salto.group(1))))
            return
        if texto.startswith('if '):
            self.condicion(texto)
            return
        if texto == 'end':
            self.emitir(43)
            return
        raise ErrorCompilacion(f'Comando Simple no reconocido: {texto}')

    def compilar(self, fuente):
        entradas = []
        anterior = -1
        for linea in fuente.splitlines():
            if not linea.strip():
                continue
            encontrada = re.fullmatch(r'\s*(\d+)\s+(.+?)\s*', linea)
            if not encontrada:
                raise ErrorCompilacion(f'La línea debe tener número y comando: {linea}')
            numero = int(encontrada.group(1))
            if numero <= anterior:
                raise ErrorCompilacion('Los números de línea deben ser ascendentes y no repetidos')
            anterior = numero
            entradas.append((numero, encontrada.group(2)))
        if not entradas:
            raise ErrorCompilacion('El programa está vacío')
        for numero, texto in entradas:
            self.etiquetas[numero] = len(self.codigo)
            try:
                self.sentencia(texto)
            except (ErrorCompilacion, ErrorSimpletron) as error:
                raise ErrorCompilacion(f'Línea {numero}: {error}') from error
        if not self.codigo or self.codigo[-1][0] != 43:
            self.emitir(43)
        for indice in range(len(self.codigo)):
            if indice >= self.tamano:
                raise ErrorCompilacion('El programa excede 100 instrucciones')
        memoria = [0] * self.tamano
        direccion = self.tamano - 1
        for referencia, valor in self.datos.items():
            if direccion < len(self.codigo):
                raise ErrorCompilacion('No hay espacio para datos y programa')
            self.tabla_simbolos[referencia] = direccion
            memoria[direccion] = Simpletron.verificar_palabra(valor)
            direccion -= 1
        for indice, (opcode, operando) in enumerate(self.codigo):
            if isinstance(operando, tuple):
                if operando[0] == 'linea':
                    destino = operando[1]
                    if destino not in self.etiquetas:
                        raise ErrorCompilacion(f'No existe la línea {destino}')
                    direccion_destino = self.etiquetas[destino]
                else:
                    direccion_destino = self.tabla_simbolos[operando]
            else:
                direccion_destino = operando
            if not 0 <= direccion_destino < self.tamano:
                raise ErrorCompilacion(f'Dirección no válida: {direccion_destino}')
            memoria[indice] = Simpletron.verificar_palabra(opcode * 100 + direccion_destino)
        return memoria


def compilar(fuente):
    return Compilador().compilar(fuente)
