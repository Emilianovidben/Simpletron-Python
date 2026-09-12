# SIMPLETRON 

memory = [0] * 100

accumulator = 0
instructionCounter = 0
instructionRegister = 0
operationCode = 0
operand = 0

print("*** Bienvenido a Simpletron ***")
print("*** Introduzca su programa ***")
print("*** Escriba 9999 para terminar ***")

i = 0

while i < 100:

    numero = int(input(f"{i:02d} ? "))

    if numero == 9999:
        break

    memory[i] = numero
    i += 1


print("\n*** Se terminó de cargar el programa ***")
print("*** Comienza la ejecución ***\n")

while True:
    instructionRegister = memory[instructionCounter]

    operationCode = instructionRegister // 100
    operand = instructionRegister % 100

    instructionCounter += 1

    if operationCode == 10:

        numero = int(input("? "))
        memory[operand] = numero

    elif operationCode == 11:

        print(memory[operand])

    elif operationCode == 20:

        accumulator = memory[operand]

    elif operationCode == 21:

        memory[operand] = accumulator

    elif operationCode == 30:

        accumulator = accumulator + memory[operand]

    elif operationCode == 31:

        accumulator = accumulator - memory[operand]

    elif operationCode == 32:

        if memory[operand] == 0:
            print("*** Error: división entre cero ***")
            break

        accumulator = accumulator // memory[operand]

    elif operationCode == 33:

        accumulator = accumulator * memory[operand]

    elif operationCode == 40:

        instructionCounter = operand

    elif operationCode == 41:

        if accumulator < 0:
            instructionCounter = operand

    elif operationCode == 42:

        if accumulator == 0:
            instructionCounter = operand

    elif operationCode == 43:

        print("\n*** Terminó la ejecución de Simpletron ***")
        break

    else:

        print("*** Error: operación inválida ***")
        break

print("\nREGISTROS")
print("accumulator:", accumulator)
print("instructionCounter:", instructionCounter)
print("instructionRegister:", instructionRegister)
print("operationCode:", operationCode)
print("operand:", operand)

print("\nMEMORIA")

for i in range(100):

    print(f"{i:02d}: {memory[i]}")

