from reader import ThompsonReader
from parsing import Parser
from nfa import NFA
from dfa import DFA
import os
from time import time

os.makedirs('output', exist_ok=True)
from input_handler import InputHandler

program_title = '''

#        AUTÓMATAS FINITOS        #

Genera NFA y DFA basados en una expresión regular y compara tiempos simulando una cadena!
'''
direct_dfa_msg = '''

    # CONSTRUCCIÓN DFA DIRECTO # '''
generate_diagram_msg = '''
Generando diagramas...'''
type_regex_msg = '''
Expresión regular leída de regex.txt: '''
type_string_msg = '''
Cadena leída de w_string.txt: '''
accepted = 'Sí'
not_accepted = 'No'
time_msg = '\nTiempo para evaluar: {:.5E} segundos'
belongs_msg_nfa = '¿La cadena pertenece a la expresión regular (NFA)?'
belongs_msg_dfa = '¿La cadena pertenece a la expresión regular (DFA)?'
expression_accepted = '\n\tExpresión aceptada!'
parsed_tree = '\tÁrbol parseado:'
err_invalid = '\n\tERR: Expresión inválida (falta paréntesis)'
err_general = '\n\tERR: {}'

if __name__ == "__main__":
    print(program_title)

    input_handler = InputHandler()
    regex = input_handler.regex
    regex_input = input_handler.input_string

    print(type_regex_msg + regex)
    print(type_string_msg + regex_input)

    try:
        thompson_reader = ThompsonReader(regex)
        tokens = thompson_reader.CreateTokens()
        parser = Parser(tokens)
        tree = parser.Parse()

        print(expression_accepted)
        print(parsed_tree, tree)

    except AttributeError as e:
        print(err_invalid)
        exit(1)

    except Exception as e:
        print(err_general.format(e))
        exit(1)

    # Thompson
    nfa = NFA(tree, thompson_reader.GetSymbols(), regex_input)
    start_time = time()
    nfa_regex = nfa.EvalRegex()
    stop_time = time()
    print(time_msg.format(stop_time - start_time))
    print(belongs_msg_nfa)
    print('>', accepted if nfa_regex == 'Si' else not_accepted)

    dfa = DFA(nfa.trans_func, nfa.symbols, nfa.curr_state, nfa.accepting_states, regex_input)
    dfa.TransformNFAToDFA()
    start_time = time()
    dfa_regex = dfa.EvalRegex()
    stop_time = time()
    print(time_msg.format(stop_time - start_time))
    print(belongs_msg_dfa)
    print('>', accepted if dfa_regex == 'Si' else not_accepted)

    print(generate_diagram_msg)
    nfa.WriteNFADiagram()
    dfa.GraphDFA()
