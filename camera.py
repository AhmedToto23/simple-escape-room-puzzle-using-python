import glm
import glfw

class Camera:
    def __init__(self, position):
        self.position = glm.vec3(position)
        self.front = glm.vec3(0, 0, -1)
        self.up = glm.vec3(0, 1, 0)

        self.yaw = -90.0
        self.pitch = 0.0

        self.speed = 3.0
        self.sensitivity = 0.1

        self.last_x = 500
        self.last_y = 350
        self.first_mouse = True

        # ===== COLLISION SETTINGS =====
        self.radius = 0.2  # player size
        self.room_min = glm.vec3(-5.0, 0.0, -5.0)
        self.room_max = glm.vec3( 5.0, 2.0,  5.0)

    def get_view_matrix(self):
        return glm.lookAt(
            self.position,
            self.position + self.front,
            self.up
        )

    # -------------------------------
    # COLLISION CHECK
    # -------------------------------
    def can_move_to(self, new_pos):
        return (
            self.room_min.x + self.radius <= new_pos.x <= self.room_max.x - self.radius and
            self.room_min.z + self.radius <= new_pos.z <= self.room_max.z - self.radius
        )

    def process_keyboard(self, window, delta_time):
        velocity = self.speed * delta_time

        # FLAT forward direction (ignore Y)
        forward = glm.vec3(self.front.x, 0.0, self.front.z)
        forward = glm.normalize(forward)

        # Right direction
        right = glm.normalize(glm.cross(forward, self.up))

        if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS:
            self.position += forward * velocity
        if glfw.get_key(window, glfw.KEY_S) == glfw.PRESS:
            self.position -= forward * velocity
        if glfw.get_key(window, glfw.KEY_A) == glfw.PRESS:
            self.position -= right * velocity
        if glfw.get_key(window, glfw.KEY_D) == glfw.PRESS:
            self.position += right * velocity

        self.position.y = 1.0

    def process_mouse(self, xpos, ypos):
        if self.first_mouse:
            self.last_x = xpos
            self.last_y = ypos
            self.first_mouse = False

        xoffset = xpos - self.last_x
        yoffset = self.last_y - ypos
        self.last_x = xpos
        self.last_y = ypos

        xoffset *= self.sensitivity
        yoffset *= self.sensitivity

        self.yaw += xoffset
        self.pitch += yoffset

        self.pitch = max(-89.0, min(89.0, self.pitch))

        self.update_vectors()

    def update_vectors(self):
        front = glm.vec3(
            glm.cos(glm.radians(self.yaw)) * glm.cos(glm.radians(self.pitch)),
            glm.sin(glm.radians(self.pitch)),
            glm.sin(glm.radians(self.yaw)) * glm.cos(glm.radians(self.pitch))
        )
        self.front = glm.normalize(front)
