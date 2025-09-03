import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.abspath('.'))

from reader import Reader

def main():
    print("=== Direct Test of Range Processing ===\n")
    
    # Test input
    test_input = "[a-c]"
    print(f"Testing input: {test_input}")
    
    try:
        # Create a Reader instance
        reader = Reader(test_input)
        print("Reader created successfully")
        
        # Print the initial state
        print(f"Initial state - curr_char: {reader.curr_char}")
        
        # Process the tokens
        print("\nProcessing tokens...")
        tokens = list(reader.CreateTokens())
        
        # Print the results
        print("\nGenerated tokens:")
        for i, token in enumerate(tokens):
            print(f"  {i+1}. {token}")
            
        print("\nInput symbols:", reader.input)
        
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
