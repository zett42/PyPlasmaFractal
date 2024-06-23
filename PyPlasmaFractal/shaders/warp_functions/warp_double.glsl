//----------------------------------------------------------------------------------------------------------------------------------
// Warp functions for texture coordinates, based on a noise vector.
// The functions in this file are used as template functions, so they must have the same number and kind of arguments.
//----------------------------------------------------------------------------------------------------------------------------------

#include "common/math_constants.glsl"

// Applies an offset to texture coordinates based on noise values.
//
// This function directly modifies texture coordinates by adding an offset derived from noise values.
// The noise values are scaled by a factor, allowing for controlled distortion of the texture coordinates.
//
// Parameters:
// - texPos: The original texture coordinates.
// - noise: A vec2 containing noise values that dictate the direction and magnitude of the offset.
// - time: Current time in seconds.
// - amplitude: A scalar that scales the noise values to control the extent of the offset.
//
// Returns:
// - vec2: The offset to apply to the texture coordinates

vec2 warpOffset(vec2 texPos, vec2 noise, float time, float params[MAX_WARP_PARAMS]) {
    
    float amplitude = params[0];

    return noise * amplitude / 20.0;
}


// Modifies texture coordinates by applying a polar-based offset, influenced by noise.
//
// This function takes initial texture coordinates and applies an offset derived from noise values,
// translated into polar coordinates. It uses the noise to determine the angle and radius of the
// offset, effectively allowing the texture to warp in a circular pattern. The angle and radius scales
// are used to control the extent of warping, which helps in creating more dynamic and varied visual effects.
// The function is particularly useful in situations where a simple, yet visually interesting, distortion
// is desired, such as in procedural texture generation or distortion effects in graphical applications.
//
// Parameters:
// - texPos: The original texture coordinates.
// - noise: A vec2 representing noise input, where noise.x affects the angular displacement and noise.y
//   affects the radial displacement.
// - time: Current time in seconds.
// - radiusScale: A float that scales the radial component of the offset. Affects how far from the original
//   position the warp can move, scaled by the noise's radial value.
// - angleScale: A float that scales the angular component of the distortion. This determines the rotational
//   influence of the noise's angular value.
//
// Returns:
// - vec2: The offset to apply to the texture coordinates

vec2 warpPolar(vec2 texPos, vec2 noise, float time, float params[MAX_WARP_PARAMS]) {

    float radiusScale = params[0];
    float angleScale  = params[1];

    // Normalize noise.x values around zero and limit angle variations
    float angle = 2.0 * M_PI * noise.x * angleScale * 10.0; 

    // Convert noise.y from -1..1 to 0..1 for the radius
    float radius = (noise.y + 1.0) / 2.0 * radiusScale / 30.0;

    // Calculate offset using polar coordinates (angle and radius)
    return vec2(cos(angle), sin(angle)) * radius;
}
