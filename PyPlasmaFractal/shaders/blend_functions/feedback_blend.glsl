#include "common/color_adjustment.glsl"

// Blends two colors linearly based on a given alpha value.
//
// This function linearly interpolates between two colors, effectively blending them together.
// The alpha parameter controls the blend ratio, determining the influence of each color in the output.
//
// Parameters:
// - prevColor: The previous color in the blending operation.
// - currentColor: The current color to blend with the previous color.
// - params: An array where params[0] holds the alpha value used for blending.
//
// Returns:
// - vec4: The resulting color after blending the previous and current colors based on alpha.

vec4 blendLinear(vec4 prevColor, vec4 currentColor, float params[MAX_FEEDBACK_PARAMS]) {

    float alpha = params[0];

    return mix(prevColor, currentColor, alpha);
}


// Blends two colors additively based on a given alpha value.
//
// This function adds the current color to the previous color weighted by alpha, enhancing the brightness
// and potentially leading to high dynamic range effects. The alpha value scales the current color's influence.
//
// Parameters:
// - prevColor: The previous color in the blending operation.
// - currentColor: The current color to add to the previous color.
// - params: An array where params[0] holds the alpha value used for additive blending.
//
// Returns:
// - vec4: The resulting color after adding the current color to the previous color, scaled by alpha.

vec4 blendAdditive(vec4 prevColor, vec4 currentColor, float params[MAX_FEEDBACK_PARAMS]) {

    float alpha = params[0];

    return prevColor * (1.0 - alpha) + currentColor;
}


// Blends two colors using a sigmoid function to control the contrast of the blend.
//
// This function applies a sigmoid contrast curve to the alpha parameter based on the luminance of the previous color.
// The contrastSteepness and contrastMidpoint parameters fine-tune the sigmoid curve, affecting the transition smoothness
// and center point of the blend, respectively.
//
// Parameters:
// - prevColor: The previous color in the blending operation.
// - currentColor: The current color to blend with the previous color.
// - params: An array where params[0] is alpha, params[1] is contrastSteepness, and params[2] is contrastMidpoint.
//
// Returns:
// - vec4: The resulting color after applying the sigmoid-modified alpha blending.

vec4 blendSigmoid(vec4 prevColor, vec4 currentColor, float params[MAX_FEEDBACK_PARAMS]) {

    float alpha = params[0];
    float contrastSteepness = params[1];
    float contrastMidpoint = params[2];

    // Apply the sigmoid function to modify alpha based on the luminance of the previous color
    float modifiedAlpha = alpha * sigmoidContrast(luminance(prevColor.rgb), contrastSteepness * 10, contrastMidpoint);

    // Perform the blending with the modified alpha
    return mix(prevColor, currentColor, modifiedAlpha);
}
