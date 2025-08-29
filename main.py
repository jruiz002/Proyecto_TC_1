from automata.nfa import NFA
from automata.subset_construction import subset_construction
from automata.dfa_minimization import minimize_dfa
from collections import defaultdict, deque
import networkx as nx
import matplotlib.pyplot as plt
import os

def get_precedence(c):
    """
    Calcula la precedencia para operadores de expresiones regulares.
    Precedencias para ERs:
    '(' -> 1
    '|' -> 2
    '.' -> 3
    '?' -> 4
    '*' -> 4
    '+' -> 4
    '^' -> 5
    """
    precedence_map = {
        '(': 1,
        '|': 2,
        '.': 3,
        '?': 4,
        '*': 4,
        '+': 4,
        '^': 5
    }
    return precedence_map.get(c, 0)

def preprocess_regex(regex):
    """
    Preprocesa la expresión regular para manejar caracteres escapados.
    """
    # Eliminar espacios en blanco
    regex = regex.replace(' ', '')
    
    # Reemplazar epsilon por ε
    regex = regex.replace('epsilon', 'ε')
    regex = regex.replace('ε', 'ε')
    
    return regex

def format_regex(regex):
    """
    Formatea la expresión regular añadiendo operadores de concatenación explícitos ('.').
    """
    result = []
    i = 0
    
    while i < len(regex):
        current = regex[i]
        result.append(current)
        
        if i + 1 < len(regex):
            next_char = regex[i + 1]
            
            # Añadir operador de concatenación si es necesario
            if (current not in ['(', '|'] and next_char not in [')', '|', '*', '+', '?']):
                result.append('.')
        
        i += 1
    
    return ''.join(result)

def infix_to_postfix(regex):
    """
    Convierte una expresión regular en notación infix a postfix usando el algoritmo Shunting Yard.
    """
    postfix = []
    stack = []
    
    for char in regex:
        if char == '(':
            stack.append(char)
        elif char == ')':
            while stack and stack[-1] != '(':
                postfix.append(stack.pop())
            if stack and stack[-1] == '(':
                stack.pop()  # Descartar el paréntesis izquierdo
        elif char in ['|', '.', '?', '*', '+']:
            while stack and stack[-1] != '(' and get_precedence(stack[-1]) >= get_precedence(char):
                postfix.append(stack.pop())
            stack.append(char)
        else:
            postfix.append(char)
    
    # Vaciar la pila de operadores
    while stack:
        postfix.append(stack.pop())
    
    return ''.join(postfix)

def thompson_construction(postfix):
    """
    Construye un AFN usando el algoritmo de Thompson a partir de una expresión regular en notación postfix
    """
    stack = []
    
    for symbol in postfix:
        if symbol == '.':
            # Concatenación
            if len(stack) < 2:
                raise ValueError("Expresión inválida para concatenación")
            
            nfa2 = stack.pop()
            nfa1 = stack.pop()
            
            # Crear un nuevo NFA para la concatenación
            result = NFA()
            
            # Copiar estados y transiciones de nfa1
            for state_id, state in nfa1.states.items():
                new_state = result.create_state(is_final=state.is_final)
                if state_id == nfa1.start_state:
                    result.set_start_state(new_state)
            
            # Mapeo de estados antiguos a nuevos para nfa1
            state_map_nfa1 = {old_id: new_id for old_id, new_id in 
                             zip(nfa1.states.keys(), list(result.states.keys())[:len(nfa1.states)])}
            
            # Copiar transiciones de nfa1
            for old_id, state in nfa1.states.items():
                for symbol, targets in state.transitions.items():
                    for target in targets:
                        result.add_transition(state_map_nfa1[old_id], symbol, 
                                             result.states[state_map_nfa1[target]])
            
            # Copiar estados de nfa2
            start_idx = len(result.states)
            for state_id, state in nfa2.states.items():
                new_state = result.create_state(is_final=state.is_final)
            
            # Mapeo de estados antiguos a nuevos para nfa2
            state_map_nfa2 = {old_id: new_id for old_id, new_id in 
                             zip(nfa2.states.keys(), list(result.states.keys())[start_idx:])}
            
            # Copiar transiciones de nfa2
            for old_id, state in nfa2.states.items():
                for symbol, targets in state.transitions.items():
                    for target in targets:
                        result.add_transition(state_map_nfa2[old_id], symbol, 
                                             result.states[state_map_nfa2[target]])
            
            # Conectar nfa1 con nfa2
            for old_id in nfa1.final_states:
                result.add_epsilon_transition(state_map_nfa1[old_id], 
                                            result.states[state_map_nfa2[nfa2.start_state]])
                result.states[state_map_nfa1[old_id]].is_final = False
            
            # Actualizar estados finales
            result.final_states = {state_map_nfa2[fs] for fs in nfa2.final_states}
            
            stack.append(result)
        
        elif symbol == '|':
            # Unión
            if len(stack) < 2:
                raise ValueError("Expresión inválida para unión")
            
            nfa2 = stack.pop()
            nfa1 = stack.pop()
            
            # Crear un nuevo AFN con un nuevo estado inicial y final
            result = NFA()
            start = result.create_state()
            result.set_start_state(start)
            
            end = result.create_state(is_final=True)
            
            # Copiar estados y transiciones de nfa1
            start_idx = len(result.states)
            for state_id, state in nfa1.states.items():
                new_state = result.create_state(is_final=False)  # No hay estados finales internos
            
            # Mapeo de estados antiguos a nuevos para nfa1
            state_map_nfa1 = {old_id: new_id for old_id, new_id in 
                             zip(nfa1.states.keys(), list(result.states.keys())[start_idx:start_idx+len(nfa1.states)])}
            
            # Copiar transiciones de nfa1
            for old_id, state in nfa1.states.items():
                for symbol, targets in state.transitions.items():
                    for target in targets:
                        result.add_transition(state_map_nfa1[old_id], symbol, 
                                             result.states[state_map_nfa1[target]])
            
            # Copiar estados de nfa2
            start_idx = len(result.states)
            for state_id, state in nfa2.states.items():
                new_state = result.create_state(is_final=False)  # No hay estados finales internos
            
            # Mapeo de estados antiguos a nuevos para nfa2
            state_map_nfa2 = {old_id: new_id for old_id, new_id in 
                             zip(nfa2.states.keys(), list(result.states.keys())[start_idx:])}
            
            # Copiar transiciones de nfa2
            for old_id, state in nfa2.states.items():
                for symbol, targets in state.transitions.items():
                    for target in targets:
                        result.add_transition(state_map_nfa2[old_id], symbol, 
                                             result.states[state_map_nfa2[target]])
            
            # Añadir transiciones epsilon desde el nuevo estado inicial a los estados iniciales de nfa1 y nfa2
            result.add_epsilon_transition(start.state_id, result.states[state_map_nfa1[nfa1.start_state]])
            result.add_epsilon_transition(start.state_id, result.states[state_map_nfa2[nfa2.start_state]])
            
            # Añadir transiciones epsilon desde los estados finales de nfa1 y nfa2 al nuevo estado final
            for final_state in nfa1.final_states:
                result.add_epsilon_transition(state_map_nfa1[final_state], end)
            
            for final_state in nfa2.final_states:
                result.add_epsilon_transition(state_map_nfa2[final_state], end)
            
            # Actualizar estados finales
            result.final_states = {end.state_id}
            
            stack.append(result)
        
        elif symbol == '*':
            # Cerradura de Kleene
            if not stack:
                raise ValueError("Expresión inválida para cerradura de Kleene")
            
            nfa = stack.pop()
            
            # Crear un nuevo AFN con un nuevo estado inicial y final
            result = NFA()
            start = result.create_state()
            result.set_start_state(start)
            
            end = result.create_state(is_final=True)
            
            # Copiar estados y transiciones de nfa
            start_idx = len(result.states)
            for state_id, state in nfa.states.items():
                new_state = result.create_state(is_final=False)  # No hay estados finales internos
            
            # Mapeo de estados antiguos a nuevos
            state_map = {old_id: new_id for old_id, new_id in 
                        zip(nfa.states.keys(), list(result.states.keys())[start_idx:])}
            
            # Copiar transiciones
            for old_id, state in nfa.states.items():
                for symbol, targets in state.transitions.items():
                    for target in targets:
                        result.add_transition(state_map[old_id], symbol, 
                                             result.states[state_map[target]])
            
            # Añadir transición epsilon desde el nuevo estado inicial al estado inicial de nfa
            result.add_epsilon_transition(start.state_id, result.states[state_map[nfa.start_state]])
            
            # Añadir transición epsilon desde el nuevo estado inicial al nuevo estado final
            result.add_epsilon_transition(start.state_id, end)
            
            # Añadir transiciones epsilon desde los estados finales de nfa al estado inicial de nfa y al nuevo estado final
            for final_state in nfa.final_states:
                result.add_epsilon_transition(state_map[final_state], result.states[state_map[nfa.start_state]])
                result.add_epsilon_transition(state_map[final_state], end)
            
            # Actualizar estados finales
            result.final_states = {end.state_id}
            
            stack.append(result)
        
        elif symbol == '+':
            # Una o más ocurrencias
            if not stack:
                raise ValueError("Expresión inválida para una o más ocurrencias")
            
            nfa = stack.pop()
            
            # Crear un nuevo AFN con un nuevo estado inicial y final
            result = NFA()
            start = result.create_state()
            result.set_start_state(start)
            
            end = result.create_state(is_final=True)
            
            # Copiar estados y transiciones de nfa
            start_idx = len(result.states)
            for state_id, state in nfa.states.items():
                new_state = result.create_state(is_final=False)  # No hay estados finales internos
            
            # Mapeo de estados antiguos a nuevos
            state_map = {old_id: new_id for old_id, new_id in 
                        zip(nfa.states.keys(), list(result.states.keys())[start_idx:])}
            
            # Copiar transiciones
            for old_id, state in nfa.states.items():
                for symbol, targets in state.transitions.items():
                    for target in targets:
                        result.add_transition(state_map[old_id], symbol, 
                                             result.states[state_map[target]])
            
            # Añadir transición epsilon desde el nuevo estado inicial al estado inicial de nfa
            result.add_epsilon_transition(start.state_id, result.states[state_map[nfa.start_state]])
            
            # Añadir transiciones epsilon desde los estados finales de nfa al estado inicial de nfa y al nuevo estado final
            for final_state in nfa.final_states:
                result.add_epsilon_transition(state_map[final_state], result.states[state_map[nfa.start_state]])
                result.add_epsilon_transition(state_map[final_state], end)
            
            # Actualizar estados finales
            result.final_states = {end.state_id}
            
            stack.append(result)
        
        elif symbol == '?':
            # Cero o una ocurrencia
            if not stack:
                raise ValueError("Expresión inválida para cero o una ocurrencia")
            
            nfa = stack.pop()
            
            # Crear un nuevo AFN con un nuevo estado inicial y final
            result = NFA()
            start = result.create_state()
            result.set_start_state(start)
            
            end = result.create_state(is_final=True)
            
            # Copiar estados y transiciones de nfa
            start_idx = len(result.states)
            for state_id, state in nfa.states.items():
                new_state = result.create_state(is_final=False)  # No hay estados finales internos
            
            # Mapeo de estados antiguos a nuevos
            state_map = {old_id: new_id for old_id, new_id in 
                        zip(nfa.states.keys(), list(result.states.keys())[start_idx:])}
            
            # Copiar transiciones
            for old_id, state in nfa.states.items():
                for symbol, targets in state.transitions.items():
                    for target in targets:
                        result.add_transition(state_map[old_id], symbol, 
                                             result.states[state_map[target]])
            
            # Añadir transición epsilon desde el nuevo estado inicial al estado inicial de nfa
            result.add_epsilon_transition(start.state_id, result.states[state_map[nfa.start_state]])
            
            # Añadir transición epsilon desde el nuevo estado inicial al nuevo estado final
            result.add_epsilon_transition(start.state_id, end)
            
            # Añadir transiciones epsilon desde los estados finales de nfa al nuevo estado final
            for final_state in nfa.final_states:
                result.add_epsilon_transition(state_map[final_state], end)
            
            # Actualizar estados finales
            result.final_states = {end.state_id}
            
            stack.append(result)
        
        else:
            # Símbolo
            nfa = NFA()
            start = nfa.create_state()
            nfa.set_start_state(start)
            
            end = nfa.create_state(is_final=True)
            
            # Manejar epsilon (ε)
            if symbol == 'ε':
                nfa.add_epsilon_transition(start.state_id, end)
            else:
                nfa.add_transition(start.state_id, symbol, end)
                nfa.alphabet.add(symbol)
            
            nfa.final_states = {end.state_id}
            
            stack.append(nfa)
    
    if len(stack) != 1:
        raise ValueError("Expresión regular inválida")
    
    return stack[0]

def visualize_automaton(automaton, title, filename):
    """
    Visualiza un autómata (NFA o DFA) usando networkx y matplotlib
    """
    G = nx.DiGraph()
    
    # Añadir nodos
    for state_id, state in automaton.states.items():
        if state.is_final:
            G.add_node(state_id, shape='doublecircle')
        else:
            G.add_node(state_id, shape='circle')
    
    # Añadir arcos
    for state_id, state in automaton.states.items():
        for symbol, targets in state.transitions.items():
            # Asegurarse de que targets sea iterable
            if isinstance(targets, (list, set)):
                for target in targets:
                    G.add_edge(state_id, target, label=symbol)
            else:
                # Si targets no es iterable, podría ser un solo estado
                G.add_edge(state_id, targets, label=symbol)
    
    # Verificar si hay nodos en el grafo
    if not G.nodes():
        print(f"No se pudieron visualizar los estados para {title}")
        return
    
    # Crear figura
    plt.figure(figsize=(10, 8))
    pos = nx.spring_layout(G, seed=42)  # Posición de los nodos
    
    # Dibujar nodos
    nx.draw_networkx_nodes(G, pos, node_size=700)
    
    # Dibujar nodos finales con doble círculo
    final_states = [state_id for state_id, state in automaton.states.items() if state.is_final]
    if final_states:
        nx.draw_networkx_nodes(G, pos, nodelist=final_states, node_size=700, node_color='lightblue')
    
    # Dibujar estado inicial con un color diferente
    if automaton.start_state is not None and automaton.start_state in G.nodes():
        nx.draw_networkx_nodes(G, pos, nodelist=[automaton.start_state], node_size=700, node_color='lightgreen')
    
    # Dibujar arcos
    nx.draw_networkx_edges(G, pos, arrowsize=20)
    
    # Dibujar etiquetas de nodos
    nx.draw_networkx_labels(G, pos, font_size=12)
    
    # Dibujar etiquetas de arcos
    if G.edges():
        edge_labels = {(u, v): d['label'] for u, v, d in G.edges(data=True)}
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=10)
    
    # Añadir título
    plt.title(title)
    plt.axis('off')
    
    # Crear directorio para guardar imágenes si no existe
    os.makedirs('automata_images', exist_ok=True)
    
    # Guardar imagen
    plt.savefig(f'automata_images/{filename}.png', dpi=300, bbox_inches='tight')
    plt.close()

def read_regex_from_file(file_path):
    """Lee expresiones regulares y cadenas de prueba desde un archivo"""
    regex_data = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            
            i = 0
            while i < len(lines):
                # Leer la expresión regular
                regex_line = lines[i].strip()
                if regex_line:
                    # Leer la siguiente línea para la cadena de prueba
                    if i + 1 < len(lines):
                        test_string = lines[i + 1].strip()
                        regex_data.append((regex_line, test_string))
                        i += 2
                    else:
                        # Si no hay cadena de prueba, usar cadena vacía
                        regex_data.append((regex_line, ""))
                        i += 1
                else:
                    i += 1
    
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {file_path}")
    except Exception as e:
        print(f"Error al leer el archivo: {e}")
    
    return regex_data

def process_regex(regex, test_string, index):
    """Procesa una expresión regular y verifica si una cadena pertenece al lenguaje"""
    try:
        # Preprocesar la expresión regular
        preprocessed_regex = preprocess_regex(regex)
        
        # Formatear la expresión regular (añadir operador de concatenación explícito)
        formatted_regex = format_regex(preprocessed_regex)
        
        # Convertir de infix a postfix
        postfix = infix_to_postfix(formatted_regex)
        
        # Construir el AFN usando el algoritmo de Thompson
        nfa = thompson_construction(postfix)
        
        # Visualizar el AFN
        visualize_automaton(nfa, f"AFN para {regex}", f"nfa_{index}")
        
        # Convertir el AFN a AFD usando el algoritmo de subconjuntos
        dfa = subset_construction(nfa)
        
        # Visualizar el AFD
        visualize_automaton(dfa, f"AFD para {regex}", f"dfa_{index}")
        
        # Minimizar el AFD
        minimized_dfa = minimize_dfa(dfa)
        
        # Visualizar el AFD minimizado
        visualize_automaton(minimized_dfa, f"AFD Minimizado para {regex}", f"minimized_dfa_{index}")
        
        # Simular el AFD con la cadena de prueba
        result = minimized_dfa.simulate(test_string)
        
        return "si" if result else "no"
    
    except Exception as e:
        print(f"Error al procesar la expresión regular: {e}")
        return "Error"

def main():
    """Función principal"""
    file_path = "expresiones_regulares.txt"
    regex_data = read_regex_from_file(file_path)
    
    if not regex_data:
        print("No se encontraron expresiones regulares para procesar.")
        return
    
    print("Procesando expresiones regulares...\n")
    
    for i, (regex, test_string) in enumerate(regex_data, 1):
        result = process_regex(regex, test_string, i)
        print(f"Expresión {i}: {regex}")
        print(f"Cadena de prueba: {test_string}")
        print(f"Resultado: {result}\n")
    
    print("Las visualizaciones de los autómatas se han guardado en el directorio 'automata_images'")

if __name__ == "__main__":
    main()
