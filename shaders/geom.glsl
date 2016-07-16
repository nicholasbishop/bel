// Adapted from:
// - strattonbrazil.blogspot.com/2011/09/single-pass-wireframe-rendering_10.html
// - developer.download.nvidia.com/SDK/10/direct3d/Source/SolidWireframe/Doc/SolidWireframe.pdf

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

void main() {
    vec2 p0 = fb_size * gl_in[0].gl_Position.xy / gl_in[0].gl_Position.w;
    vec2 p1 = fb_size * gl_in[1].gl_Position.xy / gl_in[1].gl_Position.w;
    vec2 p2 = fb_size * gl_in[2].gl_Position.xy / gl_in[2].gl_Position.w;

    vec2 v0 = p2 - p1;
    vec2 v1 = p2 - p0;
    vec2 v2 = p1 - p0;
    float area = abs((v1.x * v2.y) -
					 (v1.y * v2.x));

    dist = vec3(area / length(v0), 0, 0);
    surface_normal = vs_out[0].vert_nor;
	surface_color = vs_out[0].vert_col;
    gl_Position = gl_in[0].gl_Position;
    EmitVertex();

    dist = vec3(0, area / length(v1), 0);
    surface_normal = vs_out[1].vert_nor;
	surface_color = vs_out[1].vert_col;
    gl_Position = gl_in[1].gl_Position;
    EmitVertex();

    dist = vec3(0, 0, area / length(v2));
    surface_normal = vs_out[2].vert_nor;
	surface_color = vs_out[2].vert_col;
    gl_Position = gl_in[2].gl_Position;
    EmitVertex();

    EndPrimitive();
}
