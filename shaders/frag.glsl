#version 330 core

in vec3 surface_normal;
out vec4 color;

void main() {
	color = vec4((surface_normal.x + 1.0) * 0.5,
				 (surface_normal.y + 1.0) * 0.5,
				 (surface_normal.z + 1.0) * 0.5,
				 1.0);
}
