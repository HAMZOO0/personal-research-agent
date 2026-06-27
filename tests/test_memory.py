from src.memory import MEMORY

def test_memory_initialization():
    if MEMORY is not None:
        print("SUCCESS: Memory initialized successfully!")
        return True
    else:
        print("FAILED: Memory is None")
        return False

if __name__ == "__main__":
    test_memory_initialization()
