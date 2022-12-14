import os
from novaclient.client import Client
from dotenv import load_dotenv

load_dotenv()

def get_nova_credentials_v2():
    d = {}
    d['version'] = '2'
    d['username'] = os.environ['OS_USERNAME']
    d['password'] = os.environ['OS_PASSWORD']
    d['project_name'] = os.environ['OS_TENANT_NAME']
    d['auth_url'] = os.environ['OS_AUTH_URL']
    d['project_domain_name'] = os.getenv('OS_PROJECT_DOMAIN_NAME', 'Default')
    # d['project_name'] = os.environ['OS_TENANT_NAME']
    d['user_domain_name'] = os.getenv('OS_USER_DOMAIN_NAME', 'Default')
    # d['interface'] = os.getenv('OS_INTERFACE', 'internal')
    return d

class OpenStackApi:
    nova = None

    def __init__(self):
        pass
    
    def nova_open(self):
        self.nova = Client(**get_nova_credentials_v2())

    def service_list(self):
        try:
            self.nova_open()
            return self.nova.services.list(), 0
        except Exception as err:
            return [], err

    def server_list(self):
        try:
            self.nova_open()
            return self.nova.servers.list(), 0
        except Exception as err:
            return [], err
    
    # def server_show(self, _id):
    #     try:
    #         self.nova_open()
    #         server = self.nova.servers.find(id=_id)
    #         if not server:
    #             return "", 0
    #         info = ""
    #         for gkey, gdata in server._info:
    #             if gkey == "addresses" and gdata:
    #                 info += "\tIP-адреса: {}".format(
    #                     '\n\t*'.join([f'{net}:`{addr["addr"]}`' for net, addr in gdata['addresses']]))
    #             else: info += "IP-адреса: Нет"
    #         return info
    #     except Exception as err:
    #         return "", err