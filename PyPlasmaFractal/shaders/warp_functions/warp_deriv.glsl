//----------------------------------------------------------------------------------------------------------------------------------
// Warp functions for texture coordinates, based on a noise vector.
// The functions in this file are used as template functions, so they must have the same number and kind of arguments.
//----------------------------------------------------------------------------------------------------------------------------------

#include "math_constants.glsl"
#include "transforms.glsl"

// Applies a simple offset to texture coordinates based on noise derivatives.
vec2 warpOffsetDeriv(vec2 texPos, vec4 noiseWithDerivatives, float time, float params[MAX_WARP_PARAMS]) {

    float amplitude = params[0] * 0.01;

    vec2 derivatives = noiseWithDerivatives.yz;

    // Calculate the offset for the texture coordinates
    vec2 offset = amplitude * derivatives;

    return offset;    
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
// - texPos: The original texture coordinates.
// - noiseWithDerivatives: A vec4 containing the noise value and its derivatives. The x component 
//   is used for adjusting the swirl angleScale, and yz components determine the dynamic center offset.
// - radiusScale: A scalar factor that adjusts the dynamic center based on noise derivatives.
// - angleScale: Controls the angleScale of the swirling effect, influencing the angular distortion.
//
// Returns:
// - vec2: The new texture coordinates after applying the swirling effect.

vec2 warpSwirl(vec2 texPos, vec4 noiseWithDerivatives, float time, float params[MAX_WARP_PARAMS]) {

    float radiusScale = params[0];
    float angleScale  = params[1];
    float isolation   = params[2];

    // Scale the isolation input from [0, 1] to a more effective range [0, 10]
    float scaledIsolationFactor = 10.0 * isolation; // Amplify the input value

    // Extract noise value and derivatives from the input
    float noiseValue = noiseWithDerivatives.x;
    vec2 derivatives = noiseWithDerivatives.yz;

    // Determine a dynamic center for the swirl based on noise and its derivatives
    vec2 center = texPos + radiusScale * derivatives;

    // Calculate distance and angle from the center for the swirling effect
    vec2 toCenter = texPos - center;
    float distance = length(toCenter);
    float angle = atan(toCenter.y, toCenter.x);

    // Safe normalization of distance to avoid division by zero
    float safeRadiusScale = radiusScale + 0.0001; // Adding a tiny value to avoid zero
    float normalizedDistance = distance / safeRadiusScale;

    // Modify swirl decrease with distance, incorporating the scaled isolation factor
    float newAngle = angle + angleScale * exp(-scaledIsolationFactor * normalizedDistance);

    // Calculate new texture coordinates
    vec2 newPos = center + normalizedDistance * radiusScale * vec2(cos(newAngle), sin(newAngle));

    return newPos - texPos;   
}

/// @brief Transforms a position vector using noise-induced warping for procedural animation effects.
///
/// This function applies a swirling distortion effect to a 2D position based on noise values and a set of parameters. 
/// It calculates a dynamic swirling center influenced by noise derivatives, scales the influence on distance,
/// and applies a sigmoid function to create a soft transition effect within a controlled range.
///
/// @param texPos The original 2D position vector to be transformed.
/// @param noiseWithDerivatives A 4D vector containing a noise value and its derivatives in the xy-plane.
/// @param time The current time or frame, used to animate or vary the effect over time (not used in this specific implementation).
/// @param params An array of float values containing parameters to control the effect:
///               - params[0]: Controls the scale of the radius from the center of the swirl.
///               - params[1]: Controls the scaling factor for the angle of rotation around the swirl center.
///               - params[2]: Represents the isolation of the effect, controlling how localized the effect appears.
///               - params[3]: The midpoint for scaling the isolation effect, adjusting the center point of the sigmoid function.
///
/// @return Returns a new 2D position vector that has been distorted by the noise-based warping effect.
vec2 warpSwirlSigmoid(vec2 texPos, vec4 noiseWithDerivatives, float time, float params[MAX_WARP_PARAMS]) {

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
    vec2 center = texPos + radiusScale * derivatives;

    // Calculate distance and angle from the center for the swirling effect
    vec2 toCenter = texPos - center;
    float distance = length(toCenter);
    float angle = atan(toCenter.y, toCenter.x);

    // Safe normalization of distance to avoid division by zero
    float safeRadiusScale = radiusScale + 0.0001; // Adding a tiny value to avoid zero
    float normalizedDistance = distance / safeRadiusScale;

    // Use the sigmoid function directly with correctly adjusted parameters
    float swirlIntensity = sigmoid(normalizedDistance, steepness, isolationMidpoint);

    float newAngle = angle + angleScale * swirlIntensity;

    // Calculate new texture coordinates
    vec2 newPos = center + normalizedDistance * radiusScale * vec2(cos(newAngle), sin(newAngle));
  
    return newPos - texPos;   
}

// Applies a dynamic swirling and warping effect to texture coordinates based on controlled feedback mechanisms.
//
// This function combines several transformation techniques to modify texture coordinates dynamically, focusing on creating
// complex visual effects. It utilizes sigmoid functions to apply non-linear transformations to the swirling intensity and 
// error handling, ensuring smooth transitions and complex patterns. The texture manipulation is influenced by noise and its 
// derivatives, which determine the center of the swirl and its intensity, thereby enriching the visual complexity.
//
// The function enhances the swirling effect by incorporating an additional noise function to randomly introduce errors, 
// adding complexity and reducing uniformity in the visual output.
//
// Parameters:
// - texture: The input texture sampler for fetching the color data.
// - texPos: The original texture coordinates.
// - newColor: A vec4 color that could potentially be used for blending or masking effects (not utilized in this specific function).
// - noiseWithDerivatives: A vec4 where the x component represents the noise value used for error adjustment, and yz components 
//   are the spatial derivatives used to determine the dynamic swirling center.
// - time: Current time or frame number, used to add a temporal variation to the noise calculations for error adjustments.
// - params: An array of floating-point values defining various parameters for the effect:
//   [0]: radiusScale - Scales the radius around which texture coordinates are swirled.
//   [1]: angleScale - Determines the angular displacement magnitude in the swirl effect.
//   [2]: isolation - Adjusts the steepness of the sigmoid function for swirl intensity, effectively isolating the effect to certain areas.
//   [3]: isolationMidpoint - Midpoint for the sigmoid function controlling swirl isolation.
//   [4]: errorScale - Scales the texture coordinates for the noise function, influencing the pattern of the error adjustments.
//   [5]: errorThreshold - Sets the threshold for when the error effect starts to apply, determining its visibility based on noise.
//   [6]: errorMidpoint - Midpoint for the sigmoid function controlling the smooth transition of the error effect.
//   [7]: errorStrength - Magnifies the impact of the error on the angular displacement.
//   [8]: errorSpeed - Modifies the speed at which the error pattern evolves over time.
//
// Returns:
// - vec2: The new texture coordinates after applying the swirling and warping effects.

vec2 warpSwirlSigmoidDistorted(vec2 texPos, vec4 noiseWithDerivatives, float time, float params[MAX_WARP_PARAMS]) {
 
    float radiusScale = params[0];
    float angleScale  = params[1];
    float isolation   = params[2] * 20.0;
    float isolationMidpoint = params[3];
    float errorScale = 1.0 + params[4] * 99.0; 
    float errorThreshold = params[5];
    float errorMidpoint = params[6];
    float errorStrength = params[7];
    float errorSpeed = params[8];  

    float noiseValue = noiseWithDerivatives.x;
    vec2 derivatives = noiseWithDerivatives.yz;

    vec2 center = texPos + radiusScale * derivatives;
    vec2 toCenter = texPos - center;
    float distance = length(toCenter);
    float angle = atan(toCenter.y, toCenter.x);

    float safeRadiusScale = radiusScale + 0.0001;
    float normalizedDistance = distance / safeRadiusScale;

    float swirlIntensity = sigmoid(normalizedDistance, isolation, isolationMidpoint);
    float newAngle = angle + angleScale * swirlIntensity;

    // Adjust for error using noise
    vec3 errorNoisePos = vec3(texPos * errorScale, time * errorSpeed + 37.0);  // Add a constant for randomness
    float errorNoise = Perlin3D_Std(errorNoisePos);
    float errorValue = (errorNoise + 1.0) * 0.5;

    // Smooth transition for error effect
    float errorEffect = sigmoid(errorValue, 10.0 * (1.0 / errorThreshold), errorMidpoint);  // Steep transition near the threshold
    float errorAngleAdjustment = errorEffect * errorNoise * errorStrength;

    newAngle += errorAngleAdjustment;

    vec2 newPos = center + normalizedDistance * radiusScale * vec2(cos(newAngle), sin(newAngle));

    return newPos - texPos;   
}

// Modifies texture coordinates using noise and derivatives to create fractal-like patterns in feedback effects.
//
// This function duplicates texture elements around centers calculated from noise values and their derivatives,
// facilitating the generation of complex, evolving patterns. These transformations are enhanced through parameters
// controlling duplication scale, influence radius, non-linearity of transformations, and dynamic rotation effects,
// both static and time-modulated. 
//
// Parameters:
// - texPos: Original texture coordinates.
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

vec2 warpInfiniteMirror(vec2 texPos, vec4 noiseWithDerivatives, float time, float params[MAX_WARP_PARAMS]) {
    
    float duplicationScale = params[0] * 4.0; // Scaled duplication scale
    float influenceRadius = params[1];
    float nonLinearity = params[2] * 10.0; // Scaled non-linearity
    float baseRotationIntensity = params[3] * 2.0; // Base intensity of the rotation
    float timeModulationIntensity = params[4]; // Time-dependent modulation intensity
    float frequency = params[5] * 10.0; // Scaled frequency of the time-based modulation

    float noiseValue = noiseWithDerivatives.x;
    vec2 derivatives = noiseWithDerivatives.yz;

    vec2 center = texPos + duplicationScale * noiseValue * normalize(derivatives);
    vec2 displacement = texPos - center;

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
    vec2 rotatedPos = center + rotationMatrix * (texPos - center);

    // Calculate new texture coordinates
    vec2 newPos = mix(texPos, 2.0 * rotatedPos - center, influence);

    return newPos - texPos;   
}

// This is just a playground function for developing new effects. It can be used to test new ideas and techniques.
// NOTE: texPos is the texture coordinates, noiseWithDerivatives is a vec4 containing the noise value and its derivatives,
// and param1, param2, param3, and param4 are user-controllable parameters that can be used in the function, with a range of [0, 1].
vec2 warpTest(vec2 texPos, vec4 noiseWithDerivatives, float time, float params[MAX_WARP_PARAMS]) {

    float displacementScale = params[0] * 0.05;
    float falloffRate = params[1] * 10.0;  // New parameter to control the falloff rate
    float noiseValue = noiseWithDerivatives.x;
    vec2 derivatives = noiseWithDerivatives.yz;

    // Smooth the derivatives to avoid sharp changes
    vec2 smoothedDerivatives = normalize(derivatives) * smoothstep(0.0, 1.0, length(derivatives));

    // Implementing falloff based on the noise value
    float falloff = exp(-falloffRate * abs(noiseValue));

    // Calculate displacement with moderated influence of derivatives and apply falloff
    return displacementScale * noiseValue * smoothedDerivatives * falloff;

}
