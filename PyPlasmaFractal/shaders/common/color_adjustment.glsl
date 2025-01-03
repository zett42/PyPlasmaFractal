/// Function to apply sigmoid-based contrast to values between 0 and 1
///
/// @param x The value to apply contrast to
/// @param steepness The steepness of the sigmoid curve
/// @param midpoint The midpoint of the sigmoid curve
///
/// @return The contrast-adjusted value

float sigmoid_contrast(float x, float steepness, float midpoint ) {
    return 1.0 / (1.0 + exp(-steepness * (x - midpoint)));
}

/// Calculate the perceived luminance of a color
///
/// @param color The color to calculate the luminance of
///
/// @return The luminance of the color

float luminance(vec3 color) {
    return dot(color.rgb, vec3(0.299, 0.587, 0.114));
}

/// Convert RGB to HSV
///
/// @param c The RGB color to convert
///
/// @return The HSV color (x = hue, y = saturation, z = value)

vec3 rgb2hsv(vec3 c) {
    vec4 K = vec4(0.0, -1.0/3.0, 2.0/3.0, -1.0);
    vec4 p = mix(vec4(c.bg, K.wz), vec4(c.gb, K.xy), step(c.b, c.g));
    vec4 q = mix(vec4(p.xyw, c.r), vec4(c.r, p.yzx), step(p.x, c.r));
    float d = q.x - min(q.w, q.y);
    float e = 1.0e-10;
    return vec3(abs(q.z + (q.w - q.y) / (6.0 * d + e)), d / (q.x + e), q.x);
}

/// Convert HSV to RGB
///
/// @param c The HSV color to convert (x = hue, y = saturation, z = value)
///
/// @return The RGB color

vec3 hsv2rgb(vec3 c) {
    vec4 K = vec4(1.0, 2.0/3.0, 1.0/3.0, 3.0);
    vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www);
    return c.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
}

/// Adjust the hue and saturation of a color
///
/// @param color The RGBA color to adjust
/// @param hue_shift The amount to shift the hue by
/// @param saturation_inc The amount to increase the saturation by
///
/// @return The adjusted RGBA color (alpha is unchanged)

vec4 adjust_hue_saturation(vec4 color, float hue_shift, float saturation_inc) {
    vec3 hsv = rgb2hsv(color.rgb);
    hsv.x = fract(hsv.x + hue_shift); // Shift hue and wrap around
    hsv.y = clamp(hsv.y + saturation_inc, 0.0, 1.0); // Adjust saturation
    return vec4(hsv2rgb(hsv), color.a);
}

/// Shift the hue of a RGBA color
/// 
/// @param color The RGBA color to adjust
/// @param hue_shift The amount to shift the hue by
/// 
/// @return The adjusted RGBA color (alpha is unchanged)

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
