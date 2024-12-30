//  Simplex Perlin Noise 3D
//  Computes two noise values for different Z planes
//  Return value range of -1.0->1.0

#include "noise_functions/simplex_perlin_3d_std.glsl"

vec2 simplex_perlin_3d_double(vec3 P, float P2z) {

    return vec2(
        simplex_perlin_3d_std(P),
        simplex_perlin_3d_std(P + vec3(0.0, 0.0, P2z))
    );
}
