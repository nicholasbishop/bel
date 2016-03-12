#version 330

layout(location = 0) in vec4 vert_loc;

void main() {
	gl_Position = vec4(vert_loc.x / 3.0, vert_loc.y / 3.0, vert_loc.z, 1);
}
