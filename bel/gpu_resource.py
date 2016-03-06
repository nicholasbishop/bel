OK Nevermind :D

Just add message types for "create_material", "create_buffer_object", etc

class GpuResource:
    def __init__(self, src):
        self._src = src
        self._hnd = None

    @property
    def uid(self):
        return self._src.uid

    def update(self, src):
        # TODO
        pass

class GpuResources:
    def __init__(self):
        self._resources = {}

    def set_resource(self, resource):
        # TODO
        if resource.uid in self._resources:
            raise RuntimeError()
        self._resources[resource.uid] = resource
