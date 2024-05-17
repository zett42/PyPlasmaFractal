#include "transforms.glsl"

// Computes two independent fractal noise values and return vec2
vec2 fractalNoise_Double_<NOISE_FUNC>(
        vec2 position, int octaves, float gain, float timeScaleFactor,
        float positionScaleFactor, float rotationAngleIncrement, float timeOffsetIncrement, float time) {

    float amplitude = 1.0;        // Initial amplitude for first octave
    float totalAmplitude = 0.0;   // Total amplitude for normalizing final noise values
    vec2 grayscale = vec2(0.0);   // Accumulated grayscale value from noise for x and y
    float currentAngle = 0.0;     // Current angle for incremental rotation
    float timeOffset = 0.0;       // Current time offset for noise variation
    float timeOffsetY = 123.0;    // Different time offset for y noise to create variation (value choosen arbitrarily)

    // Iterate over each octave to accumulate noise contributions
    for(int i = 0; i < octaves; i++) {

        // Adjust time and position scaling per octave
        float timeScalePerOctave = pow(timeScaleFactor, float(i));
        float positionScalePerOctave = pow(positionScaleFactor, float(i));

        // Apply rotation
        currentAngle += rotationAngleIncrement;
        vec2 rotatedPosition = rotate2D(position, currentAngle);

        // Calculate effective time including time scaling and offset
        float effectiveTimeX = time * timeScalePerOctave + timeOffset;
        float effectiveTimeY = effectiveTimeX + timeOffsetY; // Apply offset to "seed" noise value for y differently

        // Create final position vector for noise
        vec3 posX = vec3(rotatedPosition * positionScalePerOctave, effectiveTimeX);
  
        // Compute noise value for x and y
        vec2 noiseValue = <NOISE_FUNC>_Double(posX, effectiveTimeY);

        // Accumulate
        grayscale += noiseValue * amplitude; // Weight noise by current amplitude
        totalAmplitude += amplitude;  // Accumulate total amplitude for normalization
        amplitude *= gain;  // Decrease amplitude for next octave
        timeOffset += timeOffsetIncrement;  // Increment time offset
    }

    return grayscale / totalAmplitude; // Return normalized noise values
}
