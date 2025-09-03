from reader import Reader

def test_regex(regex):
    print(f"\nTesting regex: {regex}")
    try:
        reader = Reader(regex)
        tokens = list(reader.CreateTokens())
        print("Generated tokens:")
        for token in tokens:
            print(f"  {token}")
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
