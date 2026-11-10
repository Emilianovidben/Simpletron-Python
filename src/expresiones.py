import re

OPERADORES = {
    '+': (1, 'izq'), '-': (1, 'izq'),
    '*': (2, 'izq'), '/': (2, 'izq'),
    'u+': (3, 'der'), 'u-': (3, 'der'),
    '^': (4, 'der')
}


class ErrorExpresion(ValueError):
    pass


def separar(expresion):
    patron = re.compile(r'\s*(\d+|[a-zA-Z][a-zA-Z0-9]*|[()+\-*/^\[\]{}])')
    tokens = []
    posicion = 0
    while posicion < len(expresion):
        if expulsion := re.match(r'\s+$', expresion[posicion:]):
            posicion += len(expulsion.group())
            break
        coincidencia = patron.match(expresion, posicion)
        if not coincidencia:
            raise ErrorExpresion(f'Símbolo no válido en posición {posicion + 1}')
        tokens.append(coincidencia.group(1))
        posicion = coincidencia.end()
    if not tokens:
        raise ErrorExpresion('Expresión vacía')
    return tokens


def validar_agrupacion(expresion):
    pila = []
    pares = {')': '(', ']': '[', '}': '{'}
    for simbolo in expresion:
        if simbolo in '([{':
            pila.append(simbolo)
        elif simbolo in ')]}':
            if not pila or pila.pop() != pares[simbolo]:
                return False
    return not pila


def infija_a_postfija(expresion):
    if not validar_agrupacion(expresion):
        raise ErrorExpresion('Símbolos de agrupación desbalanceados')
    salida = []
    pila = []
    anterior = 'inicio'
    for simbolo in separar(expresion):
        if simbolo.isdigit() or simbolo[0].isalpha():
            if anterior == 'valor':
                raise ErrorExpresion('Falta operador')
            salida.append(simbolo)
            anterior = 'valor'
        elif simbolo in '([{':
            if anterior == 'valor':
                raise ErrorExpresion('Falta operador antes de agrupar')
            pila.append('(')
            anterior = 'abre'
        elif simbolo in ')]}':
            if anterior != 'valor':
                raise ErrorExpresion('Agrupación vacía o incompleta')
            while pila and pila[-1] != '(':
                salida.append(pila.pop())
            if not pila:
                raise ErrorExpresion('Agrupación desbalanceada')
            pila.pop()
            anterior = 'valor'
        else:
            if simbolo in '+-' and anterior != 'valor':
                operador = 'u' + simbolo
                pila.append(operador)
                anterior = 'operador'
                continue
            if anterior != 'valor':
                raise ErrorExpresion('Operador sin operando')
            operador = simbolo
            prioridad, lado = OPERADORES[operador]
            while pila and pila[-1] in OPERADORES:
                prioridad_pila = OPERADORES[pila[-1]][0]
                if prioridad_pila > prioridad or (prioridad_pila == prioridad and lado == 'izq'):
                    salida.append(pila.pop())
                else:
                    break
            pila.append(operador)
            anterior = 'operador'
    if anterior != 'valor':
        raise ErrorExpresion('Expresión incompleta')
    while pila:
        simbolo = pila.pop()
        if simbolo == '(':
            raise ErrorExpresion('Agrupación desbalanceada')
        salida.append(simbolo)
    return salida


def dividir_enteros(a, b):
    if b == 0:
        raise ErrorExpresion('División entre cero')
    cociente = abs(a) // abs(b)
    return -cociente if (a < 0) != (b < 0) else cociente


def potencia_entera(a, b):
    if b < 0:
        raise ErrorExpresion('El exponente debe ser no negativo')
    return a ** b


def evaluar_postfija(postfija, variables=None):
    variables = variables or {}
    pila = []
    for simbolo in postfija:
        if simbolo in ('u+', 'u-'):
            if not pila:
                raise ErrorExpresion('Falta operando')
            a = pila.pop()
            pila.append(a if simbolo == 'u+' else -a)
        elif simbolo in ('+', '-', '*', '/', '^'):
            if len(pila) < 2:
                raise ErrorExpresion('Faltan operandos')
            b = pila.pop()
            a = pila.pop()
            if simbolo == '+':
                pila.append(a + b)
            elif simbolo == '-':
                pila.append(a - b)
            elif simbolo == '*':
                pila.append(a * b)
            elif simbolo == '/':
                pila.append(dividir_enteros(a, b))
            else:
                pila.append(potencia_entera(a, b))
        elif simbolo.isdigit():
            pila.append(int(simbolo))
        elif simbolo in variables:
            pila.append(int(variables[simbolo]))
        else:
            raise ErrorExpresion(f'Variable no definida: {simbolo}')
    if len(pila) != 1:
        raise ErrorExpresion('Expresión inválida')
    return pila[0]


def evaluar(expresion, variables=None):
    return evaluar_postfija(infija_a_postfija(expresion), variables)
