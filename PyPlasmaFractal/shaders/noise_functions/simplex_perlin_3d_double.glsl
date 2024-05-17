//  Simplex Perlin Noise 3D
//  Computes two noise values for different Z planes
//  Return value range of -1.0->1.0

vec2 SimplexPerlin3D_Double(vec3 P, float P2z) {

    return vec2(
        SimplexPerlin3D_Std(P),
        SimplexPerlin3D_Std(P + vec3(0.0, 0.0, P2z))
    );
}
