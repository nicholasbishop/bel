# pylint crashes when linting this function, not sure why yet.
# (pylint 1.5.5, astroid 1.4.5) For now just disable all checks here.
#
# pylint: skip-file

def create_peer_api(api):
    def init(self, rpc, client_id):
        self.rpc = rpc
        self.client_id = client_id

    def make_method(method_name):
        async def method(self, *params):
            return await self.rpc.call('_hub_dispatch', {
                'client_id': self.client_id,
                'method': method_name,
                'params': params
            })
        return method

    members = {'__init__': init}
    for method_name in api:
        members[method_name] = make_method(method_name)
    return type('PeerApi', (object,), members)
