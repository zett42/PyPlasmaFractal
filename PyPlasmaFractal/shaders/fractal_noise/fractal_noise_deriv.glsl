#include "common/transforms.glsl"

// Function to compute fractal noise and its derivatives
vec4 fractalNoise_Deriv_<NOISE_FUNC>(vec2 position, int octaves, float gain, float timeScaleFactor,
                                     float positionScaleFactor, float rotationAngleIncrement, float timeOffsetIncrement, float time) {

    float amplitude = 1.0;        // Initial amplitude for first octave
    float totalAmplitude = 0.0;   // Total amplitude for normalizing final noise value
    float grayscale = 0.0;        // Accumulated grayscale value from noise
    vec2 totalDerivative = vec2(0.0); // Total derivative accumulation
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

        // Retrieve noise value and its derivatives from noise function (template parameter)
        vec4 noiseAndDeriv = <NOISE_FUNC>_Deriv(pos);

        // Accumulate grayscale, x and y derivatives
        grayscale += noiseAndDeriv.x * amplitude; // Weight noise by current amplitude
        totalDerivative += noiseAndDeriv.yz * amplitude * positionScalePerOctave; // Accumulate weighted derivatives scaled by position scale

        totalAmplitude += amplitude;  // Accumulate total amplitude for normalization
        amplitude *= gain;  // Decrease amplitude for next octave
        timeOffset += timeOffsetIncrement;  // Increment time offset
    }

    // Normalize the accumulated noise and derivatives
    grayscale /= totalAmplitude;
    totalDerivative /= totalAmplitude;

    // Return the noise value and the derivatives
    return vec4(grayscale, totalDerivative.x, totalDerivative.y, 0.0); // The z derivative is set to 0.0 as it's not computed here
}
