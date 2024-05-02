// Function to apply sigmoid-based contrast to values between 0 and 1
float sigmoidContrast(float x, float contrastSteepness, float contrastMidpoint ) {
    return 1.0 / (1.0 + exp(-contrastSteepness * (x - contrastMidpoint)));
}
