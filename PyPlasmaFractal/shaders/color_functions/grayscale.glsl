/// Returns a grayscale color from a grayscale value.
///
/// @param grayscale The grayscale value (0.0 to 1.0).
///
/// @return The grayscale color.

vec4 colorize_grayscale(float grayscale) {

    return vec4(grayscale, grayscale, grayscale, 1.0);  
}
