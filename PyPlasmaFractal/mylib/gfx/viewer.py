import numpy as np
import glm

class Viewer:
    def __init__(self, position=(0.0, 0.0, 0.0), direction=(0.0, 0.0, -1.0), roll_angle=0.0):
        self._position = glm.vec3(position)
        self._direction = glm.normalize(glm.vec3(direction))
        self._roll = roll_angle
        
        # Calculate initial pitch and yaw from the direction vector
        self._pitch = glm.degrees(glm.asin(self._direction.y))
        self._yaw = glm.degrees(glm.atan(self._direction.x, -self._direction.z))
        
        self.update_camera_matrix()

    def update_camera_matrix(self):
        # Create the rotation matrices for pitch, yaw, and roll
        pitch_matrix = glm.rotate(glm.mat4(1.0), glm.radians(self._pitch), glm.vec3(1, 0, 0))
        yaw_matrix = glm.rotate(glm.mat4(1.0), glm.radians(self._yaw), glm.vec3(0, 1, 0))
        roll_matrix = glm.rotate(glm.mat4(1.0), glm.radians(self._roll), glm.vec3(0, 0, 1))

        # Combine the rotation matrices
        rotation_matrix = roll_matrix * yaw_matrix * pitch_matrix

        # Extract the direction vector from the combined rotation matrix
        self._direction = glm.vec3(rotation_matrix * glm.vec4(0.0, 0.0, -1.0, 1.0))

        # Create the translation matrix
        translation_matrix = glm.translate(glm.mat4(1.0), self._position)
        
        # Combine the translation and rotation matrices to form the view matrix
        self.view_matrix = glm.inverse(rotation_matrix * translation_matrix)

    @property
    def position(self):
        return tuple(self._position)

    @position.setter
    def position(self, value):
        self._position = glm.vec3(value)
        self.update_camera_matrix()

    @property
    def direction(self):
        return tuple(self._direction)

    @direction.setter
    def direction(self, value):
        self._direction = glm.normalize(glm.vec3(value))
        self._pitch = glm.degrees(glm.asin(self._direction.y))
        self._yaw = glm.degrees(glm.atan(self._direction.x, -self._direction.z))
        self.update_camera_matrix()

    @property
    def roll(self):
        return self._roll

    @roll.setter
    def roll(self, value):
        self._roll = value
        self.update_camera_matrix()

    @property
    def pitch(self):
        return self._pitch

    @property
    def yaw(self):
        return self._yaw

    def adjust_pitch(self, angle):
        self._pitch += angle
        self.update_camera_matrix()

    def adjust_yaw(self, angle):
        self._yaw += angle
        self.update_camera_matrix()

    def adjust_roll(self, angle):
        self._roll += angle
        self.update_camera_matrix()
        
    def move_forward(self, distance: float):
        self._position += self._direction * distance
        self.update_camera_matrix()        

    def get_view_matrix(self):
        return np.array(self.view_matrix.to_list(), dtype=np.float32)
