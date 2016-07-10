#version 330 core

noperspective in vec3 dist;
in vec3 surface_normal;
out vec4 color;

void main() {
	color = vec4((surface_normal.x + 1.0) * 0.5,
				 (surface_normal.y + 1.0) * 0.5,
				 (surface_normal.z + 1.0) * 0.5,
				 1.0);

	// Adapted from http://strattonbrazil.blogspot.com/2011/09/single-pass-wireframe-rendering_10.html
	float nearest = min(min(dist[0],dist[1]),dist[2]);
	float edge_intensity = 1.0 - exp2(-1.0 * nearest * nearest);

	color = color * edge_intensity;
}
