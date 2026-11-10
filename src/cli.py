import argparse
from pathlib import Path
from .expresiones import ErrorExpresion, evaluar, infija_a_postfija, validar_agrupacion
from .simpletron import ErrorSimpletron, Simpletron, leer_sml, escribir_sml
from .compilador import ErrorCompilacion, Compilador


def main(argv=None):
    parser = argparse.ArgumentParser(description='Proyecto final Simpletron')
    comandos = parser.add_subparsers(dest='accion', required=True)
    ejecutar = comandos.add_parser('ejecutar', help='Ejecutar archivo SML')
    ejecutar.add_argument('archivo')
    ejecutar.add_argument('--entrada', action='append', default=[])
    ejecutar.add_argument('--dump', action='store_true')
    ejecutar.add_argument('--max-pasos', type=int, default=100000)
    compilar_cmd = comandos.add_parser('compilar', help='Compilar Simple a SML')
    compilar_cmd.add_argument('archivo')
    compilar_cmd.add_argument('salida')
    expresion = comandos.add_parser('expresion', help='Convertir y evaluar expresión')
    expresion.add_argument('texto')
    expresion.add_argument('--variable', action='append', default=[])
    comandos.add_parser('cargar', help='Cargar instrucciones por teclado')
    args = parser.parse_args(argv)
    try:
        if args.accion == 'compilar':
            fuente = Path(args.archivo).read_text(encoding='utf-8')
            compilador = Compilador()
            memoria = compilador.compilar(fuente)
            Path(args.salida).write_text(escribir_sml(memoria), encoding='utf-8')
            print(f'Archivo generado: {args.salida}')
            print(f'Instrucciones: {len(compilador.codigo)}')
            print(f'Datos: {len(compilador.tabla_simbolos)}')
        elif args.accion == 'expresion':
            variables = {}
            for item in args.variable:
                nombre, valor = item.split('=', 1)
                variables[nombre] = int(valor)
            print('Agrupación:', 'correcta' if validar_agrupacion(args.texto) else 'incorrecta')
            print('Postfija:', ' '.join(infija_a_postfija(args.texto)))
            print('Resultado:', evaluar(args.texto, variables))
        elif args.accion == 'ejecutar':
            memoria = leer_sml(Path(args.archivo).read_text(encoding='utf-8'))
            entradas = iter(args.entrada)
            def leer(mensaje):
                try:
                    valor = next(entradas)
                    print(mensaje + valor)
                    return valor
                except StopIteration:
                    return input(mensaje)
            maquina = Simpletron(lector=leer)
            maquina.cargar(memoria)
            try:
                maquina.ejecutar(args.max_pasos)
            finally:
                if args.dump:
                    print(maquina.volcado())
        else:
            numeros = []
            print('Introduzca instrucciones. Escriba 9999 para terminar.')
            for i in range(100):
                numero = int(input(f'{i:02d} ? '))
                if numero == 9999:
                    break
                numeros.append(numero)
            maquina = Simpletron()
            maquina.cargar(numeros)
            try:
                maquina.ejecutar()
            finally:
                print(maquina.volcado())
    except (ErrorExpresion, ErrorSimpletron, ErrorCompilacion, ValueError, OSError, OverflowError) as error:
        parser.exit(1, f'Error: {error}\n')


if __name__ == '__main__':
    main()
