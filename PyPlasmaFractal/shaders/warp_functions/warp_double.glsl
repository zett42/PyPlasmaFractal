//----------------------------------------------------------------------------------------------------------------------------------
// Warp functions for texture coordinates, based on a noise vector.
//----------------------------------------------------------------------------------------------------------------------------------

#include "common/math_constants.glsl"

/// Applies an offset to texture coordinates based on noise values.
/// 
/// This function directly modifies texture coordinates by adding an offset derived from noise values.
/// The noise values are scaled by a factor, allowing for controlled distortion of the texture coordinates.
/// 
/// @param tex_pos The original texture coordinates.
/// @param noise A vec2 containing noise values that dictate the direction and magnitude of the offset.
/// @param time Current time in seconds.
/// @param amplitude A scalar that scales the noise values to control the extent of the offset.
///
/// @return vec2 The offset to apply to the texture coordinates.

vec2 warp_offset(vec2 tex_pos, vec2 noise, float time, float amplitude) {
    return noise * amplitude / 20.0;
}

/// Modifies texture coordinates by applying a polar-based offset, influenced by noise.
/// 
/// This function takes initial texture coordinates and applies an offset derived from noise values,
/// translated into polar coordinates. It uses the noise to determine the angle and radius of the
/// offset, effectively allowing the texture to warp in a circular pattern. The angle and radius scales
/// are used to control the extent of warping, which helps in creating more dynamic and varied visual effects.
/// The function is particularly useful in situations where a simple, yet visually interesting, distortion
/// is desired, such as in procedural texture generation or distortion effects in graphical applications.
/// 
/// @param tex_pos The original texture coordinates.
/// @param noise A vec2 representing noise input, where noise.x affects the angular displacement and noise.y
///   affects the radial displacement.
/// @param time Current time in seconds.
/// @param radius_scale A float that scales the radial component of the offset. Affects how far from the original
///   position the warp can move, scaled by the noise's radial value.
/// @param angle_scale A float that scales the angular component of the distortion. This determines the rotational
///   influence of the noise's angular value.
///
/// @return vec2 The offset to apply to the texture coordinates.

vec2 warp_polar(vec2 tex_pos, vec2 noise, float time, float radius_scale, float angle_scale) {

    // Normalize noise.x values around zero and limit angle variations
    float angle = 2.0 * M_PI * noise.x * angle_scale * 10.0; 

    // Convert noise.y from -1..1 to 0..1 for the radius
    float radius = (noise.y + 1.0) / 2.0 * radius_scale / 30.0;

    // Calculate offset using polar coordinates (angle and radius)
    return vec2(cos(angle), sin(angle)) * radius;
}
