from OpenGL.GL import *
import freetype
import ctypes
import glm


class TextRenderer:
    def __init__(self, font_path, font_size=48):
        # Store glyph data
        self.characters = {}

        # Load font
        face = freetype.Face(font_path)
        face.set_pixel_sizes(0, font_size)

        # IMPORTANT for FreeType bitmap alignment
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)

        # Load ASCII characters
        for c in range(32, 128):
            face.load_char(chr(c))
            glyph = face.glyph
            bitmap = glyph.bitmap

            # Generate texture for glyph
            texture = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, texture)

            glTexImage2D(
                GL_TEXTURE_2D,
                0,
                GL_RED,
                bitmap.width,
                bitmap.rows,
                0,
                GL_RED,
                GL_UNSIGNED_BYTE,
                bitmap.buffer
            )

            # Texture parameters
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

            # Store character info
            self.characters[c] = {
                "texture": texture,
                "size": (bitmap.width, bitmap.rows),
                "bearing": (glyph.bitmap_left, glyph.bitmap_top),
                "advance": glyph.advance.x
            }

        glBindTexture(GL_TEXTURE_2D, 0)

        # ===== VAO & VBO =====
        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)

        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)

        # 6 vertices × 4 floats (x, y, u, v)
        glBufferData(GL_ARRAY_BUFFER, 6 * 4 * 4, None, GL_DYNAMIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(
            0,
            4,
            GL_FLOAT,
            GL_FALSE,
            4 * 4,
            ctypes.c_void_p(0)
        )

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

    def render_text(self, shader, text, x, y, scale, color):
        shader.use()
        shader.set_vec3("textColor", color)
        shader.set_int("text", 0)  # ✅ FIX

        glActiveTexture(GL_TEXTURE0)
        glBindVertexArray(self.vao)

        for char in text:
            ch = self.characters.get(ord(char))
            if ch is None:
                continue

            xpos = x + ch["bearing"][0] * scale
            ypos = y - (ch["size"][1] - ch["bearing"][1]) * scale

            w = ch["size"][0] * scale
            h = ch["size"][1] * scale

            vertices = (
                xpos,     ypos + h,   0.0, 0.0,
                xpos,     ypos,       0.0, 1.0,
                xpos + w, ypos,       1.0, 1.0,

                xpos,     ypos + h,   0.0, 0.0,
                xpos + w, ypos,       1.0, 1.0,
                xpos + w, ypos + h,   1.0, 0.0
            )

            glBindTexture(GL_TEXTURE_2D, ch["texture"])
            glBindBuffer(GL_ARRAY_BUFFER, self.vbo)

            glBufferSubData(
                GL_ARRAY_BUFFER,
                0,
                ctypes.sizeof(ctypes.c_float * len(vertices)),
                (ctypes.c_float * len(vertices))(*vertices)
            )

            glDrawArrays(GL_TRIANGLES, 0, 6)

            # Advance cursor (1/64th pixels → pixels)
            x += (ch["advance"] >> 6) * scale

        glBindVertexArray(0)
        glBindTexture(GL_TEXTURE_2D, 0)
