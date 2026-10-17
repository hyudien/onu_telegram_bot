import os

from settings import load_dotenv

load_dotenv()

ROUTERS = {

    "KWL": {
        "host": os.getenv("MIKROTIK_KWL_HOST", "192.168.220.1"),
        "username": os.getenv("MIKROTIK_KWL_USERNAME", ""),
        "password": os.getenv("MIKROTIK_KWL_PASSWORD", ""),
        "port": int(os.getenv("MIKROTIK_KWL_PORT", "3101"))
    },

    "NOMBES": {
        "host": os.getenv("MIKROTIK_NOMBES_HOST", "103.160.178.39"),
        "username": os.getenv("MIKROTIK_NOMBES_USERNAME", ""),
        "password": os.getenv("MIKROTIK_NOMBES_PASSWORD", ""),
        "port": int(os.getenv("MIKROTIK_NOMBES_PORT", "8777"))
    }

}
