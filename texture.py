from OpenGL.GL import *
from PIL import Image

def load_texture(path):
    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    image = Image.open(path).transpose(Image.FLIP_TOP_BOTTOM)
    img_data = image.convert("RGB").tobytes()

    glTexImage2D(
        GL_TEXTURE_2D,
        0,
        GL_RGB,
        image.width,
        image.height,
        0,
        GL_RGB,
        GL_UNSIGNED_BYTE,
        img_data
    )

    glGenerateMipmap(GL_TEXTURE_2D)
    return texture
