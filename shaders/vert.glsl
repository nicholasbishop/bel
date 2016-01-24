attribute vec4 vert_loc;
 
uniform mat4 model_view;
uniform mat4 projection;
 
void main() {
    vec4 p = model_view * vert_loc;
    gl_Position = projection * p;
}
