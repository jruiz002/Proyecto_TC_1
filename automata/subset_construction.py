from .dfa import DFA

def subset_construction(nfa):
    """Implementa el algoritmo de construcción de subconjuntos para convertir un AFN a un AFD"""
    if nfa.start_state is None:
        return None
    
    dfa = DFA()
    
    # Calcular la cerradura epsilon del estado inicial del AFN
    initial_closure = frozenset(nfa.epsilon_closure({nfa.start_state}))
    
    # Crear el estado inicial del AFD
    dfa_start = dfa.create_state(
        is_final=bool(initial_closure.intersection(nfa.final_states)),
        nfa_states=initial_closure
    )
    dfa.set_start_state(dfa_start)
    
    # Mapear el conjunto de estados del AFN al estado del AFD
    dfa.state_map[initial_closure] = dfa_start.state_id
    
    # Cola de conjuntos de estados por procesar
    unmarked_states = [initial_closure]
    
    while unmarked_states:
        current_nfa_states = unmarked_states.pop(0)
        current_dfa_state_id = dfa.state_map[current_nfa_states]
        
        # Para cada símbolo del alfabeto
        for symbol in nfa.alphabet:
            # Calcular el conjunto de estados alcanzables con el símbolo
            move_result = nfa.move(current_nfa_states, symbol)
            
            # Calcular la cerradura epsilon del resultado
            next_nfa_states = frozenset(nfa.epsilon_closure(move_result))
            
            # Si el conjunto no está vacío
            if next_nfa_states:
                # Verificar si ya existe un estado para este conjunto
                if next_nfa_states not in dfa.state_map:
                    # Crear un nuevo estado en el AFD
                    is_final = bool(next_nfa_states.intersection(nfa.final_states))
                    new_dfa_state = dfa.create_state(is_final=is_final, nfa_states=next_nfa_states)
                    
                    # Mapear el conjunto al nuevo estado
                    dfa.state_map[next_nfa_states] = new_dfa_state.state_id
                    
                    # Marcar el nuevo conjunto para procesamiento
                    unmarked_states.append(next_nfa_states)
                
                # Añadir la transición
                next_dfa_state_id = dfa.state_map[next_nfa_states]
                dfa.add_transition(
                    dfa.states[current_dfa_state_id],
                    symbol,
                    dfa.states[next_dfa_state_id]
                )
    
    # Eliminar estados inalcanzables
    unreachable = dfa.get_unreachable_states()
    if unreachable:
        dfa.remove_states(unreachable)
    
    return dfa