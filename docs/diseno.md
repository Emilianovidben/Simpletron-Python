# Decisiones de diseño y apartados

## 2.1 Programación SML
Cada instrucción usa cuatro dígitos: dos para opcode y dos para operando. Los programas muestran entrada, salida, aritmética, almacenamiento, secuencia, decisiones y ciclos.

## 2.2 Simpletron
El simulador implementa el ciclo de búsqueda, decodificación, ejecución y actualización del contador. Tiene cinco registros, volcado de memoria y validaciones para entradas, opcodes, direcciones, división entre cero y desbordamiento.

## 2.3 Extensiones
Se implementan módulo (34), potencia (35), salto de línea (12), entrada y salida de cadenas (13 y 14). Las cadenas usan almacenamiento independiente de la memoria entera. Se conserva el límite de 100 palabras; no se implementa punto flotante.

## 2.4 Expresiones
La validación de agrupación comprueba (), [] y {}. Se usa una pila para convertir de infija a postfija y otra para evaluar. La potencia es asociativa por la derecha y la división es entera con truncamiento hacia cero.

## 2.5 Lenguaje Simple
Se admiten líneas ascendentes y comandos en minúscula: rem, input, let, print, goto, if/goto, end; variables de una letra y expresiones aritméticas y relacionales.

## 2.6 Compilador
Primera pasada: registra números de línea, genera instrucciones provisionales y crea referencias de datos. Segunda pasada: asigna direcciones a símbolos y resuelve saltos hacia adelante y hacia atrás. Programa y datos ocupan zonas separadas de memoria.

## 2.7 Repositorio
Se conservó Simpletron.py y se creó la rama proyecto-final para cambios independientes. README, programas, pruebas y documentación están organizados por carpeta.

## 2.8 Evidencias
Las capturas reales de uso de ramas, commits y ejecución deben obtenerse en el equipo de trabajo. No se sustituyen por ejemplos inventados.
