import os
from dotenv import load_dotenv

load_dotenv()
disable_mode = os.getenv("DISABLE_AI_MODE")
print(f"DISABLE_AI_MODE={disable_mode}")
print(f"Type: {type(disable_mode)}")
print(f"Lower: {disable_mode.lower() if disable_mode else 'None'}")
print(f"Comparison: {disable_mode.lower() == 'true' if disable_mode else False}")


