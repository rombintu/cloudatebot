import os, sys
from dotenv import load_dotenv

# load vars from .env file
load_dotenv()

error_parse = "Some vars from .env is None: {}"

def parse_dotenv() -> dict:
    envs = {
        "TOKEN" : os.getenv('TOKEN', default=None),
        "DATABASE" : os.getenv("DATABASE", default="sqlite://"),
        
        "OS_USERNAME": os.getenv("OS_USERNAME", default="admin"),
        "OS_TENANT_NAME": os.getenv("OS_TENANT_NAME", default="admin"),
        "OS_AUTH_URL": os.getenv("OS_AUTH_URL", default="http://admin"),
        "OS_PASSWORD": os.getenv("OS_PASSWORD", default="admin"),

    }
    if None in envs.values():
        print(error_parse.format(["TOKEN, DATABASE"]))
        sys.exit(0)
    return envs