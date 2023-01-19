import os
from novaclient.client import Client
from dotenv import load_dotenv

load_dotenv()

def get_nova_credentials_v2(ucreds={}):
    creds = {}
    creds['version'] = '2'
    if not ucreds:
        creds['username'] = os.environ['OS_USERNAME']
        creds['password'] = os.environ['OS_PASSWORD']
        creds['project_name'] = os.environ['OS_TENANT_NAME']
        creds['auth_url'] = os.environ['OS_AUTH_URL']
        creds['project_domain_name'] = os.getenv('OS_PROJECT_DOMAIN_NAME', 'Default')
        creds['user_domain_name'] = os.getenv('OS_USER_DOMAIN_NAME', 'Default')
    else:
        creds['username'] = ucreds['OS_USERNAME']
        creds['password'] = ucreds['OS_PASSWORD']
        creds['project_name'] = ucreds['OS_TENANT_NAME']
        creds['auth_url'] = ucreds['OS_AUTH_URL']
        creds['project_domain_name'] = ucreds['OS_PROJECT_DOMAIN_NAME']
        creds['user_domain_name'] = ucreds['OS_USER_DOMAIN_NAME']
    return creds

class OpenStackApi:
    nova = None

    def __init__(self):
        pass
    
    def nova_open(self, creds={}):
        self.nova = Client(**get_nova_credentials_v2(creds))


    def service_list(self):
        try:
            self.nova_open()
            return self.nova.services.list(), 0
        except Exception as err:
            return [], err

    def server_list(self, creds={}):
        # try:
        self.nova_open(creds)
        return self.nova.servers.list()
        # except Exception as err:
        #     return [], err
    
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