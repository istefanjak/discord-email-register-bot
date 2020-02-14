"""
Log test file, ignore
"""
from log import getLogger

if __name__ == "__main__":
    getLogger(__file__).debug("Debug")