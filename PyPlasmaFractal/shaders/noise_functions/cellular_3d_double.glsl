//  Cellular Noise 3D
//  Computes two noise values for different Z planes
//  Return value range of 0.0->1.0

#include "noise_functions/cellular_3d_std.glsl"

vec2 Cellular3D_Double(vec3 P, float P2z) {

    return vec2(
        Cellular3D_Std(P),
        Cellular3D_Std(P + vec3(0.0, 0.0, P2z))
    );
}
