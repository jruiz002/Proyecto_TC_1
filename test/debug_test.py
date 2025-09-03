import sys

def main():
    print("=== Debug Test ===")
    print("Python version:", sys.version)
    print("Current directory:", os.getcwd())
    print("Files in directory:", os.listdir('.'))
    
    # Test basic file operations
    try:
        with open('test.txt', 'w') as f:
            f.write("Test file content")
        print("Successfully wrote to test file")
    except Exception as e:
        print(f"Error writing to file: {e}")

if __name__ == "__main__":
    import os
    main()
