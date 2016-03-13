#version 330 core

layout(location=0) in vec3 vert_loc;
layout(location=1) in vec3 vert_nor;
out vec3 surface_normal;

uniform mat4 projection;
uniform mat4 model_view;

void main() {
    float zpos = -2.0;
    vec4 adj = vec4(vert_loc.x, vert_loc.y, vert_loc.z + zpos, 1.0f);
    surface_normal = vert_nor;
    gl_Position = projection * model_view * adj;
}
