#version 330 core

layout(location=0) in vec3 vert_loc;
layout(location=1) in vec3 vert_nor;
layout(location=2) in vec4 vert_col;

out VsOut {
    vec3 vert_loc;
	vec3 vert_nor;
	vec4 vert_col;
} vs_out;
    
uniform mat4 projection;
uniform mat4 camera;
uniform mat4 model;

void main() {
    gl_Position = projection * camera * model * vec4(vert_loc, 1.0f);
	vs_out.vert_loc = vert_loc;
	vs_out.vert_nor = vert_nor;
	vs_out.vert_col = vert_col;
}
