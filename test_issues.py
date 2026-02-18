
def find_col(columns, keywords):
    for col in columns:
        if any(k in col.lower() for k in keywords):
            return col
    return None

try:
    print("Testing find_col with strings...")
    cols = ['Name', 'Age', 'Department']
    res = find_col(cols, ['dept', 'department'])
    print(f"Result: {res}")
except Exception as e:
    print(f"Error: {e}")

try:
    print("\nTesting find_col with integers...")
    cols = [1, 2, 3] # Common in Excel files without headers
    res = find_col(cols, ['dept'])
    print(f"Result: {res}")
except Exception as e:
    print(f"Error: {e}")
