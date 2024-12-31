/// Maps a grayscale value to a color gradient between two colors.
/// 
/// @param grayscale The grayscale value (0.0 to 1.0).
/// @param start_color The color for the minimum grayscale value.
/// @param end_color The color for the maximum grayscale value.
/// @param gamma Adjusts the gradient interpolation curve.
///
/// @return The interpolated color.

vec4 colorize_gradient(float grayscale, vec4 start_color, vec4 mid_color, vec4 end_color, float mid_position) {
    float t = smoothstep(0.0, mid_position, grayscale);
    float s = smoothstep(mid_position, 1.0, grayscale);
    return mix(
        mix(start_color, mid_color, t),
        mix(mid_color, end_color, s),
        s
    );
}
