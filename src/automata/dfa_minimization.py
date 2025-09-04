from collections import deque, defaultdict

from typing import Dict, Set, Iterable, Tuple, List
from pythomata import SimpleDFA
from ..utils.helpers import WriteToFile


def alcanzables(dfa):
    """
    Devuelve el conjunto de estados alcanzables desde el estado inicial.
    No modifica el DFA original.
    """
    visitados = set()
    orden = []

    q0 = dfa.initial_state
    if q0 not in dfa.trans_func:
        return orden
    
    cola = [q0]
    visitados.add(q0)

    alfabeto = [s for s in dfa.symbols if s != 'ε']

    while cola:
        u = cola.pop(0)
        orden.append(u)
        #por cada simbolo, ver a donde se puede ir
        for a in alfabeto:
            if u in dfa.trans_func and a in dfa.trans_func[u]:
                v = dfa.trans_func[u][a]
                if (v in dfa.trans_func) and (v not in visitados):
                    visitados.add(v)
                    cola.append(v)

    return orden

def particion_inicial(dfa, R):
    """
    Devuelve la partición inicial de estados del DFA.
    """
    finales = set(dfa.accepting_states)
    R_set = set(R)

    bloque_finales = [q for q in R if q in finales]
    bloque_no_finales = [q for q in R if q not in finales]

    P0 = []
    if bloque_finales:
        P0.append(bloque_finales)
    if bloque_no_finales:
        P0.append(bloque_no_finales)
    return P0

# Refinamiento por particiones 

def indice_bloque(P, q):
    """Devuelve el índice del bloque de P que contiene q; -1 si no está."""
    for i in range(len(P)):
        if q in P[i]:
            return i
    return -1

def misma_firma(dfa, q, r, P, alfabeto):
    """
    q y r quedan en el mismo sub-bloque si, para cada símbolo a,
    δ(q,a) y δ(r,a) caen en el MISMO bloque de P (o ambos no tienen transición).
    """
    for a in alfabeto:
        # siguiente de q con 'a'
        if (q in dfa.trans_func) and (a in dfa.trans_func[q]):
            qn = dfa.trans_func[q][a]
        else:
            qn = None
        # siguiente de r con 'a'
        if (r in dfa.trans_func) and (a in dfa.trans_func[r]):
            rn = dfa.trans_func[r][a]
        else:
            rn = None

        iq = indice_bloque(P, qn) if qn is not None else -1
        ir = indice_bloque(P, rn) if rn is not None else -1
        if iq != ir:
            return False
    return True

def partir_bloque(dfa, P, B, alfabeto):
    """
    Parte B en sub-bloques usando comparación contra un representante.
    sub = [[estados_con_misma_firma], ...]
    """
    sub = []
    reps = []  # representantes
    for q in B:
        colocado = False
        for i in range(len(reps)):
            rep = reps[i]
            if misma_firma(dfa, q, rep, P, alfabeto):
                sub[i].append(q)
                colocado = True
                break
        if not colocado:
            reps.append(q)
            sub.append([q])
    return sub

def refinar_una_vez(dfa, P):
    """Aplica 'partir_bloque' a cada bloque. Devuelve (nueva_partición, hubo_cambio)."""
    alfabeto = [s for s in dfa.symbols if s != 'ε']
    nueva = []
    hubo_cambio = False

    for B in P:
        sub = partir_bloque(dfa, P, B, alfabeto)
        if len(sub) > 1:
            hubo_cambio = True
        # añadimos los sub-bloques 
        for s in sub:
            s.sort()
            nueva.append(s)

    # ordenar bloques: el que contiene al inicial primero, luego por nombre
    nueva.sort(key=lambda b: (0 if dfa.initial_state in b else 1, b[0] if b else ""))
    return nueva, hubo_cambio

def refinar_hasta_estabilizar(dfa, P0):
    """Repite refinamiento hasta que no haya cambios y devuelve la partición final."""
    # normalización inicial 
    P = [sorted(b) for b in P0]
    P.sort(key=lambda b: (0 if dfa.initial_state in b else 1, b[0] if b else ""))

    while True:
        P1, cambio = refinar_una_vez(dfa, P)
        if not cambio:
            return P1
        P = P1

# Construcción del DFA minimizado

LETRAS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

def nombre(i):
    """Devuelve el nombre de un estado dado su índice."""
    if i < len(LETRAS):
        return LETRAS[i]
    else:
        return 'A' + str(i - len(LETRAS))
    

def ordenar_bloques(P,inicial):
    """Ordena los bloques de P para que el que contiene el estado inicial quede primero."""
    P2 = P[:]
    P2.sort(key=lambda b: (0 if inicial in b else 1, b[0] if b else ""))
    return P2


def DFA_minimizado(dfa, P_final):
    """
    Devuelve:
      - nuevos_estados es una lista de nombres (A, B, C, ...)
      - nuevo_alfabeto es un set (símbolos sin 'ε')
      - nuevos_finales es una lista con los estados finales nuevos
      - nueva_delta tiene la misma forma que dfa.trans_func, pero sobre los estados nuevos
    """
    alfabeto = [s for s in dfa.symbols if s != 'ε']

    # 1) Ordenar bloques y asignar nombres A, B, C... 
    bloques = ordenar_bloques(P_final, dfa.initial_state)
    nombres = [nombre(i) for i in range(len(bloques))]

    # 2) Nuevo inicial y nuevos finales
    nuevo_inicial = nombres[0]  # porque ese bloque contiene al inicial original
    nuevos_finales = []
    for i, B in enumerate(bloques):
        if any(q in dfa.accepting_states for q in B):
            nuevos_finales.append(nombres[i])

    # 3) Transiciones: usar un representante de cada bloque
    nueva_delta = {}
    for i, B in enumerate(bloques):
        src = nombres[i]
        nueva_delta[src] = {}
        if not B: 
            continue
        rep = B[0]  # representante

        for a in alfabeto:
            if (rep in dfa.trans_func) and (a in dfa.trans_func[rep]):
                v = dfa.trans_func[rep][a]           # estado viejo destino
                j = indice_bloque(bloques, v)        # a q bloque cae
                if j != -1:
                    nueva_delta[src][a] = nombres[j]
            # si no hay transición definida, no se agrega

    nuevos_estados = nombres[:]  
    nuevo_alfabeto = set(alfabeto)

    return nuevos_estados, nuevo_alfabeto, nuevo_inicial, nuevos_finales, nueva_delta


def eval_minimized_dfa(nuevos_estados, nuevo_alfabeto, nuevo_inicial, nuevos_finales, nueva_delta, w: str):
    """
    Evalúa la palabra w en el DFA minimizado definido por la tupla
    """
    estado = nuevo_inicial
    if not nuevos_estados or not nuevo_alfabeto:
        return 'No'

    for c in w:
        if c not in nuevo_alfabeto:
            return 'No'
        trans = nueva_delta.get(estado, {})
        if c not in trans:
            return 'No'
        estado = trans[c]

    return 'Si' if estado in set(nuevos_finales) else 'No'


def graph_minimized_dfa(nuevos_estados, nuevo_alfabeto, nuevo_inicial, nuevos_finales, nueva_delta, out_basename: str = 'MinDFA'):
    """
    Genera el diagrama del DFA minimizado y lo guarda en ./output/<out_basename>.gv (+ .pdf).
    """
    states = set(nuevos_estados)
    alphabet = set(nuevo_alfabeto)
    initial = nuevo_inicial
    finals = set(nuevos_finales)

    dfa = SimpleDFA(states, alphabet, initial, finals, nueva_delta)
    graph = dfa.trim().to_graphviz()
    graph.attr(rankdir='LR')

    source = graph.source
    filepath = f'./output/{out_basename}.gv'
    WriteToFile(filepath, source)
    graph.render(filepath, format='pdf', view=True)
