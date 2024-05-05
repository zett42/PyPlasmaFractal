//----------------------------------------------------------------------------------------------------------------------------------
// Warp functions for texture coordinates, based on a noise vector.
// The functions in this file are used as template functions, so they must have the same number and kind of arguments.
//----------------------------------------------------------------------------------------------------------------------------------

#include "math_constants.glsl"

// Applies a simple offset to texture coordinates based on noise derivatives.
vec2 warpOffsetDeriv(vec2 pos, vec4 noiseWithDerivatives, float time, float params[MAX_WARP_PARAMS]) {

    float amplitude = params[0] * 0.01;

    vec2 derivatives = noiseWithDerivatives.yz;

    // Calculate the offset for the texture coordinates
    vec2 offset = amplitude * derivatives;

    return pos + offset;
}

// Applies a swirling effect to texture coordinates based on noise and its derivatives.
//
// This function modifies texture coordinates by introducing a swirling motion centered dynamically
// using the derivatives of noise values. By converting the Cartesian coordinates into polar coordinates
// around a noise-derived center, it applies a radial and angular distortion. This method effectively 
// reduces linear artifacts by swirling points around a varying center, thus avoiding the grid-like 
// effects commonly associated with direct Cartesian noise applications.
//
// Parameters:
// - pos: The original texture coordinates.
// - noiseWithDerivatives: A vec4 containing the noise value and its derivatives. The x component 
//   is used for adjusting the swirl angleScale, and yz components determine the dynamic center offset.
// - radiusScale: A scalar factor that adjusts the dynamic center based on noise derivatives.
// - angleScale: Controls the angleScale of the swirling effect, influencing the angular distortion.
//
// Returns:
// - vec2: The new texture coordinates after applying the swirling effect.

vec2 warpSwirl(vec2 pos, vec4 noiseWithDerivatives, float time, float params[MAX_WARP_PARAMS]) {

    float radiusScale = params[0];
    float angleScale  = params[1];
    float isolation   = params[2];

    // Scale the isolation input from [0, 1] to a more effective range [0, 10]
    float scaledIsolationFactor = 10.0 * isolation; // Amplify the input value

    // Extract noise value and derivatives from the input
    float noiseValue = noiseWithDerivatives.x;
    vec2 derivatives = noiseWithDerivatives.yz;

    // Determine a dynamic center for the swirl based on noise and its derivatives
    vec2 center = pos + radiusScale * derivatives;

    // Calculate distance and angle from the center for the swirling effect
    vec2 toCenter = pos - center;
    float distance = length(toCenter);
    float angle = atan(toCenter.y, toCenter.x);

    // Safe normalization of distance to avoid division by zero
    float safeRadiusScale = radiusScale + 0.0001; // Adding a tiny value to avoid zero
    float normalizedDistance = distance / safeRadiusScale;

    // Modify swirl decrease with distance, incorporating the scaled isolation factor
    float newAngle = angle + angleScale * exp(-scaledIsolationFactor * normalizedDistance);

    // Calculate new texture coordinates
    vec2 newST = center + normalizedDistance * radiusScale * vec2(cos(newAngle), sin(newAngle));

    return newST;
}

// Applies a duplication effect to texture coordinates based on noise and its derivatives to support fractal-like patterns in feedback effects.
//
// This function modifies texture coordinates by strategically duplicating texture elements around dynamically 
// calculated centers derived from noise values. By adjusting the noise derivatives and the original position, 
// the function positions multiple instances of texture patterns, which can lead to complex, fractal-like visual 
// effects when used in a feedback loop. This technique is particularly effective for generating intricate 
// patterns that evolve over time, reducing uniformity and avoiding repetitive grid-like effects commonly 
// associated with direct noise applications.
//
// Parameters:
// - pos: The original texture coordinates.
// - noiseWithDerivatives: A vec4 containing the noise value and its derivatives. The x component 
//   influences the scale and intensity of the duplication, while the yz components are crucial in 
//   determining the dynamic centers for duplication.
// - params: An array of parameters where:
//     * params[0] (duplicationScale) - A scalar that adjusts the scale of duplication, influencing 
//       the spatial distribution of the duplicates.
//     * params[1] (influenceRadius) - Defines the radius within which the duplication effect is 
//       concentrated, aiding in the smooth integration of duplicated textures with the original.
//
// Returns:
// - vec2: The new texture coordinates after applying the duplication effect, which when used in feedback loops,
//   can contribute to the generation of fractal patterns.

vec2 warpInfiniteMirror(vec2 pos, vec4 noiseWithDerivatives, float time, float params[MAX_WARP_PARAMS]) {
    
    // Parameters for transformation
    float duplicationScale = params[0];
    float influenceRadius = params[1];

    // Extract noise and derivatives
    float noiseValue = noiseWithDerivatives.x;
    vec2 derivatives = noiseWithDerivatives.yz;

    // Calculate dynamic center for texture duplication
    vec2 center = pos + duplicationScale * noiseValue * normalize(derivatives);

    // Compute distance from the original position to the new center
    vec2 displacement = pos - center;
    float distance = length(displacement);

    // Influence calculation to limit effect based on distance
    float influence = smoothstep(influenceRadius, 0.0, distance);

    // Calculate final texture coordinates by blending original and duplicated
    vec2 newST = mix(pos, 2.0 * pos - center, influence);

    return newST;
}

// This is just a playground function for developing new effects. It can be used to test new ideas and techniques.
// NOTE: pos is the texture coordinates, noiseWithDerivatives is a vec4 containing the noise value and its derivatives,
// and param1, param2, param3, and param4 are user-controllable parameters that can be used in the function, with a range of [0, 1].
vec2 warpTest(vec2 pos, vec4 noiseWithDerivatives, float time, float params[MAX_WARP_PARAMS]) {
    
    float param1 = params[0];
    float param2 = params[1];
    float param3 = params[2];
    float param4 = params[3];

    // Extract noise value and derivatives from the input
    float noiseValue = noiseWithDerivatives.x;
    vec2 derivatives = noiseWithDerivatives.yz;

    // Adjust parameters for more subtle effects
    float amplitude = mix(0.001, 0.005, param1);  // Lowered amplitude
    float frequency = mix(1.0, 5.0, param2);      // Reduced frequency for smoother transitions
    float noiseMix = mix(0.5, 1.0, param3);       // Focus on stronger influence of derivatives
    float directionalStrength = mix(0.01, 0.1, param4);  // Reduced directional strength

    // Dynamic center based on derivatives
    vec2 center = pos + derivatives * noiseMix;

    // Calculate displacement around the dynamic center
    vec2 displacement;
    displacement.x = amplitude * sin(frequency * (pos.x - center.x) + noiseValue);
    displacement.y = amplitude * cos(frequency * (pos.y - center.y) + noiseValue);

    // Apply displacement to position
    vec2 newPos = pos + displacement;

    return newPos;
}
