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

    def test_server_show(self):
        server, err = osapi.server_show("ac8b2c98-6fbe-40b1-8e0b-2506162e4288")
        if err:
            print(err)
        print(server)
if __name__ == '__main__':
    unittest.main()