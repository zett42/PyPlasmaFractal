// Function to rotate a 2D vector by a given angle in radians
vec2 rotate2D(vec2 v, float angle) {
    float cosA = cos(angle);
    float sinA = sin(angle);
    return vec2(v.x * cosA - v.y * sinA, v.x * sinA + v.y * cosA);
}

float sigmoid(float value, float steepness, float midpoint) {

    return 1.0 / (1.0 + exp(-steepness * (value - midpoint)));
}

vec2 adjustVectorUsingSigmoid(vec2 p, float steepness, float midpoint) {

    float adjustedLength = length(p) / 1.4142135623731; // Normalize length to max 1
    float scale = sigmoid(adjustedLength, steepness, midpoint);
    return normalize(p) * scale;
}
