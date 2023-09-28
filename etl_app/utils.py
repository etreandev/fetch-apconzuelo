import json
import hashlib
from typing import Dict, Any

# In PROD we would handle this as a secret
def get_config_data():
    with open('../cfg/db_config.json') as file:
        return json.load(file)



