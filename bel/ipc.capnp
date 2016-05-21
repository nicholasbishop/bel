@0xc654f5eb06492130;

struct MaterialId {
	
}

interface SceneNode {
	
}

interface App {
	shutdown @0 ();
}

interface Scene {
	sayHello @0 () -> (response :Text);
	loadPath @1 (path :Text) -> (node :SceneNode);
	shutdown @2 ();
}

interface Material {
}

interface Window {
	sayHello @0 () -> (response :Text);
	shutdown @1 ();
	setScene @2 (scene :Scene);
}
