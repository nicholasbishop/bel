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

vec4 perspective_projection(const mat4 projection,
                            const mat4 camera,
                            const mat4 model,
                            const vec3 point);

void main() {
    gl_Position = perspective_projection(projection,
										 camera,
										 model,
										 vert_loc);
	vs_out.vert_loc = vert_loc;
	vs_out.vert_nor = vert_nor;
	vs_out.vert_col = vert_col;
}
