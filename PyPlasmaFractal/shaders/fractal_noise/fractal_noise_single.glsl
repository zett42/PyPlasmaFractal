#include "common/transforms.glsl"

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

float fractal_noise_single_<NOISE_FUNC>(
        vec2 position, int octaves, float gain, float time_scale_factor, 
        float position_scale_factor, float rotation_angle_increment, float time_offset_increment, float time) {

    float amplitude = 1.0;        // Current amplitude for noise
    float total_amplitude = 0.0;   // Total amplitude for normalizing final noise value
    float grayscale = 0.0;        // Accumulated grayscale value from noise
    float current_angle = 0.0;     // Current angle for incremental rotation
    float time_offset = 0.0;       // Current time offset for noise variation

    // Iterate over each octave to accumulate noise contributions
    for(int i = 0; i < octaves; i++) {

        // Adjust time and position scaling per octave
        float time_scale_per_octave = pow(time_scale_factor, float(i)); 
        float position_scale_per_octave = pow(position_scale_factor, float(i)); 

        // Apply rotation
        current_angle += rotation_angle_increment;
        vec2 rotated_position = rotate2D(position, current_angle);

        // Calculate effective time including time scaling and offset
        float effective_time = time * time_scale_per_octave + time_offset;

        // Create final position vector for noise
        vec3 pos = vec3(rotated_position * position_scale_per_octave, effective_time); 

        // Retrieve noise value from noise function (template parameter)
        float noise_value = <NOISE_FUNC>_Std(pos);  

        // Accumulate
        grayscale += noise_value * amplitude; // Weight noise by current amplitude
        total_amplitude += amplitude;  // Accumulate total amplitude for normalization
        amplitude *= gain;  // Decrease amplitude for next octave
        time_offset += time_offset_increment;  // Increment time offset
    }

    return grayscale / total_amplitude; // Normalize noise value
}