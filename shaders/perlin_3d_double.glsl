// This is a modified version of the original code from Brian Sharpe's Wombat library: 
// https://github.com/BrianSharpe/Wombat/blob/master/Perlin3D.glsl
//
// Modifications include:
// - Calculating two noise values for different Z planes

//
//  Perlin Noise 3D
//  Computes two noise values for different Z planes
//  Return value range of -1.0->1.0
//
vec2 Perlin3D_Double( vec3 P, float P2z )
{
    vec3 Pi = floor(P);
    vec3 Pf = P - Pi;
    vec3 Pf_min1 = Pf - 1.0;

    Pi.xyz = Pi.xyz - floor(Pi.xyz * (1.0 / 69.0)) * 69.0;
    vec3 Pi_inc1 = step(Pi, vec3(69.0 - 1.5)) * (Pi + 1.0);

    vec4 Pt = vec4(Pi.xy, Pi_inc1.xy) + vec2(50.0, 161.0).xyxy;
    Pt *= Pt;
    Pt = Pt.xzxz * Pt.yyww;
    const vec3 SOMELARGEFLOATS = vec3(635.298681, 682.357502, 668.926525);
    const vec3 ZINC = vec3(48.500388, 65.294118, 63.934599);

    vec3 lowz_mod = vec3(1.0 / (SOMELARGEFLOATS + Pi.zzz * ZINC));
    vec3 highz_mod = vec3(1.0 / (SOMELARGEFLOATS + Pi_inc1.zzz * ZINC));
    vec4 hashx0 = fract(Pt * lowz_mod.xxxx);
    vec4 hashx1 = fract(Pt * highz_mod.xxxx);
    vec4 hashy0 = fract(Pt * lowz_mod.yyyy);
    vec4 hashy1 = fract(Pt * highz_mod.yyyy);
    vec4 hashz0 = fract(Pt * lowz_mod.zzzz);
    vec4 hashz1 = fract(Pt * highz_mod.zzzz);

    vec4 grad_x0 = hashx0 - 0.49999;
    vec4 grad_y0 = hashy0 - 0.49999;
    vec4 grad_z0 = hashz0 - 0.49999;
    vec4 grad_x1 = hashx1 - 0.49999;
    vec4 grad_y1 = hashy1 - 0.49999;
    vec4 grad_z1 = hashz1 - 0.49999;
    vec4 grad_results_0 = inversesqrt(grad_x0 * grad_x0 + grad_y0 * grad_y0 + grad_z0 * grad_z0) * (vec2(Pf.x, Pf_min1.x).xyxy * grad_x0 + vec2(Pf.y, Pf_min1.y).xxyy * grad_y0 + Pf.zzzz * grad_z0);
    vec4 grad_results_1 = inversesqrt(grad_x1 * grad_x1 + grad_y1 * grad_y1 + grad_z1 * grad_z1) * (vec2(Pf.x, Pf_min1.x).xyxy * grad_x1 + vec2(Pf.y, Pf_min1.y).xxyy * grad_y1 + Pf_min1.zzzz * grad_z1);

    vec3 blend = Pf * Pf * Pf * (Pf * (Pf * 6.0 - 15.0) + 10.0);
    vec4 res0 = mix(grad_results_0, grad_results_1, blend.z);
    vec4 blend2 = vec4(blend.xy, vec2(1.0 - blend.xy));
    float final1 = dot(res0, blend2.zxzx * blend2.wwyy);

    // Recalculate for P2z
    vec3 P2 = vec3(P.xy, P2z);
    vec3 Pi2 = floor(P2);
    vec3 Pf2 = P2 - Pi2;
    vec3 Pf2_min1 = Pf2 - 1.0;
    Pi2.z = Pi2.z - floor(Pi2.z * (1.0 / 69.0)) * 69.0;
    vec3 Pi2_inc1 = step(Pi2.zzz, vec3(69.0 - 1.5)) * (Pi2.zzz + 1.0);
    vec3 lowz_mod2 = vec3(1.0 / (SOMELARGEFLOATS + Pi2.zzz * ZINC));
    vec3 highz_mod2 = vec3(1.0 / (SOMELARGEFLOATS + Pi2_inc1.zzz * ZINC));
    vec4 hashz02 = fract(Pt * lowz_mod2.zzzz);
    vec4 hashz12 = fract(Pt * highz_mod2.zzzz);
    vec4 grad_z02 = hashz02 - 0.49999;
    vec4 grad_z12 = hashz12 - 0.49999;
    vec4 grad_results_02 = inversesqrt(grad_z02 * grad_z02 + grad_z02 * grad_z02 + grad_z02 * grad_z02) * (Pf2.zzzz * grad_z02);
    vec4 grad_results_12 = inversesqrt(grad_z12 * grad_z12 + grad_z12 * grad_z12 + grad_z12 * grad_z12) * (Pf2_min1.zzzz * grad_z12);
    vec4 res02 = mix(grad_results_02, grad_results_12, blend.z);
    float final2 = dot(res02, blend2.zxzx * blend2.wwyy);

    return vec2(final1, final2) * 1.1547005383792515290182975610039;
}
