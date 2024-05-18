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
#define MAX_FEEDBACK_PARAMS <MAX_FEEDBACK_PARAMS>  // Maximum number of feedback blend parameters
#define MAX_WARP_PARAMS     <MAX_WARP_PARAMS>      // Maximum number of warp parameters

// General uniforms
uniform float u_time;                   // Elapsed time in seconds
uniform sampler2D u_texture;            // Feedback texture (from previous frame)

// Parameters for fractal noise
uniform vec2 u_scale;                   // Scaling factor for the noise coordinates
uniform int u_octaves;                  // Number of noise octaves
uniform float u_gain;                   // Gain factor decreasing amplitude each octave
uniform float u_timeScaleFactor;        // Time scaling per octave
uniform float u_positionScaleFactor;    // Position scaling per octave
uniform float u_rotationAngleIncrement; // Rotation angle increase per octave
uniform float u_timeOffsetIncrement;    // Time offset increase per octave
uniform float u_brightness;             // Scales the noise output
uniform float u_contrastSteepness;      // Sigmoid function steepness for contrast adjustment
uniform float u_contrastMidpoint;       // Midpoint for sigmoid contrast function

// Feedback blend parameters
uniform float u_feedbackParams[MAX_FEEDBACK_PARAMS]; // Parameters specific to the feedback blend function

// Parameters for fractal noise that warps the feedback texture
uniform float u_warpParams[MAX_WARP_PARAMS]; // Parameters specific to the warp function
uniform float u_warpSpeed;              // Noise mutation speed
uniform vec2 u_warpScale;               // Noise scale factor
uniform int u_warpOctaves;              // Number of warping noise octaves
uniform float u_warpGain;               // Noise gain factor
uniform float u_warpTimeScaleFactor;    // Time scaling for warping noise
uniform float u_warpPositionScaleFactor;// Position scaling for warping noise
uniform float u_warpRotationAngleIncrement; // Rotation angle increase for warping noise
uniform float u_warpTimeOffsetInitial;      // Time offset initial for warping noise
uniform float u_warpTimeOffsetIncrement;    // Time offset increase for warping noise

// Input/Output
in vec2 v_tex;               // Texture coordinates from vertex shader
in vec2 v_pos;               // Position coordinates from vertex shader
out vec4 f_color;            // Fragment shader output color

#include "color_adjustment.glsl"
#include "transforms.glsl"

// Include user-selectable functions for noise, warp, and blend operations
#include "noise_functions/perlin_3d_std.glsl"
#include "noise_functions/perlin_3d_double.glsl"
#include "noise_functions/perlin_3d_deriv.glsl"
#include "noise_functions/simplex_perlin_3d_std.glsl"
#include "noise_functions/simplex_perlin_3d_double.glsl"
#include "noise_functions/simplex_perlin_3d_deriv.glsl"
#include "noise_functions/cellular_3d_std.glsl"
#include "noise_functions/cellular_3d_double.glsl"
#include "noise_functions/cellular_3d_deriv.glsl"

#include "warp_functions/warp_double.glsl"
#include "warp_functions/warp_deriv.glsl"

#include "blend_functions/feedback_blend.glsl"

// Use the noise implementation specified by template argument for the fractal noise functions
#apply_template "fractal_noise/fractal_noise_single.glsl", NOISE_FUNC = <NOISE_FUNC>
#apply_template "fractal_noise/fractal_noise_double.glsl", NOISE_FUNC = <FB_WARP_NOISE_FUNC>
#apply_template "fractal_noise/fractal_noise_deriv.glsl", NOISE_FUNC = <FB_WARP_NOISE_FUNC>


// Function to apply feedback to the noise color, if enabled
vec4 applyFeedback_Enabled(vec4 noise_color) {

    vec2 scaledPosition = v_pos * u_warpScale;  // Scale position by provided scale factor

    vec4 tex_color = warp<FB_WARP_XFORM_FUNC>(
        u_texture,
        v_tex,
        noise_color,
        fractalNoise_<FB_WARP_FRACTAL_NOISE_VARIANT>_<FB_WARP_NOISE_FUNC>( 
            scaledPosition, u_warpOctaves, u_warpGain, u_warpTimeScaleFactor, 
            u_warpPositionScaleFactor, u_warpRotationAngleIncrement, 
            u_warpTimeOffsetIncrement, u_warpTimeOffsetInitial + u_time * u_warpSpeed ),
        u_time,
        u_warpParams);
    
    return blend<FB_BLEND_FUNC>(tex_color, noise_color, u_feedbackParams);
}

// Do nothing with the noise color, if feedback is disabled
vec4 applyFeedback_Disabled(vec4 noise_color) {
    return noise_color;
}

// Main shader function to process each fragment
void main() {

    // Compute fractal noise value and apply contrast adjustment

    vec2 scaledPosition = v_pos * u_scale;  // Scale position by provided scale factor

    float grayscale = fractalNoise_Single_<NOISE_FUNC>(scaledPosition, u_octaves, u_gain, u_timeScaleFactor, 
                                                       u_positionScaleFactor, u_rotationAngleIncrement, u_timeOffsetIncrement, u_time);

    // Normalize noise to 0..1 range
    grayscale = (grayscale - NOISE_MIN) / (NOISE_MAX - NOISE_MIN); 

    grayscale = sigmoidContrast(grayscale, u_contrastSteepness, u_contrastMidpoint); // Apply contrast adjustment
    grayscale = grayscale * u_brightness; // Apply brightness adjustment
    vec4 noise_color = vec4(grayscale, grayscale, grayscale, 1.0); // Set output color to grayscale

    // Apply feedback to the noise color, if enabled
    f_color = applyFeedback_<FB_ENABLED>(noise_color);
}
