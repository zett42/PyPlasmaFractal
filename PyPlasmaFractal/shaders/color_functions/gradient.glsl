#include "noise_functions/simplex_perlin_3d_std.glsl"
#apply_template "fractal_noise/fractal_noise_single.glsl", NOISE_FUNC = simplex_perlin_3d

/// Maps a grayscale value to a color gradient between two colors.
/// 
/// @param grayscale The grayscale value (0.0 to 1.0).
/// @param start_color The color for the minimum grayscale value.
/// @param end_color The color for the maximum grayscale value.
/// @param gamma Adjusts the gradient interpolation curve.
///
/// @return The interpolated color.

vec4 colorize_gradient3(float grayscale, vec2 pos, float time, vec4 start_color, vec4 mid_color, vec4 end_color, float mid_position) {

    float t = smoothstep(0.0, mid_position, grayscale);
    float s = smoothstep(mid_position, 1.0, grayscale);
    return mix(
        mix(start_color, mid_color, t),
        mix(mid_color, end_color, s),
        s
    );
}

/// Maps a grayscale value to a color gradient between two colors with noise.
/// 
/// @param grayscale The grayscale value (0.0 to 1.0).
/// @param pos The position vector.
/// @param time The current time.
/// @param start_color The color for the minimum grayscale value.
/// @param end_color The color for the maximum grayscale value.
/// @param noise_octaves Number of noise octaves.
/// @param noise_gain Noise gain.
/// @param noise_time_scale_factor Time scale factor for noise.
/// @param noise_position_scale_factor Position scale factor for noise.
/// @param noise_rotation_angle_increment Rotation angle increment for noise.
/// @param noise_time_offset_increment Time offset increment for noise.
/// @param noise_scale Scale factor for noise.
/// @param gamma Adjusts the gradient interpolation curve.
///
/// @return The interpolated color with noise.

vec4 shift_hue(vec4 color, float hue_shift) {
    float angle = hue_shift * 6.28318530718; // 2 * PI
    float s = sin(angle);
    float c = cos(angle);
    mat3 hue_rotation = mat3(
        vec3(0.299, 0.587, 0.114) + vec3(0.701, -0.587, -0.114) * c + vec3(0.168, -0.330, 1.000) * s,
        vec3(0.299, 0.587, 0.114) + vec3(-0.299, 0.413, -0.114) * c + vec3(0.328, 0.035, -1.000) * s,
        vec3(0.299, 0.587, 0.114) + vec3(-0.300, -0.588, 0.886) * c + vec3(-0.497, 0.330, 0.000) * s
    );
    return vec4(hue_rotation * color.rgb, color.a);
}

vec4 colorize_gradient2_noise(
    float grayscale, vec2 pos, float time, vec4 start_color, vec4 end_color,
    float noise_scale, int noise_octaves, float noise_gain, float noise_time_scale_factor,
    float noise_position_scale_factor, float noise_rotation_angle_increment,
    float noise_time_offset_increment, float hue_shift_factor) {

    float noise_value = fractal_noise_single_simplex_perlin_3d(
        pos * noise_scale, noise_octaves, noise_gain, noise_time_scale_factor,
        noise_position_scale_factor, noise_rotation_angle_increment,
        noise_time_offset_increment, time);

    vec4 noisy_color = shift_hue(end_color, noise_value * hue_shift_factor);
    return mix(start_color, noisy_color, grayscale);
}

/// Maps a grayscale value to a color gradient between three colors with noise.
/// 
/// @param grayscale The grayscale value (0.0 to 1.0).
/// @param pos The position vector.
/// @param time The current time.
/// @param start_color The color for the minimum grayscale value.
/// @param end_color1 The first color for the maximum grayscale value.
/// @param end_color2 The second color for the maximum grayscale value.
/// @param end_color3 The third color for the maximum grayscale value.
/// @param noise_scale Scale factor for noise.
/// @param noise_octaves Number of noise octaves.
/// @param noise_gain Noise gain.
/// @param noise_time_scale_factor Time scale factor for noise.
/// @param noise_position_scale_factor Position scale factor for noise.
/// @param noise_rotation_angle_increment Rotation angle increment for noise.
/// @param noise_time_offset_increment Time offset increment for noise.
/// @param hue_shift_factor Factor to scale the hue shift based on noise value.
///
/// @return The interpolated color with noise.

vec4 colorize_gradient3_noise(

    float grayscale, vec2 pos, float time, vec4 start_color, vec4 end_color1, vec4 end_color2, vec4 end_color3,
    float noise_speed, float noise_scale, int noise_octaves, float noise_gain, float noise_time_scale_factor,
    float noise_position_scale_factor, float noise_rotation_angle_increment,
    float noise_time_offset_increment) {

    float noise_value = fractal_noise_single_simplex_perlin_3d(
        pos * noise_scale, noise_octaves, noise_gain, noise_time_scale_factor,
        noise_position_scale_factor, noise_rotation_angle_increment,
        noise_time_offset_increment, time * noise_speed);

    // Map noise_value from [-1, 1] to [0, 1]
    float mapped_noise_value = (noise_value + 1.0) * 0.5;

    float t1 = smoothstep(0.0, 0.5, mapped_noise_value);
    float t2 = smoothstep(0.5, 1.0, mapped_noise_value);

    vec4 mid_color = mix(end_color1, end_color2, t1);
    vec4 noisy_color = mix(mid_color, end_color3, t2);

    return mix(start_color, noisy_color, grayscale);
}

