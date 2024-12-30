#include "common/color_adjustment.glsl"

/// Blends two colors linearly based on a given alpha value.
///
/// This function linearly interpolates between two colors, effectively blending them together.
/// The alpha parameter controls the blend ratio, determining the influence of each color in the output.
///
/// @param color1 The first color in the blending operation.
/// @param color2 The second color to blend with the first color.
/// @param alpha The alpha value used for blending.
///
/// @return vec4 The resulting color after blending the first and second colors based on alpha.

vec4 blend_linear(vec4 color1, vec4 color2, float alpha) {
    return mix(color1, color2, alpha);
}

/// Blends two colors additively based on a given alpha value.
///
/// This function adds the second color to the first color weighted by alpha, enhancing the brightness
/// and potentially leading to high dynamic range effects. The alpha value scales the second color's influence.
///
/// @param color1 The first color in the blending operation.
/// @param color2 The second color to add to the first color.
/// @param alpha The alpha value used for blending.
///
/// @return vec4 The resulting color after adding the second color to the first color, scaled by alpha.

vec4 blend_additive(vec4 color1, vec4 color2, float alpha) {
    return color1 * (1.0 - alpha) + color2;
}

/// Blends two colors using a sigmoid function to control the contrast of the blend.
///
/// This function applies a sigmoid contrast curve to the alpha parameter based on the luminance of the first color.
/// The steepness and midpoint parameters fine-tune the sigmoid curve, affecting the transition smoothness
/// and center point of the blend, respectively.
///
/// @param color1 The first color in the blending operation.
/// @param color2 The second color to blend with the first color.
/// @param alpha The alpha value used for blending, modified by the sigmoid contrast function.
/// @param steepness The steepness of the sigmoid contrast curve.
/// @param midpoint The midpoint of the sigmoid contrast curve.
///
/// @return vec4 The resulting color after applying the sigmoid-modified alpha blending.

vec4 blend_sigmoid(vec4 color1, vec4 color2, float alpha, float steepness, float midpoint) {
    float modifiedAlpha = alpha * sigmoid_contrast(luminance(color1.rgb), steepness * 10, midpoint);
    return mix(color1, color2, modifiedAlpha);
}
