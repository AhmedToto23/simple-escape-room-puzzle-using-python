from OpenGL.GL import *
import glm
import ctypes
from PIL import Image


class UIText:
    def __init__(self, font_path):
        self.char_size = 16
        self.chars_per_row = 16

        self.texture = self.load_texture(font_path)
        self.vao, self.vbo = glGenVertexArrays(1), glGenBuffers(1)

        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, 6 * 4 * 4, None, GL_DYNAMIC_DRAW)

        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 4 * 4, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)

        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 4 * 4, ctypes.c_void_p(8))
        glEnableVertexAttribArray(1)

        glBindVertexArray(0)

    def load_texture(self, path):
        image = Image.open(path).convert("RGBA")
        image = image.transpose(Image.FLIP_TOP_BOTTOM)
        img_data = image.tobytes()

        tex = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex)

        glTexImage2D(
            GL_TEXTURE_2D, 0, GL_RGBA,
            image.width, image.height, 0,
            GL_RGBA, GL_UNSIGNED_BYTE, img_data
        )

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

        return tex

    def draw_text(self, shader, text, x, y, scale, color, screen_w, screen_h):
        shader.use()
        shader.set_vec3("textColor", color)

        projection = glm.ortho(0, screen_w, 0, screen_h)
        shader.set_mat4("projection", projection)

        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glBindVertexArray(self.vao)

        for char in text:
            ascii_code = ord(char)
            tx = (ascii_code % self.chars_per_row) / self.chars_per_row
            ty = (ascii_code // self.chars_per_row) / self.chars_per_row

            w = self.char_size * scale
            h = self.char_size * scale

            vertices = [
                x,     y + h, tx,            ty,
                x,     y,     tx,            ty + 1/16,
                x + w, y,     tx + 1/16,     ty + 1/16,

                x,     y + h, tx,            ty,
                x + w, y,     tx + 1/16,     ty + 1/16,
                x + w, y + h, tx + 1/16,     ty
            ]

            glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
            glBufferSubData(GL_ARRAY_BUFFER, 0, len(vertices) * 4, (ctypes.c_float * len(vertices))(*vertices))
            glDrawArrays(GL_TRIANGLES, 0, 6)

            x += w

        glBindVertexArray(0)
