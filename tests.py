import unittest

from internal import api

osapi = api.OpenStackApi()

class Test_OSAPI(unittest.TestCase):
    def test_service_list(self):
        services, err = osapi.service_list()
        if err:
            print(err)
        for s in services:
            print(f"HOST: {s.host} STATE: {s.state} ZONE {s.zone}")

    def test_server_list(self):
        servers, err = osapi.server_list()
        if err:
            print(err)
        for s in servers:
            print(f"Name: {s.name} STATE: {s.status} ID {s.id}")

if __name__ == '__main__':
    unittest.main()