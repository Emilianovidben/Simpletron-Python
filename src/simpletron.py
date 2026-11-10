import re
from .expresiones import dividir_enteros


class ErrorSimpletron(Exception):
    pass


class Simpletron:
    INSTRUCCIONES = {
        10: 'READ', 11: 'WRITE', 12: 'NEWLINE', 13: 'READSTRING',
        14: 'WRITESTRING', 20: 'LOAD', 21: 'STORE', 30: 'ADD',
        31: 'SUBTRACT', 32: 'DIVIDE', 33: 'MULTIPLY', 34: 'MOD',
        35: 'POWER', 40: 'BRANCH', 41: 'BRANCHNEG',
        42: 'BRANCHZERO', 43: 'HALT'
    }

    def __init__(self, lector=input, escritor=print, tamano=100):
        if not 1 <= tamano <= 100:
            raise ValueError('Memoria permitida: 1 a 100 palabras')
        self.memory = [0] * tamano
        self.strings = {}
        self.lector = lector
        self.escritor = escritor
        self.accumulator = 0
        self.instructionCounter = 0
        self.instructionRegister = 0
        self.operationCode = 0
        self.operand = 0
        self.pasos = 0
        self.terminado = False

    @staticmethod
    def verificar_palabra(numero):
        if not isinstance(numero, int) or not -9999 <= numero <= 9999:
            raise ErrorSimpletron(f'Valor fuera del rango SML: {numero}')
        return numero

    def verificar_direccion(self, direccion):
        if not 0 <= direccion < len(self.memory):
            raise ErrorSimpletron(f'Dirección inválida: {direccion}')

    def cargar(self, palabras):
        palabras = list(palabras)
        if len(palabras) > len(self.memory):
            raise ErrorSimpletron('Programa mayor que la memoria disponible')
        self.memory = [0] * len(self.memory)
        for indice, numero in enumerate(palabras):
            self.memory[indice] = self.verificar_palabra(numero)
        self.strings.clear()
        self.accumulator = 0
        self.instructionCounter = 0
        self.instructionRegister = 0
        self.operationCode = 0
        self.operand = 0
        self.pasos = 0
        self.terminado = False

    def ejecutar(self, max_pasos=100000):
        while not self.terminado:
            if self.pasos >= max_pasos:
                raise ErrorSimpletron('Límite de instrucciones alcanzado')
            self.verificar_direccion(self.instructionCounter)
            palabra = self.memory[self.instructionCounter]
            if palabra < 0:
                raise ErrorSimpletron('Una instrucción no puede ser negativa')
            self.instructionRegister = palabra
            self.operationCode = palabra // 100
            self.operand = palabra % 100
            codigo = self.operationCode
            direccion = self.operand
            if codigo not in self.INSTRUCCIONES:
                raise ErrorSimpletron(f'Opcode inválido: {codigo}')
            self.verificar_direccion(direccion)
            self.instructionCounter += 1
            self.pasos += 1
            if codigo == 10:
                try:
                    valor = int(self.lector('? '))
                except (ValueError, EOFError) as error:
                    raise ErrorSimpletron('Entrada numérica inválida') from error
                self.memory[direccion] = self.verificar_palabra(valor)
            elif codigo == 11:
                self.escritor(str(self.memory[direccion]))
            elif codigo == 12:
                self.escritor('')
            elif codigo == 13:
                self.strings[direccion] = str(self.lector('Texto: '))
            elif codigo == 14:
                self.escritor(self.strings.get(direccion, ''))
            elif codigo == 20:
                self.accumulator = self.memory[direccion]
            elif codigo == 21:
                self.memory[direccion] = self.accumulator
            elif codigo == 30:
                self.accumulator = self.verificar_palabra(self.accumulator + self.memory[direccion])
            elif codigo == 31:
                self.accumulator = self.verificar_palabra(self.accumulator - self.memory[direccion])
            elif codigo == 32:
                if self.memory[direccion] == 0:
                    raise ErrorSimpletron('División entre cero')
                self.accumulator = self.verificar_palabra(dividir_enteros(self.accumulator, self.memory[direccion]))
            elif codigo == 33:
                self.accumulator = self.verificar_palabra(self.accumulator * self.memory[direccion])
            elif codigo == 34:
                divisor = self.memory[direccion]
                if divisor == 0:
                    raise ErrorSimpletron('Módulo entre cero')
                cociente = dividir_enteros(self.accumulator, divisor)
                self.accumulator = self.verificar_palabra(self.accumulator - cociente * divisor)
            elif codigo == 35:
                exponente = self.memory[direccion]
                if exponente < 0:
                    raise ErrorSimpletron('Exponente negativo')
                if abs(self.accumulator) > 1 and exponente > 14:
                    raise ErrorSimpletron('Desbordamiento del acumulador')
                self.accumulator = self.verificar_palabra(pow(self.accumulator, exponente))
            elif codigo == 40:
                self.instructionCounter = direccion
            elif codigo == 41 and self.accumulator < 0:
                self.instructionCounter = direccion
            elif codigo == 42 and self.accumulator == 0:
                self.instructionCounter = direccion
            elif codigo == 43:
                self.terminado = True
        return self.accumulator

    def volcado(self):
        lineas = [
            'REGISTROS',
            f'accumulator: {self.accumulator:+05d}',
            f'instructionCounter: {self.instructionCounter:02d}',
            f'instructionRegister: {self.instructionRegister:+05d}',
            f'operationCode: {self.operationCode:02d}',
            f'operand: {self.operand:02d}',
            '', 'MEMORIA'
        ]
        lineas.append('     ' + ' '.join(f'{i:>5}' for i in range(10)))
        for inicio in range(0, len(self.memory), 10):
            linea = f'{inicio:02d}:  ' + ' '.join(f'{n:+05d}' for n in self.memory[inicio:inicio + 10])
            lineas.append(linea)
        if self.strings:
            lineas.append('CADENAS')
            for direccion, valor in sorted(self.strings.items()):
                lineas.append(f'{direccion:02d}: {valor!r}')
        return '\n'.join(lineas)


def leer_sml(texto, tamano=100):
    memoria = [0] * tamano
    indice_siguiente = 0
    for linea in texto.splitlines():
        linea = linea.split('#', 1)[0].strip()
        if not linea:
            continue
        encontrada = re.fullmatch(r'(\d{1,2})\s*\?\s*([+-]?\d+)', linea)
        if encontrada:
            indice = int(encontrada.group(1))
            numero = int(encontrada.group(2))
        else:
            if not re.fullmatch(r'[+-]?\d+', linea):
                raise ErrorSimpletron(f'Formato SML inválido: {linea}')
            indice = indice_siguiente
            numero = int(linea)
        if not 0 <= indice < tamano:
            raise ErrorSimpletron(f'Dirección inválida: {indice}')
        memoria[indice] = Simpletron.verificar_palabra(numero)
        indice_siguiente = indice + 1
    return memoria


def escribir_sml(memoria):
    return '\n'.join(f'{i:02d} ? {n:+05d}' for i, n in enumerate(memoria)) + '\n'
