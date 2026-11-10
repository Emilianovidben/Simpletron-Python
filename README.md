# Proyecto final - Simpletron en Python

Simulador de computadora Simpletron, lenguaje de máquina SML, extensiones, conversión y evaluación de expresiones, lenguaje Simple y compilador de dos pasadas.

El archivo original `Simpletron.py` se conserva.

## Ejecutar

Requiere Python 3.8 o posterior. No usa librerías externas. Abrir terminal en la carpeta principal del repositorio.

```bash
python -m src.cli ejecutar programas/sml/suma.sml --entrada 7 --entrada 8 --dump
python -m src.cli ejecutar programas/sml/extension.sml
python -m src.cli cargar
```

## Compilar Simple a SML

```bash
python -m src.cli compilar programas/simple/suma.simple programas/sml/suma_generada.sml
python -m src.cli ejecutar programas/sml/suma_generada.sml --entrada 7 --entrada 8
python -m src.cli compilar programas/simple/factorial.simple programas/sml/factorial_generado.sml
python -m src.cli ejecutar programas/sml/factorial_generado.sml --entrada 5
```

## Expresiones

```bash
python -m src.cli expresion "2+3*(4+1)^2"
python -m src.cli expresion "a*4+2" --variable a=5
```

## Instrucciones SML

| Opcode | Instrucción |
|---|---|
| 10 | READ |
| 11 | WRITE |
| 12 | NEWLINE |
| 13 | READSTRING |
| 14 | WRITESTRING |
| 20 | LOAD |
| 21 | STORE |
| 30 | ADD |
| 31 | SUBTRACT |
| 32 | DIVIDE |
| 33 | MULTIPLY |
| 34 | MOD |
| 35 | POWER |
| 40 | BRANCH |
| 41 | BRANCHNEG |
| 42 | BRANCHZERO |
| 43 | HALT |

Se admiten 100 palabras de memoria, enteros de -9999 a +9999 y cadenas almacenadas por dirección en un área independiente. `MOD`, `POWER`, `NEWLINE`, `READSTRING` y `WRITESTRING` son extensiones. Los registros son `accumulator`, `instructionCounter`, `instructionRegister`, `operationCode` y `operand`.

## Lenguaje Simple

Incluye `rem`, `input`, `let`, `print`, `goto`, `if/goto`, `end`. Se aceptan números de línea ascendentes, variables de una letra minúscula, constantes enteras y operadores `+`, `-`, `*`, `/`, `^`, `<`, `<=`, `>`, `>=`, `==`, `!=`.

```text
10 input a
20 let b = a * 2 + 3
30 if b < 10 goto 50
40 print b
50 end
```

El compilador registra referencias en una primera pasada y las resuelve en una segunda pasada. Código y datos se almacenan en regiones distintas.

## Pruebas

```bash
python -m unittest discover -s pruebas -v
```

## Archivos

- `Simpletron.py`: código original.
- `src/simpletron.py`: simulador SML.
- `src/expresiones.py`: conversión y evaluación de expresiones.
- `src/compilador.py`: compilador Simple a SML.
- `src/cli.py`: comandos.
- `programas/simple` y `programas/sml`: ejemplos.
- `pruebas`: pruebas automatizadas.
- `docs`: diseño y entregables.
- `evidencias`: carpeta para capturas reales de pruebas y Git.

La entrega final consiste en la URL del repositorio GitHub. Revisar `docs/entrega.md` antes de entregar.
