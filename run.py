"""
run.py — Entry point for the Auto Unit Test Generator
"""

from app import create_app

app = create_app()

if __name__ == "__main__":
    print("\n" + "═" * 52)
    print("  🧪  AST Unit Test Generator")
    print("  → http://127.0.0.1:5000")
    print("═" * 52 + "\n")
    app.run(debug=True, host="0.0.0.0", port=5000)