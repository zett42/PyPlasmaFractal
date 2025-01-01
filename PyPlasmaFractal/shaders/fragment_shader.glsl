// This shader template utilizes fractal noise to dynamically generate visual effects on textures and optionally
// incorporates feedback mechanisms to enhance or transform the visual outputs based on previous frames. The shader is 
// designed to operate in real-time environments where effects like procedural textures, warping, and visual 
// distortions are desired. Parameters such as octaves, scale, amplitude, and time influence the fractal 
// noise generation.
// The feedback effect, if enabled, allows the shader to progressively evolve the output by blending the current frame's 
// output with a texture from a previous frame, controlled by parameters like feedback decay. This makes the 
// shader particularly useful for creating dynamic backgrounds, animated textures, or any graphics where 
// a sense of continuous change and motion is required.

#version 330
precision highp float;

#define NOISE_MIN           <NOISE_MIN>            // Minimum noise value
#define NOISE_MAX           <NOISE_MAX>            // Maximum noise value

// General uniforms
uniform float u_time;                   // Elapsed time in seconds
uniform sampler2D u_texture;            // Feedback texture (from previous frame)

// Parameters for fractal noise
uniform vec2 u_scale;                   // Scaling factor for the noise coordinates
uniform int u_octaves;                  // Number of noise octaves
uniform float u_gain;                   // Gain factor decreasing amplitude each octave
uniform float u_time_scale_factor;      // Time scaling per octave
uniform float u_position_scale_factor;  // Position scaling per octave
uniform float u_rotation_angle_increment; // Rotation angle increase per octave
uniform float u_time_offset_increment;  // Time offset increase per octave
uniform float u_brightness;             // Scales the noise output
uniform float u_contrast_steepness;     // Sigmoid function steepness for contrast adjustment
uniform float u_contrast_midpoint;      // Midpoint for sigmoid contrast function

// Parameters for fractal noise that warps the feedback texture
uniform float u_warp_speed;              // Noise mutation speed
uniform vec2 u_warp_scale;               // Noise scale factor
uniform int u_warp_octaves;              // Number of warping noise octaves
uniform float u_warp_gain;               // Noise gain factor
uniform float u_warp_time_scale_factor;  // Time scaling for warping noise
uniform float u_warp_position_scale_factor; // Position scaling for warping noise
uniform float u_warp_rotation_angle_increment; // Rotation angle increase for warping noise
uniform float u_warp_time_offset_initial;      // Time offset initial for warping noise
uniform float u_warp_time_offset_increment;    // Time offset increase for warping noise

// Declare uniforms for configurable function parameters
<FB_BLEND_FUNC_UNIFORMS>
<FB_WARP_FUNC_UNIFORMS>
<COLOR_FUNC_UNIFORMS>

// Input/Output
in vec2 v_tex;               // Texture coordinates from vertex shader
in vec2 v_pos;               // Position coordinates from vertex shader
out vec4 f_color;            // Fragment shader output color

#include "common/color_adjustment.glsl"
#include "common/transforms.glsl"

// Include user-selectable functions for noise, warp, blend, and color operations
#include "noise_functions\*.glsl"
#include "warp_functions\*.glsl"
#include "blend_functions\*.glsl"
#include "color_functions\*.glsl"

// Use the noise implementation specified by template argument for the fractal noise functions
#apply_template "fractal_noise/fractal_noise_single.glsl", NOISE_FUNC = <NOISE_FUNC>
#apply_template "fractal_noise/fractal_noise_double.glsl", NOISE_FUNC = <FB_WARP_NOISE_FUNC>
#apply_template "fractal_noise/fractal_noise_deriv.glsl", NOISE_FUNC = <FB_WARP_NOISE_FUNC>


// Function to apply feedback to the noise color, if enabled
vec4 apply_feedback_enabled(vec4 noise_color) {

    vec2 scaled_position = v_pos * u_warp_scale;  // Scale position by provided scale factor

    vec2 offset = warp_<FB_WARP_XFORM_FUNC>(
        v_tex,
        fractal_noise_<FB_WARP_FRACTAL_NOISE_VARIANT>_<FB_WARP_NOISE_FUNC>( 
            scaled_position, u_warp_octaves, u_warp_gain, u_warp_time_scale_factor, 
            u_warp_position_scale_factor, u_warp_rotation_angle_increment, 
            u_warp_time_offset_increment, u_warp_time_offset_initial + u_time * u_warp_speed ),
        u_time
        <FB_WARP_FUNC_ARGS>);
    
    vec4 tex_color = texture(u_texture, v_tex + offset);
    
    return blend_<FB_BLEND_FUNC>(tex_color, noise_color <FB_BLEND_FUNC_ARGS>);
}

// Do nothing with the noise color, if feedback is disabled
vec4 apply_feedback_disabled(vec4 noise_color) {
    return noise_color;
}

// Main shader function to process each fragment
void main() {

    // Compute fractal noise value and apply contrast adjustment

    vec2 scaled_position = v_pos * u_scale;  // Scale position by provided scale factor

    float grayscale = fractal_noise_single_<NOISE_FUNC>(scaled_position, u_octaves, u_gain, u_time_scale_factor, 
                                                        u_position_scale_factor, u_rotation_angle_increment, u_time_offset_increment, u_time);

    // Normalize noise to 0..1 range
    grayscale = (grayscale - NOISE_MIN) / (NOISE_MAX - NOISE_MIN); 

    grayscale = sigmoid_contrast(grayscale, u_contrast_steepness, u_contrast_midpoint); // Apply contrast adjustment
    grayscale = grayscale * u_brightness; // Apply brightness adjustment

    // Apply colorization to the noise color
    vec4 noise_color = colorize_<COLOR_FUNC>(grayscale, v_pos, u_time <COLOR_FUNC_ARGS>);

    // Apply feedback to the noise color, if enabled
    f_color = apply_feedback_<FB_ENABLED>(noise_color);
}
