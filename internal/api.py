# import keystoneauth1.session as session
# import novaclient.client as novaclient

from keystoneclient import session
# import keystoneauth1.identity.v2 as auth
from keystoneclient.auth.identity.v3 import Password
# from keystoneclient.v3 import client
from novaclient import client as novacli

class OpenStackApi:
    session = None
    nova = None

    OS_USERNAME="admin"
    OS_TENANT_NAME="admin"
    OS_AUTH_URL=""
    OS_PASSWORD=""
    OS_TENANT_NAME="admin"
    OS_INTERFACE="internal"
    OS_PROJECT_DOMAIN_NAME="Default"

    def __init__(self, username, password, auth_url, 
                tenant_name, project_domain_name):
        self.OS_USERNAME = username
        self.OS_PASSWORD = password
        self.OS_AUTH_URL = auth_url
        self.OS_TENANT_NAME = tenant_name
        self.OS_PROJECT_DOMAIN_NAME = project_domain_name
    
    def server_list(self):
        pass
    
    def nova_open(self):
        self.session = session.Session(
            auth=Password(
                auth_url=self.OS_AUTH_URL,
                username=self.OS_USERNAME,
                password=self.OS_PASSWORD,
                project_name=self.OS_TENANT_NAME,
                user_domain_name="Default",
                project_domain_name=self.OS_PROJECT_DOMAIN_NAME,
            )
        )
        self.nova = novacli.Client(version="2.0", session=self.session)

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
 