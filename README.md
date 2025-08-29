# Procesador de Expresiones Regulares

Este proyecto implementa un procesador completo de expresiones regulares que permite validar si una cadena pertenece al lenguaje definido por una expresión regular. El sistema construye automáticamente los Autómatas Finitos No Deterministas (AFN), los convierte a Autómatas Finitos Deterministas (AFD) y finalmente los minimiza para una evaluación eficiente.

## Características

- Soporte para operadores estándar de expresiones regulares:
  - Concatenación (implícita o con `.`)
  - Alternación (`|`)
  - Cerradura de Kleene (`*`)
  - Una o más ocurrencias (`+`)
  - Cero o una ocurrencia (`?`)
  - Agrupación con paréntesis
  - Soporte para epsilon (ε)

- Algoritmos implementados:
  - Construcción de Thompson para AFN
  - Algoritmo de subconjuntos para convertir AFN a AFD
  - Minimización de AFD
  - Simulación de AFD para validar cadenas

- Visualización de autómatas:
  - Generación de gráficos para AFN
  - Generación de gráficos para AFD
  - Generación de gráficos para AFD minimizado

## Estructura del Proyecto

```
.
├── automata/
│   ├── __init__.py
│   ├── nfa.py                  # Implementación de Autómatas Finitos No Deterministas
│   ├── subset_construction.py  # Algoritmo para convertir AFN a AFD
│   └── dfa_minimization.py     # Algoritmo para minimizar AFD
├── automata_images/            # Directorio donde se guardan las visualizaciones
├── main.py                     # Programa principal
├── expresiones_regulares.txt   # Archivo con expresiones regulares y cadenas de prueba
└── requirements.txt            # Dependencias del proyecto
```

## Formato del Archivo de Expresiones Regulares

El archivo `expresiones_regulares.txt` debe seguir el siguiente formato:

```
<expresión_regular_1>
<cadena_de_prueba_1>

<expresión_regular_2>
<cadena_de_prueba_2>

...
```

Donde cada expresión regular está en una línea y la cadena de prueba correspondiente está en la línea siguiente. Las parejas de expresión-cadena están separadas por una línea en blanco.

## Requisitos

- Python 3.6 o superior
- Dependencias (instalables con `pip install -r requirements.txt`):
  - matplotlib
  - numpy
  - networkx

## Uso

1. Asegúrate de tener todas las dependencias instaladas:

```bash
pip install -r requirements.txt
```

2. Edita el archivo `expresiones_regulares.txt` con tus expresiones regulares y cadenas de prueba.

3. Ejecuta el programa principal:

```bash
python main.py
```

4. Los resultados se mostrarán en la consola y las visualizaciones de los autómatas se guardarán en el directorio `automata_images/`.

## Ejemplos

Algunas expresiones regulares de ejemplo que puedes probar:

- `a*b` - Cero o más 'a' seguidas de una 'b'
- `(a|b)*abb` - Cualquier número de 'a' o 'b', seguido de 'abb'
- `a+b` - Una o más 'a' seguidas de una 'b'
- `a?b*c` - Cero o una 'a', seguida de cero o más 'b', seguida de una 'c'
- `(a|b)*a(a|b)(a|b)*` - Cualquier cadena que contenga una 'a' seguida de cualquier símbolo

## Implementación

El proyecto sigue un enfoque modular basado en los siguientes pasos:

1. **Preprocesamiento**: Elimina espacios y maneja caracteres especiales.
2. **Formateo**: Añade operadores de concatenación explícitos.
3. **Conversión Infix a Postfix**: Utiliza el algoritmo Shunting Yard.
4. **Construcción de Thompson**: Crea un AFN a partir de la expresión postfix.
5. **Algoritmo de Subconjuntos**: Convierte el AFN a un AFD.
6. **Minimización de AFD**: Reduce el número de estados del AFD.
7. **Simulación**: Evalúa si una cadena pertenece al lenguaje.
8. **Visualización**: Genera representaciones gráficas de los autómatas.