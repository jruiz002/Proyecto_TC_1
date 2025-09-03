from tokens import Token, TokenType

LETTERS = 'abcdefghijklmnopqrstuvwxyz01234567890.ε'


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


class ThompsonReader(BaseReader):
    def CreateTokens(self):
        while self.curr_char != None:

            if self.curr_char in LETTERS:
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
                        (self.curr_char in LETTERS or self.curr_char == '('):
                    yield Token(TokenType.APPEND, '.')

            else:
                raise Exception(f'Entrada inválida: {self.curr_char}')


class DirectReader(BaseReader):
    def __init__(self, string: str):
        super().__init__(string)
        self.rparPending = False

    def CreateTokens(self):
        while self.curr_char != None:

            if self.curr_char in LETTERS:
                self.input.add(self.curr_char)
                yield Token(TokenType.LETTER, self.curr_char)

                self.Next()

                # Finally, check if we need to add an append token
                if self.curr_char != None and \
                        (self.curr_char in LETTERS or self.curr_char == '('):
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
                                    (self.curr_char in LETTERS or self.curr_char == '('):
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
                        (self.curr_char in LETTERS or self.curr_char == '('):
                    yield Token(TokenType.APPEND, '.')

            else:
                raise Exception(f'Entrada inválida: {self.curr_char}')

        yield Token(TokenType.APPEND, '.')
        yield Token(TokenType.LETTER, '#')
