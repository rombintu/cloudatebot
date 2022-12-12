from internal import api

osapi = api.OpenStackApi()

class MEM:
    servers = []

    def refresh_servers(self):
        servers, err = osapi.server_list()
        if err:
            print(err)
            return
        # REFRESH CACHE
        self.servers = servers