import unittest

from internal import api
from internal import database
from internal.memory import User

db = database.Database("sqlite:///db.sqlite")
osapi = api.OpenStackApi()

# class Test_OSAPI(unittest.TestCase):
#     def test_service_list(self):
#         services, err = osapi.service_list()
#         if err:
#             print(err)
#         for s in services:
#             print(f"HOST: {s.host} STATE: {s.state} ZONE {s.zone}")

#     def test_server_list(self):
#         servers, err = osapi.server_list()
#         if err:
#             print(err)
#         for s in servers:
#             print(f"Name: {s.name} STATE: {s.status} ID {s.id}")

class TestDatabase(unittest.TestCase):
    # def test_create_user(self):
    #     u = User(0, "testing")
    #     user = db.login(u)
    #     print(user.username)

    # def test_update_creds(self):
    #     u = User(0, "testing")
    #     u.creds = b'''TEST=some_env_var'''
    #     db.update_creds(u)
    #     user = db.login(u)
    #     print(user.creds)
    
    # def test_get_env(self):
    #     self.test_update_creds()
    #     u = User(0, "testing")
    #     user = db.login(u)
    #     env = user.get_env()
    #     print(env["TEST"])

    def test_get_server_user(self):
        u = User(0, "testing")
        user = db.login(u)
        servers, err = osapi.server_list(user.get_creds())
        print("ERR:", err)
        for s in servers:
            print(s.name)

if __name__ == '__main__':
    unittest.main()