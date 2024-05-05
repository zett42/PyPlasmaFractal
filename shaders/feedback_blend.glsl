vec4 blendLinear(vec4 prevColor, vec4 currentColor, float alpha) {
    return mix(prevColor, currentColor, alpha);
}

vec4 blendAdditive(vec4 prevColor, vec4 currentColor, float alpha) {
    return prevColor * (1.0 - alpha) + currentColor;
}