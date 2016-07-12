#version 330 core

layout(location=0) in vec3 vert_loc;
layout(location=1) in vec4 vert_col;

out vec4 vs_color;

uniform mat4 projection;
uniform mat4 camera;
uniform mat4 model;

void main() {
	vs_color = vert_col;
    gl_Position = projection * camera * model * vec4(vert_loc, 1.0f);
}
