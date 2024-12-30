#include "common/transforms.glsl"

// Computes two independent fractal noise values and return vec2
vec2 fractal_noise_double_<NOISE_FUNC>(
        vec2 position, int octaves, float gain, float time_scale_factor,
        float position_scale_factor, float rotation_angle_increment, float time_offset_increment, float time) {

    float amplitude = 1.0;        // Initial amplitude for first octave
    float total_amplitude = 0.0;   // Total amplitude for normalizing final noise values
    vec2 grayscale = vec2(0.0);   // Accumulated grayscale value from noise for x and y
    float current_angle = 0.0;     // Current angle for incremental rotation
    float time_offset = 0.0;       // Current time offset for noise variation
    float time_offset_y = 123.0;    // Different time offset for y noise to create variation (value choosen arbitrarily)

    // Iterate over each octave to accumulate noise contributions
    for(int i = 0; i < octaves; i++) {

        // Adjust time and position scaling per octave
        float time_scale_per_octave = pow(time_scale_factor, float(i));
        float position_scale_per_octave = pow(position_scale_factor, float(i));

        // Apply rotation
        current_angle += rotation_angle_increment;
        vec2 rotated_position = rotate2D(position, current_angle);

        // Calculate effective time including time scaling and offset
        float effective_time_x = time * time_scale_per_octave + time_offset;
        float effective_time_y = effective_time_x + time_offset_y; // Apply offset to "seed" noise value for y differently

        // Create final position vector for noise
        vec3 pos_x = vec3(rotated_position * position_scale_per_octave, effective_time_x);
  
        // Compute noise value for x and y
        vec2 noise_value = <NOISE_FUNC>_Double(pos_x, effective_time_y);

        // Accumulate
        grayscale += noise_value * amplitude; // Weight noise by current amplitude
        total_amplitude += amplitude;  // Accumulate total amplitude for normalization
        amplitude *= gain;  // Decrease amplitude for next octave
        time_offset += time_offset_increment;  // Increment time offset
    }

    return grayscale / total_amplitude; // Return normalized noise values
}
