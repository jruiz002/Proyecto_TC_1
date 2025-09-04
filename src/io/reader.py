from ..parsing.tokens import Token, TokenType
import string

# Accept letters, digits, and most punctuation except regex meta chars. Keep ε explicit.
_META = set('()[]|*+?\\')
_PUNCT = ''.join(ch for ch in string.punctuation if ch not in _META)
LETTERS = string.ascii_letters + string.digits + _PUNCT + 'ε'


class BaseReader:
    def __init__(self, string: str):
        self.string = iter(string.replace(' ', ''))
        self.input = set()
        self.Next()

    def Next(self):
        try:
            self.curr_char = next(self.string)
        except StopIteration:
            self.curr_char = None

    def GetSymbols(self):
        return self.input

    def _get_char_range(self, start_char, end_char):
        """Generate all characters in the range from start_char to end_char"""
        if ord(start_char) > ord(end_char):
            start_char, end_char = end_char, start_char
        return ''.join(chr(i) for i in range(ord(start_char), ord(end_char) + 1))

    def _process_range(self):
        """Process a character class like [a-fA-F0-9], honoring escapes and ranges."""
        self.Next()  # Skip '['
        items = []
        last_literal = None

        while self.curr_char is not None and self.curr_char != ']':
            if self.curr_char == '\\':
                # escape inside class: '\n' -> two literals '\' and 'n'; otherwise literal of next
                self.Next()
                if self.curr_char is None:
                    raise Exception('Fin de entrada inesperado después del carácter de escape')
                if self.curr_char == 'n':
                    items.extend(['\\', 'n'])
                    last_literal = 'n'  # last seen literal is 'n'
                    self.Next()
                else:
                    items.append(self.curr_char)
                    last_literal = self.curr_char
                    self.Next()
                continue

            if self.curr_char == '-' and last_literal is not None:
                # Range: previous literal to next literal
                self.Next()
                if self.curr_char is None or self.curr_char == ']':
                    # '-' as literal
                    items.append('-')
                    last_literal = '-'
                    continue
                if self.curr_char == '\\':
                    self.Next()
                    if self.curr_char is None:
                        raise Exception('Fin de entrada inesperado después del carácter de escape')
                    end_lit = self.curr_char
                    self.Next()
                else:
                    end_lit = self.curr_char
                    self.Next()
                # expand range
                for c in self._get_char_range(last_literal, end_lit):
                    items.append(c)
                last_literal = None
                continue

            # regular literal
            items.append(self.curr_char)
            last_literal = self.curr_char
            self.Next()

        if self.curr_char != ']':
            raise Exception(f'Rango de caracteres sin cerrar, se esperaba ] pero se obtuvo {self.curr_char}')

        self.Next()  # Skip ']'
        if not items:
            raise Exception('Rango de caracteres vacío')
        return ''.join(items)


class ThompsonReader(BaseReader):
    def CreateTokens(self):
        while self.curr_char != None:

            # Skip whitespace/newlines between tokens
            if self.curr_char in ' \t\r\n':
                self.Next()
                continue

            # Backslash escape outside classes: hides '\' and literalizes next char,
            # except '\n' which yields two literals: '\\' and 'n'.
            if self.curr_char == '\\':
                # consume backslash
                self.Next()
                if self.curr_char is None:
                    raise Exception('Barra invertida sin carácter a escapar')

                if self.curr_char == 'n':
                    # emit two literals: '\\' and 'n'
                    yield Token(TokenType.LPAR, '(')
                    self.input.add('\\')
                    yield Token(TokenType.LETTER, '\\')
                    yield Token(TokenType.APPEND, '.')
                    self.input.add('n')
                    yield Token(TokenType.LETTER, 'n')
                    yield Token(TokenType.RPAR, ')')
                    self.Next()
                elif self.curr_char == '\\':
                    # '\\' -> single backslash literal
                    yield Token(TokenType.LPAR, '(')
                    self.input.add('\\')
                    yield Token(TokenType.LETTER, '\\')
                    yield Token(TokenType.RPAR, ')')
                    self.Next()
                else:
                    # '\x' -> literal 'x'
                    ch = self.curr_char
                    yield Token(TokenType.LPAR, '(')
                    self.input.add(ch)
                    yield Token(TokenType.LETTER, ch)
                    yield Token(TokenType.RPAR, ')')
                    self.Next()

                # Add concatenation if next token starts an atom
                if self.curr_char != None and (self.curr_char in LETTERS or self.curr_char in '([' or self.curr_char == '\\'):
                    yield Token(TokenType.APPEND, '.')
                continue

            if self.curr_char == '[':
                # Procesar rango mejorado
                range_str = self._process_range()
                
                # Generar OR para cada carácter en el rango
                yield Token(TokenType.LPAR, '(')
                
                first_char = True
                for c in range_str:
                    self.input.add(c)
                    if not first_char:
                        yield Token(TokenType.OR, '|')
                    yield Token(TokenType.LETTER, c)
                    first_char = False
                
                yield Token(TokenType.RPAR, ')')
                
                # Verificar si necesitamos agregar un token de concatenación
                if self.curr_char != None and (self.curr_char in LETTERS or self.curr_char == '(' or self.curr_char == '[' or self.curr_char == '\\'):
                    yield Token(TokenType.APPEND, '.')
            
            elif self.curr_char in LETTERS:
                self.input.add(self.curr_char)
                yield Token(TokenType.LPAR, '(')
                yield Token(TokenType.LETTER, self.curr_char)

                self.Next()
                added_parenthesis = False

                while self.curr_char != None and (self.curr_char in LETTERS or self.curr_char in '*+?'):

                    if self.curr_char == '*':
                        yield Token(TokenType.KLEENE, '*')
                        yield Token(TokenType.RPAR, ')')
                        added_parenthesis = True

                    elif self.curr_char == '+':
                        yield Token(TokenType.PLUS, '+')
                        yield Token(TokenType.RPAR, ')')
                        added_parenthesis = True

                    elif self.curr_char == '?':
                        yield Token(TokenType.QUESTION, '?')
                        yield Token(TokenType.RPAR, ')')
                        added_parenthesis = True

                    elif self.curr_char in LETTERS:
                        self.input.add(self.curr_char)
                        yield Token(TokenType.APPEND, '.')
                        yield Token(TokenType.LETTER, self.curr_char)

                    self.Next()

                    # Si terminamos con cuantificador y el siguiente token comienza un átomo, agregar concatenación
                    if self.curr_char != None and added_parenthesis and (self.curr_char == '(' or self.curr_char == '[' or self.curr_char == '\\'):
                        yield Token(TokenType.APPEND, '.')

                if self.curr_char != None and self.curr_char == '(' and not added_parenthesis:
                    yield Token(TokenType.RPAR, ')')
                    yield Token(TokenType.APPEND, '.')

                elif not added_parenthesis:
                    yield Token(TokenType.RPAR, ')')
                    # If next starts an atom (escape or class), add concatenation
                    if self.curr_char != None and (self.curr_char == '[' or self.curr_char == '\\'):
                        yield Token(TokenType.APPEND, '.')

            elif self.curr_char == '|':
                self.Next()
                yield Token(TokenType.OR, '|')

            elif self.curr_char == '(':
                self.Next()
                yield Token(TokenType.LPAR, '(')

            elif self.curr_char in (')*+?'):

                if self.curr_char == ')':
                    self.Next()
                    yield Token(TokenType.RPAR, ')')

                elif self.curr_char == '*':
                    self.Next()
                    yield Token(TokenType.KLEENE, '*')

                elif self.curr_char == '+':
                    self.Next()
                    yield Token(TokenType.PLUS, '+')

                elif self.curr_char == '?':
                    self.Next()
                    yield Token(TokenType.QUESTION, '?')

                # Finally, check if we need to add an append token
                if self.curr_char != None and \
                        (self.curr_char in LETTERS or self.curr_char == '(' or self.curr_char == '[' or self.curr_char == '\\'):
                    yield Token(TokenType.APPEND, '.')

            else:
                raise Exception(f'Entrada inválida: {self.curr_char}')


class DirectReader(BaseReader):
    def __init__(self, string: str):
        super().__init__(string)
        self.rparPending = False

    def CreateTokens(self):
        while self.curr_char != None:

            # Skip whitespace/newlines between tokens
            if self.curr_char in ' \t\r\n':
                self.Next()
                continue

            # Backslash escape outside classes: hides '\' and literalizes next char,
            # except '\n' which yields two literals: '\\' and 'n'.
            if self.curr_char == '\\':
                # consume backslash
                self.Next()
                if self.curr_char is None:
                    raise Exception('Barra invertida sin carácter a escapar')

                out_chars = []
                if self.curr_char == 'n':
                    out_chars = ['\\', 'n']
                    self.Next()
                elif self.curr_char == '\\':
                    out_chars = ['\\']
                    self.Next()
                else:
                    out_chars = [self.curr_char]
                    self.Next()

                first = True
                for ch in out_chars:
                    if not first:
                        yield Token(TokenType.APPEND, '.')
                    self.input.add(ch)
                    yield Token(TokenType.LETTER, ch)
                    first = False

                if self.curr_char != None and (self.curr_char in LETTERS or self.curr_char in '([' or self.curr_char == '\\'):
                    yield Token(TokenType.APPEND, '.')
                continue

            if self.curr_char == '[':
                # Procesar rango mejorado
                range_str = self._process_range()
                
                # Generar OR para cada carácter en el rango
                yield Token(TokenType.LPAR, '(')
                
                first_char = True
                for c in range_str:
                    self.input.add(c)
                    if not first_char:
                        yield Token(TokenType.OR, '|')
                    yield Token(TokenType.LETTER, c)
                    first_char = False
                
                yield Token(TokenType.RPAR, ')')
                
                # Verificar si necesitamos agregar un token de concatenación
                if self.curr_char != None and (self.curr_char in LETTERS or self.curr_char == '(' or self.curr_char == '[' or self.curr_char == '\\'):
                    yield Token(TokenType.APPEND, '.')
            
            elif self.curr_char in LETTERS:
                self.input.add(self.curr_char)
                yield Token(TokenType.LETTER, self.curr_char)

                self.Next()

                # Finally, check if we need to add an append token
                if self.curr_char != None and (self.curr_char in LETTERS or self.curr_char == '(' or self.curr_char == '[' or self.curr_char == '\\'):
                    yield Token(TokenType.APPEND, '.')

            elif self.curr_char == '|':
                yield Token(TokenType.OR, '|')

                self.Next()

                if self.curr_char != None and self.curr_char not in '()':
                    yield Token(TokenType.LPAR, '(')

                    while self.curr_char != None and self.curr_char not in ')*+?':
                        if self.curr_char in LETTERS:
                            self.input.add(self.curr_char)
                            yield Token(TokenType.LETTER, self.curr_char)

                            self.Next()
                            if self.curr_char != None and \
                                    (self.curr_char in LETTERS or self.curr_char == '(' or self.curr_char == '['):
                                yield Token(TokenType.APPEND, '.')

                    if self.curr_char != None and self.curr_char in '*+?':
                        self.rparPending = True
                    elif self.curr_char != None and self.curr_char == ')':
                        yield Token(TokenType.RPAR, ')')
                    else:
                        yield Token(TokenType.RPAR, ')')

            elif self.curr_char == '(':
                self.Next()
                yield Token(TokenType.LPAR, '(')

            elif self.curr_char in (')*+?'):

                if self.curr_char == ')':
                    self.Next()
                    yield Token(TokenType.RPAR, ')')

                elif self.curr_char == '*':
                    self.Next()
                    yield Token(TokenType.KLEENE, '*')

                elif self.curr_char == '+':
                    self.Next()
                    yield Token(TokenType.PLUS, '+')

                elif self.curr_char == '?':
                    self.Next()
                    yield Token(TokenType.QUESTION, '?')

                if self.rparPending:
                    yield Token(TokenType.RPAR, ')')
                    self.rparPending = False

                # Finally, check if we need to add an append token
                if self.curr_char != None and \
                        (self.curr_char in LETTERS or self.curr_char == '(' or self.curr_char == '['):
                    yield Token(TokenType.APPEND, '.')

            else:
                raise Exception(f'Entrada inválida: {self.curr_char}')

        yield Token(TokenType.APPEND, '.')
        yield Token(TokenType.LETTER, '#')
