// Function to apply sigmoid-based contrast to values between 0 and 1
float sigmoid_contrast(float x, float steepness, float midpoint ) {
    return 1.0 / (1.0 + exp(-steepness * (x - midpoint)));
}

// Calculate the perceived luminance of a color
float luminance(vec3 color) {
    return dot(color.rgb, vec3(0.299, 0.587, 0.114));
}