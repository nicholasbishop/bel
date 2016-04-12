@0xc654f5eb06492130;

struct MaterialId {
	
}

interface SceneNode {
	
}

interface Scene {
	loadPath @0 (path :Text) -> (node :SceneNode);
}

interface Material {
}

interface Window {
	sayHello @0 () -> (response :Text);
}
