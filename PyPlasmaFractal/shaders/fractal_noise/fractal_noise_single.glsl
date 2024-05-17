#include "transforms.glsl"

// Computes fractal noise based on multiple octaves of a noise function.
//
// This function generates a fractal noise pattern by accumulating noise values across several octaves,
// each with its own scaling and rotation adjustments. The noise is calculated using a templated noise function,
// `<NOISE_FUNC>`, which is a placeholder for any noise-generating function (e.g., Perlin, Simplex). This template
// parameter allows the function to be flexible and reusable with different noise algorithms.
// The noise values are normalized by the cumulative amplitude to ensure a consistent output range.
//
// Template Parameter:
// - <NOISE_FUNC>: A template parameter representing the specific noise function to be used. This noise function
//   must conform to the signature `float <NOISE_FUNC>_Std(vec3 pos)`, where `pos` includes both position (xy) and time (z)
//   information for generating the noise value.
//
// Parameters:
// - position: A vec2 specifying the initial position in the noise field.
// - octaves: An integer representing the number of octaves to process. More octaves result in more detail but increased computation.
// - gain: A float that controls the decay of amplitude with each octave, affecting the prominence of finer details.
// - timeScaleFactor: A float that adjusts the influence of time on the noise calculation per octave.
// - positionScaleFactor: A float that scales the position input for each octave, affecting the frequency of the noise pattern.
// - rotationAngleIncrement: A float specifying the rotation angle increment applied to the position per octave, adding rotational variance.
// - timeOffsetIncrement: A float that increments the time offset per octave, adding temporal variance to the noise.
// - time: A float representing the initial time value, useful for generating time-varying noise patterns.
//
// Returns:
// - float: The normalized grayscale noise value as a float, representing the combined effect of all octaves.

float fractalNoise_Single_<NOISE_FUNC>(
        vec2 position, int octaves, float gain, float timeScaleFactor, 
        float positionScaleFactor, float rotationAngleIncrement, float timeOffsetIncrement, float time) {

    float amplitude = 1.0;        // Current amplitude for noise
    float totalAmplitude = 0.0;   // Total amplitude for normalizing final noise value
    float grayscale = 0.0;        // Accumulated grayscale value from noise
    float currentAngle = 0.0;     // Current angle for incremental rotation
    float timeOffset = 0.0;       // Current time offset for noise variation

    // Iterate over each octave to accumulate noise contributions
    for(int i = 0; i < octaves; i++) {

        // Adjust time and position scaling per octave
        float timeScalePerOctave = pow(timeScaleFactor, float(i)); 
        float positionScalePerOctave = pow(positionScaleFactor, float(i)); 

        // Apply rotation
        currentAngle += rotationAngleIncrement;
        vec2 rotatedPosition = rotate2D(position, currentAngle);

        // Calculate effective time including time scaling and offset
        float effectiveTime = time * timeScalePerOctave + timeOffset;

        // Create final position vector for noise
        vec3 pos = vec3(rotatedPosition * positionScalePerOctave, effectiveTime); 

        // Retrieve noise value from noise function (template parameter)
        float noiseValue = <NOISE_FUNC>_Std(pos);  

        // Accumulate
        grayscale += noiseValue * amplitude; // Weight noise by current amplitude
        totalAmplitude += amplitude;  // Accumulate total amplitude for normalization
        amplitude *= gain;  // Decrease amplitude for next octave
        timeOffset += timeOffsetIncrement;  // Increment time offset
    }

    return grayscale / totalAmplitude; // Normalize noise value
}