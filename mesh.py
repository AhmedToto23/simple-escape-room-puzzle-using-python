import numpy as np
from OpenGL.GL import *


class CubeMesh:
    def __init__(self):
        # Position (3) + Normal (3)
        self.vertices = np.array([
            # Front
            -0.5, -0.5,  0.5,   0, 0, 1,
             0.5, -0.5,  0.5,   0, 0, 1,
             0.5,  0.5,  0.5,   0, 0, 1,
             0.5,  0.5,  0.5,   0, 0, 1,
            -0.5,  0.5,  0.5,   0, 0, 1,
            -0.5, -0.5,  0.5,   0, 0, 1,

            # Back
            -0.5, -0.5, -0.5,   0, 0, -1,
            -0.5,  0.5, -0.5,   0, 0, -1,
             0.5,  0.5, -0.5,   0, 0, -1,
             0.5,  0.5, -0.5,   0, 0, -1,
             0.5, -0.5, -0.5,   0, 0, -1,
            -0.5, -0.5, -0.5,   0, 0, -1,

            # Left
            -0.5,  0.5,  0.5,  -1, 0, 0,
            -0.5,  0.5, -0.5,  -1, 0, 0,
            -0.5, -0.5, -0.5,  -1, 0, 0,
            -0.5, -0.5, -0.5,  -1, 0, 0,
            -0.5, -0.5,  0.5,  -1, 0, 0,
            -0.5,  0.5,  0.5,  -1, 0, 0,

            # Right
             0.5,  0.5,  0.5,   1, 0, 0,
             0.5, -0.5, -0.5,   1, 0, 0,
             0.5,  0.5, -0.5,   1, 0, 0,
             0.5, -0.5, -0.5,   1, 0, 0,
             0.5,  0.5,  0.5,   1, 0, 0,
             0.5, -0.5,  0.5,   1, 0, 0,

            # Top
            -0.5,  0.5, -0.5,   0, 1, 0,
            -0.5,  0.5,  0.5,   0, 1, 0,
             0.5,  0.5,  0.5,   0, 1, 0,
             0.5,  0.5,  0.5,   0, 1, 0,
             0.5,  0.5, -0.5,   0, 1, 0,
            -0.5,  0.5, -0.5,   0, 1, 0,

            # Bottom
            -0.5, -0.5, -0.5,   0, -1, 0,
             0.5, -0.5,  0.5,   0, -1, 0,
            -0.5, -0.5,  0.5,   0, -1, 0,
             0.5, -0.5,  0.5,   0, -1, 0,
            -0.5, -0.5, -0.5,   0, -1, 0,
             0.5, -0.5, -0.5,   0, -1, 0,
        ], dtype=np.float32)

        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)

        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        # Position
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 6 * 4, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)

        # Normal
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 6 * 4, ctypes.c_void_p(12))
        glEnableVertexAttribArray(1)

        glBindVertexArray(0)

    def draw(self):
        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES, 0, 36)
        glBindVertexArray(0)
