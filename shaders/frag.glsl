#version 330 core

noperspective in vec3 dist;
in vec3 surface_normal;
in vec4 surface_color;
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

	// TODO, dijkstra viz hack
	float dista = surface_color[0];

	if (dista < 0) {
		color *= vec4(0.3, 0.3, 0.3, 1.0);
	} else {
		//color[0] = dista;
		float rep = 0.1;
		float fac = 1.0 / rep;
		color[0] = pow(mod(surface_color[0], rep) * fac, 4);
	}
}
