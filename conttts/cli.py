import sys
from conttts.main import run_gui

def main():
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "download":
            print("Downloading models...")  # <- You can plug actual logic here
        else:
            print(f"Unknown command: {command}")
    else:
        run_gui()
