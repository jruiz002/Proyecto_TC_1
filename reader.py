from tokens import Token, TokenType
import string

LETTERS = string.ascii_letters + string.digits + '.-_ε'


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
        """Process a character range like [a-fA-F0-9] or [abc\-] with escapes"""
        self.Next()  # Skip '['
        range_str = ''
        
        while self.curr_char != ']' and self.curr_char is not None:
            if self.curr_char == '\\':
                self.Next()
                if self.curr_char is None:
                    raise Exception('Fin de entrada inesperado después del carácter de escape')
                range_str += self.curr_char
            elif self.curr_char == '-' and len(range_str) > 0:
                start_char = range_str[-1]
                self.Next()  # Skip '-'
                if self.curr_char == ']':
                    range_str += '-'
                    break
                if self.curr_char is None:
                    raise Exception('Fin de entrada inesperado en rango de caracteres')
                end_char = self.curr_char
                range_chars = self._get_char_range(start_char, end_char)
                range_str = range_str[:-1] + range_chars
            else:
                range_str += self.curr_char
            self.Next()
            
        if self.curr_char != ']':
            raise Exception(f'Rango de caracteres sin cerrar, se esperaba ] pero se obtuvo {self.curr_char}')
        
        self.Next()  # Skip ']'
        if len(range_str) == 0:
            raise Exception('Rango de caracteres vacío')
        return range_str


class ThompsonReader(BaseReader):
    def CreateTokens(self):
        while self.curr_char != None:

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
                if self.curr_char != None and (self.curr_char in LETTERS or self.curr_char == '(' or self.curr_char == '['):
                    yield Token(TokenType.APPEND, '.')
            
            elif self.curr_char in LETTERS:
                self.input.add(self.curr_char)
                yield Token(TokenType.LPAR, '(')
                yield Token(TokenType.LETTER, self.curr_char)

                self.Next()
                added_parenthesis = False

                while self.curr_char != None and \
                        (self.curr_char in LETTERS or self.curr_char in '*+?'):

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

                    if self.curr_char != None and self.curr_char == '(' and added_parenthesis:
                        yield Token(TokenType.APPEND, '.')

                if self.curr_char != None and self.curr_char == '(' and not added_parenthesis:
                    yield Token(TokenType.RPAR, ')')
                    yield Token(TokenType.APPEND, '.')

                elif not added_parenthesis:
                    yield Token(TokenType.RPAR, ')')

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
                        (self.curr_char in LETTERS or self.curr_char == '(' or self.curr_char == '['):
                    yield Token(TokenType.APPEND, '.')

            else:
                raise Exception(f'Entrada inválida: {self.curr_char}')


class DirectReader(BaseReader):
    def __init__(self, string: str):
        super().__init__(string)
        self.rparPending = False

    def CreateTokens(self):
        while self.curr_char != None:

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
                if self.curr_char != None and (self.curr_char in LETTERS or self.curr_char == '(' or self.curr_char == '['):
                    yield Token(TokenType.APPEND, '.')
            
            elif self.curr_char in LETTERS:
                self.input.add(self.curr_char)
                yield Token(TokenType.LETTER, self.curr_char)

                self.Next()

                # Finally, check if we need to add an append token
                if self.curr_char != None and \
                        (self.curr_char in LETTERS or self.curr_char == '(' or self.curr_char == '['):
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
