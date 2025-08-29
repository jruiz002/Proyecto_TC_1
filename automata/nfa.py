from .state import NFAState

class NFA:
    """Clase para representar un Autómata Finito No Determinista"""
    def __init__(self):
        self.states = {}
        self.start_state = None
        self.final_states = set()
        self.alphabet = set()
        self.state_counter = 0
    
    def create_state(self, is_final=False):
        """Crea un nuevo estado"""
        state = NFAState(self.state_counter, is_final)
        self.states[self.state_counter] = state
        if is_final:
            self.final_states.add(self.state_counter)
        self.state_counter += 1
        return state
    
    def set_start_state(self, state):
        """Establece el estado inicial"""
        self.start_state = state.state_id
    
    def add_transition(self, from_state, symbol, to_state):
        """Añade una transición al AFN"""
        if isinstance(from_state, int):
            from_state_id = from_state
            from_state = self.states[from_state_id]
        else:
            from_state_id = from_state.state_id
        
        if isinstance(to_state, int):
            to_state_id = to_state
            to_state = self.states[to_state_id]
        else:
            to_state_id = to_state.state_id
        
        from_state.add_transition(symbol, to_state_id)
        if symbol != 'ε':
            self.alphabet.add(symbol)
    
    def add_epsilon_transition(self, from_state, to_state):
        """Añade una transición epsilon al AFN"""
        self.add_transition(from_state, 'ε', to_state)
    
    def epsilon_closure(self, states):
        """Calcula la cerradura epsilon de un conjunto de estados"""
        closure = set(states)
        stack = list(states)
        
        while stack:
            current = stack.pop()
            if current in self.states:
                for next_state in self.states[current].transitions.get('ε', []):
                    if next_state not in closure:
                        closure.add(next_state)
                        stack.append(next_state)
        
        return closure
    
    def move(self, states, symbol):
        """Calcula el conjunto de estados alcanzables desde un conjunto de estados con un símbolo"""
        result = set()
        for state_id in states:
            if state_id in self.states:
                for next_state in self.states[state_id].transitions.get(symbol, []):
                    result.add(next_state)
        return result
    
    def simulate(self, input_string):
        """Simula el AFN con una cadena de entrada"""
        if self.start_state is None:
            return False
        
        current_states = self.epsilon_closure({self.start_state})
        
        for symbol in input_string:
            next_states = set()
            for state_id in current_states:
                if state_id in self.states:
                    for next_state in self.states[state_id].transitions.get(symbol, []):
                        next_states.add(next_state)
            
            current_states = self.epsilon_closure(next_states)
            
            if not current_states:
                return False
        
        # Verificar si algún estado actual es final
        return bool(current_states.intersection(self.final_states))