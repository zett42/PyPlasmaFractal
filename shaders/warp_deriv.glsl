//----------------------------------------------------------------------------------------------------------------------------------
// Warp functions for texture coordinates, based on a noise vector.
// The functions in this file are used as template functions, so they must have the same number and kind of arguments.
//----------------------------------------------------------------------------------------------------------------------------------

#include "math_constants.glsl"
#include "transforms.glsl"

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

/// @brief Transforms a position vector using noise-induced warping for procedural animation effects.
///
/// This function applies a swirling distortion effect to a 2D position based on noise values and a set of parameters. 
/// It calculates a dynamic swirling center influenced by noise derivatives, scales the influence on distance,
/// and applies a sigmoid function to create a soft transition effect within a controlled range.
///
/// @param pos The original 2D position vector to be transformed.
/// @param noiseWithDerivatives A 4D vector containing a noise value and its derivatives in the xy-plane.
/// @param time The current time or frame, used to animate or vary the effect over time (not used in this specific implementation).
/// @param params An array of float values containing parameters to control the effect:
///               - params[0]: Controls the scale of the radius from the center of the swirl.
///               - params[1]: Controls the scaling factor for the angle of rotation around the swirl center.
///               - params[2]: Represents the isolation of the effect, controlling how localized the effect appears.
///               - params[3]: The midpoint for scaling the isolation effect, adjusting the center point of the sigmoid function.
///
/// @return Returns a new 2D position vector that has been distorted by the noise-based warping effect.
vec2 warpSwirlSigmoid(vec2 pos, vec4 noiseWithDerivatives, float time, float params[MAX_WARP_PARAMS]) {

    float radiusScale = params[0];
    float angleScale  = params[1];
    float isolation   = params[2];
    float isolationMidpoint = params[3];

    // Scale the isolation input from [0, 1] to a more effective range [0, 10]
    float steepness = 20.0 * isolation; // Amplify the input value for steepness

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

    // Use the sigmoid function directly with correctly adjusted parameters
    float swirlIntensity = sigmoid(normalizedDistance, steepness, isolationMidpoint);

    float newAngle = angle + angleScale * swirlIntensity;

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

    float displacementScale = params[0] * 0.05;
    float falloffRate = params[1] * 10.;  // New parameter to control the falloff rate
    float noiseValue = noiseWithDerivatives.x;
    vec2 derivatives = noiseWithDerivatives.yz;

    // Smooth the derivatives to avoid sharp changes
    vec2 smoothedDerivatives = normalize(derivatives) * smoothstep(0.0, 1.0, length(derivatives));

    // Implementing falloff based on the noise value
    float falloff = exp(-falloffRate * abs(noiseValue));

    // Calculate displacement with moderated influence of derivatives and apply falloff
    vec2 displacement = displacementScale * noiseValue * smoothedDerivatives * falloff;

    vec2 newPos = pos + displacement;

    return newPos;
}
