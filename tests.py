import unittest

from internal import api
from tools import parser

envs = parser.parse_dotenv()
print(envs)
osapi = api.OpenStackApi(
        username=envs["OS_USERNAME"],
        password=envs["OS_PASSWORD"],
        auth_url=envs["OS_AUTH_URL"],
        tenant_name=envs["OS_TENANT_NAME"],
        project_domain_name="Default",
)
class Test_OSAPI(unittest.TestCase):
    def test_service_list(self):
        services, err = osapi.service_list()
        if err:
            print(err)
        for s in services:
            print(f"HOST: {s.host} STATE: {s.state} ZONE {s.zone}")

    def test_server_list(self):
        server, err = osapi.server_list()
        if err:
            print(err)
        for s in server:
            print(f"Name: {s.name} STATE: {s.status} ID {s.id}")

if __name__ == '__main__':
    unittest.main()