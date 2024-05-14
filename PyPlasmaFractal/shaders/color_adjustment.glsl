// Function to apply sigmoid-based contrast to values between 0 and 1
float sigmoidContrast(float x, float contrastSteepness, float contrastMidpoint ) {
    return 1.0 / (1.0 + exp(-contrastSteepness * (x - contrastMidpoint)));
}

// Calculate the perceived luminance of a color
float luminance(vec3 color) {
    return dot(color.rgb, vec3(0.299, 0.587, 0.114));
}