import os
import sys

# Development mode.
if os.getenv("DEBUG"):
    print("DEBUG is set, injecting '.' into sys.path for local module lookup")
    sys.path.insert(0, '.')

from forgepb.command_line import start

if __name__ == '__main__':
    start()
