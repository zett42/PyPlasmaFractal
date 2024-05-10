#include "color_adjustment.glsl"

vec4 blendLinear(vec4 prevColor, vec4 currentColor, float alpha, float unused, float unused2) {
    return mix(prevColor, currentColor, alpha);
}

vec4 blendAdditive(vec4 prevColor, vec4 currentColor, float alpha, float unused, float unused2) {
    return prevColor * (1.0 - alpha) + currentColor;
}

vec4 blendSigmoid(vec4 prevColor, vec4 currentColor, float alpha, float contrastSteepness, float contrastMidpoint) {

    // Apply the sigmoid function to modify alpha
    float modifiedAlpha = alpha * sigmoidContrast(luminance(prevColor.rgb), contrastSteepness * 10, contrastMidpoint);

    // Perform the blending with the modified alpha
    return mix(prevColor, currentColor, modifiedAlpha);
}