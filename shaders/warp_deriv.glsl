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

// Modifies texture coordinates using noise and derivatives to create fractal-like patterns in feedback effects.
//
// This function duplicates texture elements around centers calculated from noise values and their derivatives,
// facilitating the generation of complex, evolving patterns. These transformations are enhanced through parameters
// controlling duplication scale, influence radius, non-linearity of transformations, and dynamic rotation effects,
// both static and time-modulated. 
//
// Parameters:
// - pos: Original texture coordinates.
// - noiseWithDerivatives: A vec4 containing the noise value (x) and its derivatives (yz), influencing the duplication scale
//   and the dynamic centers.
// - params: Array of parameters:
//     * params[0] (duplicationScale) - Scales duplication, affecting spatial distribution.
//     * params[1] (influenceRadius) - Defines the focus area of the effect.
//     * params[2] (nonLinearity) - Adjusts the progression of the influence curve.
//     * params[3] (baseRotationIntensity) - Base rotation intensity around dynamic centers.
//     * params[4] (timeModulationIntensity) - Modulates rotation intensity over time.
//     * params[5] (frequency) - Controls the oscillation speed of time-based rotation.
//
// Returns:
// - vec2: New texture coordinates after applying duplication and dynamic transformations.

vec2 warpInfiniteMirror(vec2 pos, vec4 noiseWithDerivatives, float time, float params[MAX_WARP_PARAMS]) {
    
    float duplicationScale = params[0] * 4.0; // Scaled duplication scale
    float influenceRadius = params[1];
    float nonLinearity = params[2] * 10.0; // Scaled non-linearity
    float baseRotationIntensity = params[3] * 2.0; // Base intensity of the rotation
    float timeModulationIntensity = params[4]; // Time-dependent modulation intensity
    float frequency = params[5] * 10.0; // Scaled frequency of the time-based modulation

    float noiseValue = noiseWithDerivatives.x;
    vec2 derivatives = noiseWithDerivatives.yz;

    vec2 center = pos + duplicationScale * noiseValue * normalize(derivatives);
    vec2 displacement = pos - center;

    // Calculate normalized distance and influence
    float normalizedDistance = length(displacement) / influenceRadius;
    float falloffPower = mix(0.1, 2.0, nonLinearity);
    float influence = 1.0 - pow(clamp(normalizedDistance, 0.0, 1.0), falloffPower);

    // Calculate rotation with time modulation
    float timeModulation = sin(time * frequency) * timeModulationIntensity * M_PI * 2;
    float rotationAngle = timeModulation + baseRotationIntensity;
    mat2 rotationMatrix = mat2(cos(rotationAngle), -sin(rotationAngle),
                               sin(rotationAngle), cos(rotationAngle));

    // Apply rotation around the center
    vec2 rotatedPos = center + rotationMatrix * (pos - center);

    // Calculate new texture coordinates
    vec2 newST = mix(pos, 2.0 * rotatedPos - center, influence);

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
