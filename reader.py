from tokens import Token, TokenType
import string

# Include all possible characters that can be used in ranges
LETTERS = string.ascii_letters + string.digits + '.-_[]\\'


class Reader:
    def __init__(self, input_string: str):
        self.string = iter(input_string.replace(' ', ''))
        self.input = set()
        self.curr_char = None
        self.Next()

    def Next(self):
        try:
            self.curr_char = next(self.string)
            print(f"Next char: {self.curr_char}")
        except StopIteration:
            self.curr_char = None
            print("Reached end of input")

    def _get_char_range(self, start_char, end_char):
        """Generate all characters in the range from start_char to end_char"""
        if start_char > end_char:
            start_char, end_char = end_char, start_char
        return ''.join(chr(i) for i in range(ord(start_char), ord(end_char) + 1))

    def _process_range(self):
        """Process a character range like [a-f] or [0-9]"""
        print("\n=== Starting _process_range ===")
        try:
            print(f"Current char before skipping [: {self.curr_char}")
            self.Next()  # Skip '['
            print(f"Current char after skipping [: {self.curr_char}")
            range_str = ''
            
            while self.curr_char != ']' and self.curr_char is not None:
                print(f"Processing char: {self.curr_char}, current range_str: {range_str}")
                if self.curr_char == '\\':
                    print("Found escape character")
                    self.Next()
                    if self.curr_char is None:
                        raise Exception('Unexpected end of input after escape character')
                    range_str += self.curr_char
                elif self.curr_char == '-' and len(range_str) > 0:
                    print(f"Found range operator after: {range_str}")
                    start_char = range_str[-1]
                    self.Next()  # Skip '-'
                    if self.curr_char == ']':
                        print("Range operator at end of range, treating as literal")
                        range_str += '-'
                        break
                    if self.curr_char is None:
                        raise Exception('Unexpected end of input in character range')
                    end_char = self.curr_char
                    print(f"Expanding range: {start_char}-{end_char}")
                    range_chars = self._get_char_range(start_char, end_char)
                    print(f"Expanded to: {range_chars}")
                    range_str = range_str[:-1] + range_chars
                else:
                    range_str += self.curr_char
                self.Next()
                
            if self.curr_char != ']':
                raise Exception(f'Unclosed character range, expected ] but got {self.curr_char}')
                
            print(f"Final range string: {range_str}")
            self.Next()  # Skip ']'
            return range_str
            
        except Exception as e:
            print(f"Error processing range at position: {self.curr_char}")
            print(f"Current range_str: {range_str}")
            raise e
        finally:
            print("=== End of _process_range ===\n")

    def CreateTokens(self):
        print("\n=== Starting CreateTokens ===")
        print(f"Initial curr_char: {self.curr_char}")
        
        while self.curr_char is not None:
            print(f"\nCurrent character in CreateTokens: {self.curr_char}")
            
            if self.curr_char == '[':
                # Handle character range
                range_str = self._process_range()
                if len(range_str) == 0:
                    raise Exception('Empty character range')
                    
                # For each character in the range, add it to the input and create tokens
                first_char = True
                for c in range_str:
                    self.input.add(c)
                    if first_char:
                        yield Token(TokenType.LPAR, '(')
                        yield Token(TokenType.LETTER, c)
                        first_char = False
                    else:
                        yield Token(TokenType.OR, '|')
                        yield Token(TokenType.LETTER, c)
                yield Token(TokenType.RPAR, ')')
                
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
                        yield Token(TokenType.APPEND)
                        yield Token(TokenType.LETTER, self.curr_char)

                    self.Next()

                    if self.curr_char != None and self.curr_char == '(' and added_parenthesis:
                        yield Token(TokenType.APPEND)

                if self.curr_char != None and self.curr_char == '(' and not added_parenthesis:
                    yield Token(TokenType.RPAR, ')')
                    yield Token(TokenType.APPEND)

                elif not added_parenthesis:
                    yield Token(TokenType.RPAR, ')')

            elif self.curr_char == '|':
                self.Next()
                yield Token(TokenType.OR, '|')

            elif self.curr_char == '(':
                self.Next()
                yield Token(TokenType.LPAR)

            elif self.curr_char in (')*+?'):

                if self.curr_char == ')':
                    self.Next()
                    yield Token(TokenType.RPAR)

                elif self.curr_char == '*':
                    self.Next()
                    yield Token(TokenType.KLEENE)

                elif self.curr_char == '+':
                    self.Next()
                    yield Token(TokenType.PLUS)

                elif self.curr_char == '?':
                    self.Next()
                    yield Token(TokenType.QUESTION)

                # Finally, check if we need to add an append token
                if self.curr_char != None and \
                        (self.curr_char in LETTERS or self.curr_char == '('):
                    yield Token(TokenType.APPEND, '.')

            else:
                raise Exception(f'Invalid entry: {self.curr_char}')

    def GetSymbols(self):
        return self.input
