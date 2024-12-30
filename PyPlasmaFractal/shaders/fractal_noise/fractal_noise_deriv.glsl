#include "common/transforms.glsl"

// Function to compute fractal noise and its derivatives
vec4 fractal_noise_deriv_<NOISE_FUNC>(vec2 position, int octaves, float gain, float time_scale_factor,
                                      float position_scale_factor, float rotation_angle_increment, float time_offset_increment, float time) {

    float amplitude = 1.0;        // Initial amplitude for first octave
    float total_amplitude = 0.0;   // Total amplitude for normalizing final noise value
    float grayscale = 0.0;        // Accumulated grayscale value from noise
    vec2 total_derivative = vec2(0.0); // Total derivative accumulation
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

        // Retrieve noise value and its derivatives from noise function (template parameter)
        vec4 noise_and_deriv = <NOISE_FUNC>_Deriv(pos);

        // Accumulate grayscale, x and y derivatives
        grayscale += noise_and_deriv.x * amplitude; // Weight noise by current amplitude
        total_derivative += noise_and_deriv.yz * amplitude * position_scale_per_octave; // Accumulate weighted derivatives scaled by position scale

        total_amplitude += amplitude;  // Accumulate total amplitude for normalization
        amplitude *= gain;  // Decrease amplitude for next octave
        time_offset += time_offset_increment;  // Increment time offset
    }

    // Normalize the accumulated noise and derivatives
    grayscale /= total_amplitude;
    total_derivative /= total_amplitude;

    // Return the noise value and the derivatives
    return vec4(grayscale, total_derivative.x, total_derivative.y, 0.0); // The z derivative is set to 0.0 as it's not computed here
}
