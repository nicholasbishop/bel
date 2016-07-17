#version 330 core

layout(triangles) in;
layout(triangle_strip, max_vertices = 3) out;

uniform vec2 fb_size;

in VsOut {
    vec3 vert_loc;
	vec3 vert_nor;
	vec4 vert_col;
} vs_out[];

out vec3 surface_normal;
out vec4 surface_color;
noperspective out vec3 dist;

vec2 viewport_to_screen_space(const vec2 framebuffer_size,
                              const vec4 point);

vec3 triangle_2d_altitudes(const vec2 triangle[3]);

void main() {
	vec2 triangle[3];

	triangle[0] = viewport_to_screen_space(fb_size, gl_in[0].gl_Position);
	triangle[1] = viewport_to_screen_space(fb_size, gl_in[1].gl_Position);
	triangle[2] = viewport_to_screen_space(fb_size, gl_in[2].gl_Position);

	vec3 altitudes = triangle_2d_altitudes(triangle);

	dist = vec3(altitudes[0], 0, 0);
    surface_normal = vs_out[0].vert_nor;
	surface_color = vs_out[0].vert_col;
    gl_Position = gl_in[0].gl_Position;
    EmitVertex();

    dist = vec3(0, altitudes[1], 0);
    surface_normal = vs_out[1].vert_nor;
	surface_color = vs_out[1].vert_col;
    gl_Position = gl_in[1].gl_Position;
    EmitVertex();

    dist = vec3(0, 0, altitudes[2]);
    surface_normal = vs_out[2].vert_nor;
	surface_color = vs_out[2].vert_col;
    gl_Position = gl_in[2].gl_Position;
    EmitVertex();

    EndPrimitive();
}
