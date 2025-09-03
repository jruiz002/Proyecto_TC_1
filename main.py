from reader import Reader
from parsing import Parser
from nfa import NFA
from dfa import DFA
from time import process_time
import os

# File names
EXPRESSIONS_FILE = 'expressions.txt'
STRINGS_FILE = 'test_strings.txt'
RESULTS_FILE = 'results.txt'

def read_file_lines(filename):
    """Read lines from a file, skipping comments and empty lines"""
    with open(filename, 'r') as f:
        return [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]

def process_expression(expr, test_string):
    """Process a single expression and test string"""
    try:
        # Parse the regular expression
        reader = Reader(expr)
        tokens = list(reader.CreateTokens())
        parser = Parser(iter(tokens))
        tree = parser.Parse()
        
        # Process with NFA
        nfa = NFA(tree, reader.GetSymbols(), test_string)
        nfa_start = process_time()
        nfa_result = nfa.EvalRegex()
        nfa_time = process_time() - nfa_start
        
        # Process with DFA
        dfa = DFA(nfa.trans_func, nfa.symbols, nfa.curr_state, nfa.accepting_states, test_string)
        dfa.TransformNFAToDFA()
        dfa_start = process_time()
        dfa_result = dfa.EvalRegex()
        dfa_time = process_time() - dfa_start
        
        return {
            'expression': expr,
            'test_string': test_string,
            'nfa_result': nfa_result,
            'nfa_time': nfa_time,
            'dfa_result': dfa_result,
            'dfa_time': dfa_time,
            'success': True
        }
    except Exception as e:
        return {
            'expression': expr,
            'test_string': test_string,
            'error': str(e),
            'success': False
        }

def show_menu(test_cases):
    """Show the main menu and handle user input"""
    while True:
        print("\n=== MENÚ PRINCIPAL ===")
        print("1. Ver resultados de pruebas")
        print("2. Generar gráficas para un caso de prueba")
        print("3. Salir")
        
        choice = input("\nSeleccione una opción: ").strip()
        
        if choice == '1':
            show_test_results(test_cases)
        elif choice == '2':
            generate_graphs_menu(test_cases)
        elif choice == '3':
            print("¡Hasta luego!")
            return
        else:
            print("Opción no válida. Por favor, intente de nuevo.")

def show_test_results(test_cases):
    """Show the test results"""
    print("\n=== RESULTADOS DE PRUEBAS ===")
    for i, case in enumerate(test_cases, 1):
        print(f"\n--- Caso de Prueba {i} ---")
        print(f"Expresión: {case['expression']}")
        print(f"Cadena de prueba: '{case['test_string']}'")
        
        if case['success']:
            print(f"  Resultado NFA: {'Aceptada' if case['nfa_result'] else 'Rechazada'}")
            print(f"  Tiempo NFA: {case['nfa_time']:.2e} segundos")
            print(f"  Resultado DFA: {'Aceptada' if case['dfa_result'] else 'Rechazada'}")
            print(f"  Tiempo DFA: {case['dfa_time']:.2e} segundos")
        else:
            print(f"  Error: {case['error']}")

def generate_graphs_menu(test_cases):
    """Show menu to generate graphs for a test case"""
    if not test_cases:
        print("No hay casos de prueba disponibles.")
        return
    
    print("\n=== GENERAR GRÁFICAS ===")
    print("Casos de prueba disponibles:")
    for i, case in enumerate(test_cases, 1):
        status = "✓" if case['success'] else "✗"
        print(f"{i}. {status} Expresión: {case['expression']}")
        print(f"   Cadena: '{case['test_string']}'")
    
    while True:
        try:
            choice = input("\nSeleccione el número del caso de prueba (o '0' para cancelar): ").strip()
            if choice == '0':
                return
                
            case_num = int(choice)
            if 1 <= case_num <= len(test_cases):
                generate_graphs(test_cases[case_num - 1], case_num)
                break
            else:
                print("Número de caso no válido. Intente de nuevo.")
        except ValueError:
            print("Por favor ingrese un número válido.")

def generate_graphs(test_case, case_num):
    """Generate NFA and DFA graphs for a test case"""
    if not test_case['success']:
        print("No se pueden generar gráficos para un caso con errores.")
        return
    
    try:
        # Process the expression to get the automata
        reader = Reader(test_case['expression'])
        tokens = list(reader.CreateTokens())
        parser = Parser(iter(tokens))
        tree = parser.Parse()
        
        # Create NFA
        nfa = NFA(tree, reader.GetSymbols(), test_case['test_string'])
        
        # Create DFA from NFA
        dfa = DFA(nfa.trans_func, nfa.symbols, nfa.curr_state, nfa.accepting_states, test_case['test_string'])
        dfa.TransformNFAToDFA()
        
        # Generate graphs
        print("\nGenerando gráficos...")
        
        # Generate NFA graph
        nfa_pdf = f"nfa_case_{case_num}.pdf"
        nfa.WriteNFADiagram()
        if os.path.exists("nfa_diagram.pdf"):
            os.rename("nfa_diagram.pdf", nfa_pdf)
            print(f"Gráfico NFA guardado como: {nfa_pdf}")
        
        # Generate DFA graph
        dfa_pdf = f"dfa_case_{case_num}.pdf"
        dfa.GraphDFA()
        if os.path.exists("dfa_diagram.pdf"):
            os.rename("dfa_diagram.pdf", dfa_pdf)
            print(f"Gráfico DFA guardado como: {dfa_pdf}")
        
        print("¡Gráficos generados exitosamente!")
        
    except Exception as e:
        print(f"Error al generar los gráficos: {str(e)}")

def main():
    print("\n=== PROBADOR DE AUTÓMATAS FINITOS ===\n")
    print(f"Leyendo expresiones de: {EXPRESSIONS_FILE}")
    print(f"Leyendo cadenas de prueba de: {STRINGS_FILE}")
    print(f"Los resultados se guardarán en: {RESULTS_FILE}\n")
    
    # Read input files
    try:
        expressions = read_file_lines(EXPRESSIONS_FILE)
        test_strings = read_file_lines(STRINGS_FILE)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return
    
    # Check if files have the same number of test cases
    if len(expressions) != len(test_strings):
        print(f"Advertencia: {EXPRESSIONS_FILE} y {STRINGS_FILE} tienen diferente cantidad de casos de prueba")
        print(f"Usando el mínimo de {min(len(expressions), len(test_strings))} casos de prueba\n")
    
    # Process each test case
    test_cases = []
    for i, (expr, test_str) in enumerate(zip(expressions, test_strings), 1):
        print(f"\n--- Procesando Caso {i} ---")
        print(f"Expresión: {expr}")
        print(f"Cadena de prueba: '{test_str}'")
        
        result = process_expression(expr, test_str)
        test_cases.append(result)
        
        if result['success']:
            print("  Resultado NFA:", "Aceptada" if result['nfa_result'] else "Rechazada")
            print(f"  Tiempo NFA: {result['nfa_time']:.2e} segundos")
            print("  Resultado DFA:", "Aceptada" if result['dfa_result'] else "Rechazada")
            print(f"  Tiempo DFA: {result['dfa_time']:.2e} segundos")
        else:
            print(f"  Error: {result['error']}")
    
    # Save results to file
    with open(RESULTS_FILE, 'w', encoding='utf-8') as f:
        f.write("=== RESULTADOS DE PRUEBAS DE AUTÓMATAS FINITOS ===\n\n")
        f.write(f"Total de casos de prueba: {len(test_cases)}\n")
        f.write("-" * 70 + "\n\n")
        
        for i, result in enumerate(test_cases, 1):
            f.write(f"CASO DE PRUEBA {i}:\n")
            f.write(f"Expresión: {result['expression']}\n")
            f.write(f"Cadena de prueba: '{result['test_string']}'\n")
            
            if result['success']:
                f.write(f"Resultado NFA: {'Aceptada' if result['nfa_result'] else 'Rechazada'}\n")
                f.write(f"Tiempo NFA: {result['nfa_time']:.2e} segundos\n")
                f.write(f"Resultado DFA: {'Aceptada' if result['dfa_result'] else 'Rechazada'}\n")
                f.write(f"Tiempo DFA: {result['dfa_time']:.2e} segundos\n")
            else:
                f.write(f"Error: {result['error']}\n")
            
            f.write("\n" + "-" * 70 + "\n\n")
    
    print(f"\n=== Procesamiento completado ===")
    print(f"Resultados guardados en: {os.path.abspath(RESULTS_FILE)}")
    
    # Show the main menu
    show_menu(test_cases)

if __name__ == "__main__":
    main()
