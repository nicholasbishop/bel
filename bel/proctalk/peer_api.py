# pylint crashes when linting the module if this file is included. It
# doesn't crash when linting just this file though. (pylint 1.5.5,
# astroid 1.4.5) For now just disable all checks here.
#
# pylint: skip-file

def make_method(method_name):
    async def method(self, *params):
        return await self.rpc.call('_hub_dispatch',
                                   dst=self.client_id,
                                   method=method_name,
                                   params=params)
    return method


# TODO(nicholasbishop): make |api| a class that includes both methods
# and type name, then give that name instead of 'PeerApi' for better
# error messages
def create_peer_api(api):
    def init(self, rpc, client_id):
        self.rpc = rpc
        self.client_id = client_id

    members = {'__init__': init}
    for method_name in api:
        members[method_name] = make_method(method_name)
    return type('PeerApi', (object,), members)
