from reader import Reader
from parsing import Parser

def test_regex(regex):
    try:
        print(f"\nTesting regex: {regex}")
        reader = Reader(regex)
        tokens = list(reader.CreateTokens())
        print("Generated tokens:")
        for token in tokens:
            print(f"  {token}")
        
        parser = Parser(iter(tokens))
        tree = parser.Parse()
        print("Parse tree:", tree)
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

# Test cases
test_cases = [
    "[a-c]",    # Simple range
    "[0-9]",    # Digit range
    "[a-zA-Z]", # Letter range (both cases)
    "[a-c0-9]"  # Combined ranges
]

for test_case in test_cases:
    if not test_regex(test_case):
        print(f"Test failed for: {test_case}")
    else:
        print(f"Test passed for: {test_case}")
