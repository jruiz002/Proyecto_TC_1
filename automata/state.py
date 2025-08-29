from collections import defaultdict

class State:
    """Clase base para representar un estado en un autómata"""
    def __init__(self, state_id, is_final=False):
        self.state_id = state_id
        self.is_final = is_final
        
    def __str__(self):
        return f"State {self.state_id}{'(F)' if self.is_final else ''}"
    
    def __repr__(self):
        return self.__str__()

class NFAState(State):
    """Clase para representar un estado del AFN"""
    def __init__(self, state_id, is_final=False):
        super().__init__(state_id, is_final)
        self.transitions = defaultdict(list)  # símbolo -> lista de estados
    
    def add_transition(self, symbol, target_state):
        """Añade una transición desde este estado"""
        self.transitions[symbol].append(target_state)

class DFAState(State):
    """Clase para representar un estado del AFD"""
    def __init__(self, state_id, is_final=False, nfa_states=None):
        super().__init__(state_id, is_final)
        self.transitions = {}  # símbolo -> estado (único)
        self.nfa_states = nfa_states or set()  # Conjunto de estados del AFN que representa
    
    def add_transition(self, symbol, target_state):
        """Añade una transición desde este estado"""
        self.transitions[symbol] = target_state
    
    def get_transition(self, symbol):
        """Obtiene el estado destino para un símbolo dado"""
        return self.transitions.get(symbol)