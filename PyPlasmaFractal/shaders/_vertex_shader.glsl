#version 330

in vec2 in_pos; // Input vertex positions in NDC
out vec2 v_tex; // Output texture coordinates
out vec2 v_pos; // Pass vertex position to fragment shader

void main() {
    gl_Position = vec4(in_pos, 0.0, 1.0); // Set vertex position in NDC
    v_tex = (in_pos + 1.0) * 0.5;         // Normalize from [-1,1] to [0,1] (texture coordinate space)
    v_pos = in_pos;                       // Pass through the original vertex position
}
