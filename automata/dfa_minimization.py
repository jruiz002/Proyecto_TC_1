from .dfa import DFA

def minimize_dfa(dfa):
    """Implementa el algoritmo de minimización de AFD mediante partición de estados"""
    if not dfa.states or dfa.start_state is None:
        return dfa
    
    # Eliminar estados inalcanzables
    unreachable = dfa.get_unreachable_states()
    if unreachable:
        dfa.remove_states(unreachable)
    
    # Inicializar particiones: estados finales y no finales
    final_states = frozenset(dfa.final_states)
    non_final_states = frozenset(set(dfa.states.keys()) - final_states)
    
    # Partición inicial
    partitions = []
    if final_states:
        partitions.append(final_states)
    if non_final_states:
        partitions.append(non_final_states)
    
    # Refinar particiones hasta que no haya cambios
    changed = True
    while changed:
        changed = False
        new_partitions = []
        
        for partition in partitions:
            # Intentar dividir la partición actual
            subpartitions = split_partition(dfa, partition, partitions)
            
            if len(subpartitions) > 1:
                changed = True
                new_partitions.extend(subpartitions)
            else:
                new_partitions.append(partition)
        
        partitions = new_partitions
    
    # Construir el AFD minimizado
    return build_minimized_dfa(dfa, partitions)

def split_partition(dfa, partition, partitions):
    """Divide una partición en subparticiones basadas en transiciones"""
    if len(partition) <= 1:
        return [partition]
    
    subpartitions = {}
    
    # Para cada estado en la partición
    for state_id in partition:
        # Calcular la firma de transición del estado
        signature = []
        for symbol in sorted(dfa.alphabet):
            target = dfa.get_transition(state_id, symbol)
            # Determinar a qué partición pertenece el estado destino
            target_partition = -1
            if target is not None:
                for i, p in enumerate(partitions):
                    if target in p:
                        target_partition = i
                        break
            signature.append((symbol, target_partition))
        
        # Usar la firma como clave para agrupar estados
        signature_tuple = tuple(signature)
        if signature_tuple not in subpartitions:
            subpartitions[signature_tuple] = set()
        subpartitions[signature_tuple].add(state_id)
    
    # Convertir los conjuntos a frozensets para hacerlos inmutables
    return [frozenset(states) for states in subpartitions.values()]

def build_minimized_dfa(original_dfa, partitions):
    """Construye un nuevo AFD basado en las particiones"""
    minimized_dfa = DFA()
    
    # Mapeo de estados originales a estados minimizados
    state_mapping = {}
    
    # Crear estados para cada partición
    for partition in partitions:
        # Verificar si la partición contiene algún estado final
        is_final = any(state_id in original_dfa.final_states for state_id in partition)
        
        # Crear un nuevo estado en el AFD minimizado
        new_state = minimized_dfa.create_state(is_final=is_final)
        
        # Mapear cada estado original en esta partición al nuevo estado
        for state_id in partition:
            state_mapping[state_id] = new_state.state_id
    
    # Establecer el estado inicial
    if original_dfa.start_state in state_mapping:
        minimized_dfa.set_start_state(minimized_dfa.states[state_mapping[original_dfa.start_state]])
    
    # Añadir transiciones
    for partition in partitions:
        # Tomar un estado representativo de la partición
        representative = next(iter(partition))
        from_state_id = state_mapping[representative]
        
        # Para cada símbolo del alfabeto
        for symbol in original_dfa.alphabet:
            target = original_dfa.get_transition(representative, symbol)
            if target is not None and target in state_mapping:
                to_state_id = state_mapping[target]
                minimized_dfa.add_transition(
                    minimized_dfa.states[from_state_id],
                    symbol,
                    minimized_dfa.states[to_state_id]
                )
    
    return minimized_dfa