#version 330 core

layout(location=0) in vec3 vert_loc;
layout(location=1) in vec3 vert_nor;
out vec3 surface_normal;

uniform mat4 projection;
uniform mat4 model_view;

void main() {
    surface_normal = vert_nor;
    gl_Position = projection * model_view * vec4(vert_loc, 1.0f);
}
