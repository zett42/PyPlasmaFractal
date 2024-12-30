//----------------------------------------------------------------------------------------------------------------------------------
// Warp functions for texture coordinates, based on a noise vector.
//----------------------------------------------------------------------------------------------------------------------------------

#include "common/math_constants.glsl"
#include "common/transforms.glsl"

/// Applies a simple offset to texture coordinates based on noise derivatives.
/// 
/// This function directly modifies texture coordinates by adding an offset derived from the derivatives of noise values.
/// The noise derivatives are scaled by a factor, allowing for controlled distortion of the texture coordinates.
///
/// @param tex_pos The original texture coordinates.
/// @param noise_with_deriv A vec4 containing the noise value and its derivatives in the xy-plane.
/// @param time Current time or frame number, used to animate or vary the effect over time (not used in this specific implementation).
/// @param amplitude A scalar that scales the noise derivatives to control the extent of the offset.
///
/// @return vec2 The offset to apply to the texture coordinates.

vec2 warp_offset_deriv(vec2 tex_pos, vec4 noise_with_deriv, float time, float amplitude) {

    vec2 derivatives = noise_with_deriv.yz;

    // Calculate the offset for the texture coordinates
    vec2 offset = amplitude * derivatives;

    return offset;    
}

/// Applies a swirling effect to texture coordinates based on noise and its derivatives.
///
/// This function modifies texture coordinates by introducing a swirling motion centered dynamically
/// using the derivatives of noise values. By converting the Cartesian coordinates into polar coordinates
/// around a noise-derived center, it applies a radial and angular distortion. This method effectively 
/// reduces linear artifacts by swirling points around a varying center, thus avoiding the grid-like 
/// effects commonly associated with direct Cartesian noise applications.
///
/// @param tex_pos The original texture coordinates.
/// @param noise_with_deriv A vec4 containing the noise value and its derivatives. The x component 
///   is used for adjusting the swirl angleScale, and yz components determine the dynamic center offset.
/// @param radius_scale A scalar factor that adjusts the dynamic center based on noise derivatives.
/// @param angle_scale Controls the angleScale of the swirling effect, influencing the angular distortion.
/// @param isolation Represents the isolation of the effect, controlling how localized the effect appears.
///
/// @return vec2 The new texture coordinates after applying the swirling effect.

vec2 warp_swirl(vec2 tex_pos, vec4 noise_with_deriv, float time, float radius_scale, float angle_scale, float isolation) {

    // Scale the isolation input from [0, 1] to a more effective range [0, 10]
    float scaled_isolation_factor = 10.0 * isolation; // Amplify the input value

    // Extract noise value and derivatives from the input
    float noise_value = noise_with_deriv.x;
    vec2 derivatives = noise_with_deriv.yz;

    // Determine a dynamic center for the swirl based on noise and its derivatives
    vec2 center = tex_pos + radius_scale * derivatives;

    // Calculate distance and angle from the center for the swirling effect
    vec2 to_center = tex_pos - center;
    float distance = length(to_center);
    float angle = atan(to_center.y, to_center.x);

    // Safe normalization of distance to avoid division by zero
    float safe_radius_scale = radius_scale + 0.0001; // Adding a tiny value to avoid zero
    float normalized_distance = distance / safe_radius_scale;

    // Modify swirl decrease with distance, incorporating the scaled isolation factor
    float new_angle = angle + angle_scale * exp(-scaled_isolation_factor * normalized_distance);

    // Calculate new texture coordinates
    vec2 new_pos = center + normalized_distance * radius_scale * vec2(cos(new_angle), sin(new_angle));

    return new_pos - tex_pos;   
}

/// Transforms a position vector using noise-induced warping for procedural animation effects.
///
/// This function applies a swirling distortion effect to a 2D position based on noise values and a set of parameters. 
/// It calculates a dynamic swirling center influenced by noise derivatives, scales the influence on distance,
/// and applies a sigmoid function to create a soft transition effect within a controlled range.
///
/// @param tex_pos The original 2D position vector to be transformed.
/// @param noise_with_deriv A 4D vector containing a noise value and its derivatives in the xy-plane.
/// @param time The current time or frame, used to animate or vary the effect over time (not used in this specific implementation).
/// @param radius_scale Controls the scale of the radius from the center of the swirl.
/// @param angle_scale Controls the scaling factor for the angle of rotation around the swirl center.
/// @param isolation Represents the isolation of the effect, controlling how localized the effect appears.
/// @param isolation_midpoint The midpoint for scaling the isolation effect, adjusting the center point of the sigmoid function.
///
/// @return vec2 The new texture coordinates after applying the swirling effect.

vec2 warp_swirl_sigmoid(vec2 tex_pos, vec4 noise_with_deriv, float time, float radius_scale, float angle_scale, float isolation, float isolation_midpoint) {

    // Scale the isolation input from [0, 1] to a more effective range [0, 10]
    float steepness = 20.0 * isolation; // Amplify the input value for steepness

    // Extract noise value and derivatives from the input
    float noise_value = noise_with_deriv.x;
    vec2 derivatives = noise_with_deriv.yz;

    // Determine a dynamic center for the swirl based on noise and its derivatives
    vec2 center = tex_pos + radius_scale * derivatives;

    // Calculate distance and angle from the center for the swirling effect
    vec2 to_center = tex_pos - center;
    float distance = length(to_center);
    float angle = atan(to_center.y, to_center.x);

    // Safe normalization of distance to avoid division by zero
    float safe_radius_scale = radius_scale + 0.0001; // Adding a tiny value to avoid zero
    float normalized_distance = distance / safe_radius_scale;

    // Use the sigmoid function directly with correctly adjusted parameters
    float swirl_intensity = sigmoid(normalized_distance, steepness, isolation_midpoint);

    float new_angle = angle + angle_scale * swirl_intensity;

    // Calculate new texture coordinates
    vec2 new_pos = center + normalized_distance * radius_scale * vec2(cos(new_angle), sin(new_angle));
  
    return new_pos - tex_pos;   
}

/// Applies a dynamic swirling and warping effect to texture coordinates based on controlled feedback mechanisms.
///
/// This function combines several transformation techniques to modify texture coordinates dynamically, focusing on creating
/// complex visual effects. It utilizes sigmoid functions to apply non-linear transformations to the swirling intensity and 
/// error handling, ensuring smooth transitions and complex patterns. The texture manipulation is influenced by noise and its 
/// derivatives, which determine the center of the swirl and its intensity, thereby enriching the visual complexity.
///
/// The function enhances the swirling effect by incorporating an additional noise function to randomly introduce errors, 
/// adding complexity and reducing uniformity in the visual output.
///
/// @param tex_pos The original texture coordinates.
/// @param noise_with_deriv A vec4 where the x component represents the noise value used for error adjustment, and yz components 
///   are the spatial derivatives used to determine the dynamic swirling center.
/// @param time Current time or frame number, used to add a temporal variation to the noise calculations for error adjustments.
/// @param radius_scale Scales the radius around which texture coordinates are swirled.
/// @param angle_scale Determines the angular displacement magnitude in the swirl effect.
/// @param isolation Adjusts the steepness of the sigmoid function for swirl intensity, effectively isolating the effect to certain areas.
/// @param isolation_midpoint Midpoint for the sigmoid function controlling swirl isolation.
/// @param error_scale Scales the texture coordinates for the noise function, influencing the pattern of the error adjustments.
/// @param error_threshold Sets the threshold for when the error effect starts to apply, determining its visibility based on noise.
/// @param error_midpoint Midpoint for the sigmoid function controlling the smooth transition of the error effect.
/// @param error_strength Magnifies the impact of the error on the angular displacement.
/// @param error_speed Modifies the speed at which the error pattern evolves over time.
///
/// @return vec2 The new texture coordinates after applying the swirling and warping effects.

vec2 warp_swirl_sigmoid_distorted(vec2 tex_pos, vec4 noise_with_deriv, float time, float radius_scale, float angle_scale, float isolation, float isolation_midpoint, float error_scale, float error_threshold, float error_midpoint, float error_strength, float error_speed) {
 
    isolation = isolation * 20.0;
    error_scale = 1.0 + error_scale * 99.0; 

    float noise_value = noise_with_deriv.x;
    vec2 derivatives = noise_with_deriv.yz;

    vec2 center = tex_pos + radius_scale * derivatives;
    vec2 to_center = tex_pos - center;
    float distance = length(to_center);
    float angle = atan(to_center.y, to_center.x);

    float safe_radius_scale = radius_scale + 0.0001;
    float normalized_distance = distance / safe_radius_scale;

    float swirl_intensity = sigmoid(normalized_distance, isolation, isolation_midpoint);
    float new_angle = angle + angle_scale * swirl_intensity;

    // Adjust for error using noise
    vec3 error_noise_pos = vec3(tex_pos * error_scale, time * error_speed + 37.0);  // Add a constant for randomness
    float error_noise = Perlin3D_Std(error_noise_pos);
    float error_value = (error_noise + 1.0) * 0.5;

    // Smooth transition for error effect
    float error_effect = sigmoid(error_value, 10.0 * (1.0 / error_threshold), error_midpoint);  // Steep transition near the threshold
    float error_angle_adjustment = error_effect * error_noise * error_strength;

    new_angle += error_angle_adjustment;

    vec2 new_pos = center + normalized_distance * radius_scale * vec2(cos(new_angle), sin(new_angle));

    return new_pos - tex_pos;   
}

/// Modifies texture coordinates using noise and derivatives to create fractal-like patterns in feedback effects.
///
/// This function duplicates texture elements around centers calculated from noise values and their derivatives,
/// facilitating the generation of complex, evolving patterns. These transformations are enhanced through parameters
/// controlling duplication scale, influence radius, non-linearity of transformations, and dynamic rotation effects,
/// both static and time-modulated. 
///
/// @param tex_pos Original texture coordinates.
/// @param noise_with_deriv A vec4 containing the noise value (x) and its derivatives (yz), influencing the duplication scale
///   and the dynamic centers.
/// @param time Current time or frame number, used to add a temporal variation to the noise calculations for error adjustments.
/// @param duplication_scale Scales duplication, affecting spatial distribution.
/// @param influence_radius Defines the focus area of the effect.
/// @param non_linearity Adjusts the progression of the influence curve.
/// @param base_rotation_intensity Base rotation intensity around dynamic centers.
/// @param time_modulation_intensity Modulates rotation intensity over time.
/// @param frequency Controls the oscillation speed of time-based rotation.
/// @return vec2 New texture coordinates after applying duplication and dynamic transformations.

vec2 warp_infinite_mirror(vec2 tex_pos, vec4 noise_with_deriv, float time, float duplication_scale, float influence_radius, float non_linearity, float base_rotation_intensity, float time_modulation_intensity, float frequency) {
    
    duplication_scale = duplication_scale * 4.0; // Scaled duplication scale
    non_linearity = non_linearity * 10.0; // Scaled non-linearity
    base_rotation_intensity = base_rotation_intensity * 2.0; // Base intensity of the rotation
    frequency = frequency * 10.0; // Scaled frequency of the time-based modulation

    float noise_value = noise_with_deriv.x;
    vec2 derivatives = noise_with_deriv.yz;

    vec2 center = tex_pos + duplication_scale * noise_value * normalize(derivatives);
    vec2 displacement = tex_pos - center;

    // Calculate normalized distance and influence
    float normalized_distance = length(displacement) / influence_radius;
    float falloff_power = mix(0.1, 2.0, non_linearity);
    float influence = 1.0 - pow(clamp(normalized_distance, 0.0, 1.0), falloff_power);

    // Calculate rotation with time modulation
    float time_modulation = sin(time * frequency) * time_modulation_intensity * M_PI * 2;
    float rotation_angle = time_modulation + base_rotation_intensity;
    mat2 rotation_matrix = mat2(cos(rotation_angle), -sin(rotation_angle),
                               sin(rotation_angle), cos(rotation_angle));

    // Apply rotation around the center
    vec2 rotated_pos = center + rotation_matrix * (tex_pos - center);

    // Calculate new texture coordinates
    vec2 new_pos = mix(tex_pos, 2.0 * rotated_pos - center, influence);

    return new_pos - tex_pos;   
}
