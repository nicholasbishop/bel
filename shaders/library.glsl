#version 330 core

// Wireframe rendering adapted from:
// - strattonbrazil.blogspot.com/2011/09/single-pass-wireframe-rendering_10.html
// - developer.download.nvidia.com/SDK/10/direct3d/Source/SolidWireframe/Doc/SolidWireframe.pdf

vec4 perspective_projection(const mat4 projection,
                            const mat4 camera,
                            const mat4 model,
                            const vec3 point) {
  return projection * camera * model * vec4(point, 1.0f);
}

// Transform point in viewport space to screen space
vec2 viewport_to_screen_space(const vec2 framebuffer_size,
                              const vec4 point) {
  return (framebuffer_size * point.xy) / point.w;
}

// Distance of each triangle vertex to the opposite edge
vec3 triangle_2d_altitudes(const vec2 triangle[3]) {
  vec2 v0 = triangle[2] - triangle[1];
  vec2 v1 = triangle[2] - triangle[0];
  vec2 v2 = triangle[1] - triangle[0];

  float area = abs((v1.x * v2.y) -
                   (v1.y * v2.x));

  return vec3(area / length(v0),
              area / length(v1),
              area / length(v2));
}
