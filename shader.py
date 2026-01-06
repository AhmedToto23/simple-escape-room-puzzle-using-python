from OpenGL.GL import *
import glm


class Shader:
    def __init__(self, vertex_path: str, fragment_path: str):
        self.id = glCreateProgram()
        self._uniform_cache = {}

        # =============================
        # Load shader sources
        # =============================
        vertex_src = self._load_file(vertex_path)
        fragment_src = self._load_file(fragment_path)

        # =============================
        # Compile shaders
        # =============================
        vertex_shader = self._compile_shader(
            vertex_src, GL_VERTEX_SHADER, vertex_path
        )
        fragment_shader = self._compile_shader(
            fragment_src, GL_FRAGMENT_SHADER, fragment_path
        )

        # =============================
        # Link program
        # =============================
        glAttachShader(self.id, vertex_shader)
        glAttachShader(self.id, fragment_shader)
        glLinkProgram(self.id)

        if not glGetProgramiv(self.id, GL_LINK_STATUS):
            error = glGetProgramInfoLog(self.id).decode()
            raise RuntimeError(f"❌ Shader link error:\n{error}")

        glDeleteShader(vertex_shader)
        glDeleteShader(fragment_shader)

    # ==================================================
    # INTERNAL HELPERS
    # ==================================================
    def _load_file(self, path: str) -> str:
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"❌ Shader file not found: {path}")

    def _compile_shader(self, source: str, shader_type, path: str):
        shader = glCreateShader(shader_type)
        glShaderSource(shader, source)
        glCompileShader(shader)

        if not glGetShaderiv(shader, GL_COMPILE_STATUS):
            error = glGetShaderInfoLog(shader).decode()
            shader_name = "VERTEX" if shader_type == GL_VERTEX_SHADER else "FRAGMENT"
            raise RuntimeError(
                f"❌ {shader_name} shader compilation error ({path}):\n{error}"
            )

        return shader

    def _get_uniform_location(self, name: str) -> int:
        if name in self._uniform_cache:
            return self._uniform_cache[name]

        location = glGetUniformLocation(self.id, name)
        # if location == -1:
        #     # Not fatal — OpenGL allows unused uniforms
        #     # But good to know during development
        #     print(f"⚠️ Warning: uniform '{name}' not found in shader")

        self._uniform_cache[name] = location
        return location

    # ==================================================
    # PUBLIC API
    # ==================================================
    def use(self):
        glUseProgram(self.id)

    # =============================
    # UNIFORMS
    # =============================
    def set_mat4(self, name: str, mat):
        glUniformMatrix4fv(
            self._get_uniform_location(name),
            1,
            GL_FALSE,
            glm.value_ptr(mat)
        )

    def set_vec3(self, name: str, vec):
        glUniform3f(
            self._get_uniform_location(name),
            float(vec.x),
            float(vec.y),
            float(vec.z)
        )

    def set_float(self, name: str, value: float):
        glUniform1f(self._get_uniform_location(name), float(value))

    def set_int(self, name: str, value: int):
        glUniform1i(self._get_uniform_location(name), int(value))

    def set_bool(self, name: str, value: bool):
        glUniform1i(self._get_uniform_location(name), 1 if value else 0)
