import sys

class Token:
    def __init__(self, type, value=None):
        self.type = type
        self.value = value
    def __repr__(self):
        return f'Token({self.type}, {self.value})'

class Reader:
    def __init__(self, input_str):
        self.string = iter(input_str.replace(' ', ''))
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
    
    def CreateTokens(self):
        print("\n=== Starting CreateTokens ===")
        while self.curr_char is not None:
            print(f"Processing: {self.curr_char}")
            if self.curr_char == '[':
                yield from self._process_range()
            else:
                self.Next()
    
    def _process_range(self):
        print("Processing range...")
        self.Next()  # Skip '['
        range_str = ''
        
        while self.curr_char != ']' and self.curr_char is not None:
            range_str += self.curr_char
            self.Next()
            
        if self.curr_char == ']':
            self.Next()  # Skip ']'
            
        print(f"Range content: {range_str}")
        yield Token('RANGE', range_str)

# Test
try:
    print("=== Minimal Test ===\n")
    reader = Reader("[a-c]")
    print("\nReader created. Processing tokens...")
    tokens = list(reader.CreateTokens())
    print("\nGenerated tokens:", tokens)
    
except Exception as e:
    print(f"\nError: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc()
