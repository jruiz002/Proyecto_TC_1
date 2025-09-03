# Proyecto de Teoría de la Computación

Este proyecto implementa autómatas finitos (NFA y DFA) a partir de expresiones regulares, permitiendo la conversión entre ellos y la validación de cadenas.

## Estructura del Proyecto

```
Proyecto_TC_1/
├── src/                    # Código fuente del proyecto
│   ├── automata/          # Implementación de autómatas
│   │   ├── __init__.py
│   │   ├── dfa.py         # Implementación de DFA
│   │   └── nfa.py         # Implementación de NFA
│   │
│   ├── parsing/           # Análisis de expresiones regulares
│   │   ├── __init__.py
│   │   ├── nodes.py       # Nodos del árbol de sintaxis
│   │   ├── parser.py      # Parser de expresiones regulares
│   │   └── tokens.py      # Definición de tokens
│   │
│   ├── io/                # Manejo de entrada/salida
│   │   ├── __init__.py
│   │   ├── input_handler.py # Manejo de archivos de entrada
│   │   └── reader.py      # Lectura de tokens
│   │
│   └── utils/             # Utilidades
│       ├── __init__.py
│       └── helpers.py     # Funciones auxiliares
│
├── input/                 # Archivos de entrada
│   ├── regex.txt          # Expresión regular de entrada
│   └── w_string.txt       # Cadena a evaluar
│
├── output/                # Archivos generados (gráficos, etc.)
├── main.py               # Punto de entrada principal
├── requirements.txt      # Dependencias
└── setup.py             # Configuración del paquete
```

## Requisitos

- Python 3.6 o superior
- Graphviz (para visualización de autómatas)
- Dependencias de Python (instalar con `pip install -r requirements.txt`)

## Uso

1. Coloca tu expresión regular en `input/regex.txt`
2. Coloca la cadena a evaluar en `input/w_string.txt`
3. Ejecuta el programa principal:
   ```bash
   python main.py
   ```

## Instalación de dependencias

```bash
pip install -r requirements.txt
```

## Notas

- Los diagramas de los autómatas se generan en la carpeta `output/`
- El programa muestra el tiempo de ejecución para la evaluación de la cadena tanto en NFA como en DFA
