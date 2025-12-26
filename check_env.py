import os
from dotenv import load_dotenv

load_dotenv(override=True)

# Print file content directly
with open(".env", "r") as f:
    print("File content (first 5 lines):")
    for i, line in enumerate(f):
        if i < 5:
            print(line.strip())

key = os.getenv("GEMINI_API_KEY")

if not key:
    print("GEMINI_API_KEY not found in environment.")
else:
    print(f"Key found: Yes")
    # print(f"Length: {len(key)}")
    # print(f"Starts with 'sk-': {key.startswith('sk-')}")
    # print(f"First 4 chars: {key[:4]}")
    # print(f"Last 4 chars: {key[-4:]}")
    has_quotes = '"' in key or "'" in key
    # print(f"Contains quotes: {has_quotes}")
    # print(f"Raw value (repr): {repr(key)}")
    print(' ')
