from reader import Reader

print("=== Starting simple test ===")

# Test 1: Basic test
print("\nTest 1: Creating Reader with '[a-c]'")
try:
    r = Reader('[a-c]')
    print("Reader created successfully!")
    print("Current character:", r.curr_char)
    
    # Try to process the range
    print("\nProcessing range:")
    tokens = list(r.CreateTokens())
    print("\nGenerated tokens:")
    for token in tokens:
        print(f"  {token}")
        
except Exception as e:
    print(f"Error: {e}")
    raise

print("\n=== Test completed ===")
