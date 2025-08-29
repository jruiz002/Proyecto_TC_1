from .state import DFAState

class DFA:
    """Clase para representar un Autómata Finito Determinista"""
    def __init__(self):
        self.states = {}
        self.start_state = None
        self.final_states = set()
        self.alphabet = set()
        self.state_counter = 0
        self.state_map = {}  # Mapeo de conjuntos de estados del AFN a estados del AFD
    
    def create_state(self, is_final=False, nfa_states=None):
        """Crea un nuevo estado"""
        state = DFAState(self.state_counter, is_final, nfa_states)
        self.states[self.state_counter] = state
        if is_final:
            self.final_states.add(self.state_counter)
        self.state_counter += 1
        return state
    
    def set_start_state(self, state):
        """Establece el estado inicial"""
        self.start_state = state.state_id
    
    def add_transition(self, from_state, symbol, to_state):
        """Añade una transición al AFD"""
        from_state.add_transition(symbol, to_state.state_id)
        self.alphabet.add(symbol)
    
    def get_transition(self, state_id, symbol):
        """Obtiene el estado destino para un estado y símbolo dados"""
        if state_id in self.states:
            return self.states[state_id].get_transition(symbol)
        return None
    
    def simulate(self, input_string):
        """Simula el AFD con una cadena de entrada"""
        if self.start_state is None:
            return False
        
        current_state = self.start_state
        
        for symbol in input_string:
            if current_state is None or current_state not in self.states:
                return False
            
            current_state = self.states[current_state].get_transition(symbol)
            
            if current_state is None:
                return False
        
        # Verificar si el estado actual es final
        return current_state in self.final_states
    
    def get_unreachable_states(self):
        """Obtiene los estados inalcanzables desde el estado inicial"""
        if self.start_state is None:
            return set(self.states.keys())
        
        # BFS para encontrar estados alcanzables
        reachable = set()
        queue = [self.start_state]
        
        while queue:
            current = queue.pop(0)
            if current not in reachable:
                reachable.add(current)
                
                # Añadir todos los estados alcanzables desde el estado actual
                if current in self.states:
                    for symbol, next_state in self.states[current].transitions.items():
                        if next_state not in reachable:
                            queue.append(next_state)
        
        # Retornar estados no alcanzables
        return set(self.states.keys()) - reachable
    
    def remove_states(self, states_to_remove):
        """Elimina un conjunto de estados del AFD"""
        for state_id in states_to_remove:
            if state_id in self.states:
                if state_id in self.final_states:
                    self.final_states.remove(state_id)
                del self.states[state_id]
        
        # Actualizar transiciones para eliminar referencias a estados eliminados
        for state in self.states.values():
            for symbol in list(state.transitions.keys()):
                if state.transitions[symbol] in states_to_remove:
                    del state.transitions[symbol]