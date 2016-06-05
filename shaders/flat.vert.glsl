#version 330 core

layout(location=0) in vec3 vert_loc;

uniform mat4 projection;
uniform mat4 model_view;

void main() {
    gl_Position = projection * model_view * vec4(vert_loc, 1.0f);
}
