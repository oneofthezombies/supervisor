import subprocess
import os
import sys

from dotenv import load_dotenv

load_dotenv()

result = subprocess.run(sys.argv[1:], env=os.environ)
sys.exit(result.returncode)
