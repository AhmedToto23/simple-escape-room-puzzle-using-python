import glfw
from OpenGL.GL import *
import glm
import time
from PIL import Image
import numpy as np

from shader import Shader
from camera import Camera
from mesh import CubeMesh
from text_renderer import TextRenderer


# ======================================================
# LEVEL CLASS
# ======================================================
class Level:
    def __init__(self, level_id, puzzle_question, puzzle_answer, wall_color=None):
        self.level_id = level_id
        self.puzzle_question = puzzle_question
        self.puzzle_answer = puzzle_answer
        self.completed = False
        # Optional: each level can have unique colors/theme
        self.wall_color = wall_color or glm.vec3(0.8, 0.8, 0.8)


# ======================================================
# CONFIGURATION
# ======================================================
class Config:
    WIDTH, HEIGHT = 1000, 700
    ROOM_SIZE = 10.0
    ROOM_LIMIT = 4.5
    PLAYER_HEIGHT = 1.0
    PLAYER_RADIUS = 0.3
    CROSSHAIR_SIZE = 20
    INTERACTION_DISTANCE = 3.0
    INTERACTION_DOT_THRESHOLD = 0.96


class UIConfig:
    PANEL_WIDTH = 700
    PANEL_HEIGHT = 300

    TITLE_Y_OFFSET = 90
    QUESTION_Y_OFFSET = 40
    ANSWER_LABEL_Y_OFFSET = -20
    ANSWER_TEXT_Y_OFFSET = -70

    PANEL_BG_COLOR = glm.vec3(0.05, 0.05, 0.08)


# ======================================================
# GAME STATE MANAGER
# ======================================================
class GameState:
    PLAYING = 0
    PUZZLE = 1
    FINISHED = 2


class Game:
    def __init__(self):
        self.current_level_index = 0

        # Multiple levels with different puzzles
        self.levels = [
            Level(
                level_id=1,
                puzzle_question="What is 5 + 7?",
                puzzle_answer="12",
                wall_color=glm.vec3(0.8, 0.8, 0.9)
            ),
            Level(
                level_id=2,
                puzzle_question="Who lives in the sea and is loved by people?",
                puzzle_answer="spongebob squarepants",
                wall_color=glm.vec3(0.9, 0.8, 0.8)
            ),
            Level(
                level_id=3,
                puzzle_question="Who is the best doctor ever?",
                puzzle_answer="hataba",
                wall_color=glm.vec3(0.8, 0.9, 0.8)
            )
        ]

        self.state = GameState.PLAYING

        # Board state (replaces door)
        self.board_visible = True
        # Board dimensions (professional size)
        self.board_size = glm.vec3(2.2, 1.3, 0.12)

        # Board on FRONT wall, centered
        self.board_pos = glm.vec3(
            0.0,  # center horizontally
            1.6,  # eye level
            -5 + (self.board_size.z / 2) + 0.05  # slightly in front of wall
        )

        # Message system
        self.show_message = False
        self.message_text = ""
        self.message_timer = 0.0

        # Puzzle state
        self.current_answer = ""
        # Cursor blinking
        self.cursor_visible = True
        self.cursor_timer = 0.0

        self.show_final_image = False
        self.final_timer = 0.0

        self.cursor_timer = 0.0
        self.cursor_visible = True

    def load_next_level(self, camera):
        """Load the next level or finish the game"""
        if self.current_level_index + 1 >= len(self.levels):
            print("🎉 GAME COMPLETED! All levels finished!")
            self.state = GameState.FINISHED
            return

        self.current_level_index += 1

        # Reset for new level
        self.board_visible = True
        self.reset_puzzle()
        self.show_message = False

        # Move player to spawn position
        camera.position = glm.vec3(0, Config.PLAYER_HEIGHT, 3)
        camera.yaw = -90
        camera.pitch = 0
        camera.update_vectors()

        print(f"➡️ Entered Level {self.current_level_index + 1}")

    @property
    def current_level(self):
        return self.levels[self.current_level_index]

    def reset_puzzle(self):
        """Clear the current answer"""
        self.current_answer = ""

    def check_answer(self):
        """Check if the answer is correct"""
        return self.current_answer.strip().lower() == self.current_level.puzzle_answer

    def complete_level(self):
        """Handle correct answer"""
        self.current_level.completed = True
        self.board_visible = False
        self.reset_puzzle()

        # FINAL LEVEL BEHAVIOR
        if self.current_level.level_id == 3:
            self.show_final_image = True
            self.final_timer = 5.0  # seconds before closing
            self.state = GameState.FINISHED
        else:
            self.show_message = True
            self.message_text = f"✓ Level {self.current_level.level_id} Complete!"
            self.message_timer = 2.5
            self.state = GameState.PLAYING

    def wrong_answer(self):
        """Handle wrong answer"""
        self.show_message = True
        self.message_text = "✗ Wrong Answer - Try Again"
        self.message_timer = 2.0

    def update(self, delta_time, camera, window=None):
        if self.show_message:
            self.message_timer -= delta_time
            if self.message_timer <= 0:
                self.show_message = False
                if not self.board_visible and self.state != GameState.FINISHED:
                    self.load_next_level(camera)

        if self.show_final_image:
            self.final_timer -= delta_time
            if self.final_timer <= 0 and window:
                glfw.set_window_should_close(window, True)

        self.cursor_timer += delta_time
        if self.cursor_timer >= 0.5:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0.0


# ======================================================
# TEXTURE LOADER
# ======================================================
class TextureManager:
    @staticmethod
    def load_texture(path):
        texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture)

        # Critical alignment setting for Windows compatibility
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)

        # Texture parameters
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        # Load and prepare image
        image = Image.open(path).convert("RGB")
        image = image.transpose(Image.FLIP_TOP_BOTTOM)

        img_data = np.array(image, dtype=np.uint8)
        img_data = np.ascontiguousarray(img_data)

        glTexImage2D(
            GL_TEXTURE_2D, 0, GL_RGB,
            image.width, image.height, 0,
            GL_RGB, GL_UNSIGNED_BYTE,
            img_data.tobytes()
        )

        glGenerateMipmap(GL_TEXTURE_2D)

        return texture


# ======================================================
# RENDERER
# ======================================================
class Renderer:
    def __init__(self, shader, cube, image_shader):
        self.shader = shader
        self.cube = cube
        self.image_shader = image_shader


    def draw_dark_overlay(self, alpha=0.45):
        """Draw semi-transparent dark overlay"""
        glDisable(GL_DEPTH_TEST)

        self.shader.use()

        ortho = glm.ortho(0, Config.WIDTH, 0, Config.HEIGHT)
        self.shader.set_mat4("projection", ortho)
        self.shader.set_mat4("view", glm.mat4(1))

        # Semi-transparent black
        self.shader.set_vec3("objectColor", glm.vec3(0, 0, 0))

        # Disable texture
        glBindTexture(GL_TEXTURE_2D, 0)

        model = glm.mat4(1)
        model = glm.translate(
            model, glm.vec3(Config.WIDTH / 2, Config.HEIGHT / 2, 0)
        )
        model = glm.scale(
            model, glm.vec3(Config.WIDTH, Config.HEIGHT, 1)
        )

        self.shader.set_mat4("model", model)

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        self.cube.draw()

    def draw_textured_cube(self, pos, scale, texture):
        """Draw a textured cube at the given position and scale"""
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, texture)
        self.shader.set_int("texture1", 0)

        model = glm.mat4(1.0)
        model = glm.translate(model, pos)
        model = glm.scale(model, scale)
        self.shader.set_mat4("model", model)

        self.cube.draw()

    def draw_colored_cube(self, pos, scale, color):
        """Draw a colored cube (no texture)"""
        glBindTexture(GL_TEXTURE_2D, 0)
        self.shader.set_vec3("objectColor", color)

        model = glm.mat4(1.0)
        model = glm.translate(model, pos)
        model = glm.scale(model, scale)
        self.shader.set_mat4("model", model)

        self.cube.draw()

    def draw_board(self, pos, size):
        """Draw the puzzle board with frame"""
        glBindTexture(GL_TEXTURE_2D, 0)

        # ===== FRAME (back, darker) =====
        frame_size = size + glm.vec3(0.18, 0.18, 0.04)
        self.shader.set_vec3("objectColor", glm.vec3(0.25, 0.18, 0.12))  # dark wood

        model = glm.mat4(1.0)
        model = glm.translate(model, pos - glm.vec3(0, 0, 0.04))
        model = glm.scale(model, frame_size)
        self.shader.set_mat4("model", model)
        self.cube.draw()

        # ===== BOARD SURFACE (front, brighter) =====
        self.shader.set_vec3("objectColor", glm.vec3(0.85, 0.75, 0.55))  # light wood

        model = glm.mat4(1.0)
        model = glm.translate(model, pos)
        model = glm.scale(model, size)
        self.shader.set_mat4("model", model)
        self.cube.draw()

    def draw_crosshair(self):
        """Draw the crosshair overlay"""
        glDisable(GL_DEPTH_TEST)

        self.shader.use()

        ortho = glm.ortho(0, Config.WIDTH, 0, Config.HEIGHT)
        self.shader.set_mat4("projection", ortho)
        self.shader.set_mat4("view", glm.mat4(1))

        # Reset lighting for 2D
        self.shader.set_vec3("lightColor", glm.vec3(1.2, 1.2, 1.2))
        self.shader.set_vec3("lightPos", glm.vec3(0))
        self.shader.set_vec3("viewPos", glm.vec3(0))
        self.shader.set_vec3("objectColor", glm.vec3(1))

        # Disable texture
        glBindTexture(GL_TEXTURE_2D, 0)

        # Horizontal line
        model = glm.mat4(1)
        model = glm.translate(model, glm.vec3(Config.WIDTH / 2, Config.HEIGHT / 2, 0))
        model = glm.scale(model, glm.vec3(Config.CROSSHAIR_SIZE, 2, 1))
        self.shader.set_mat4("model", model)
        self.cube.draw()

        # Vertical line
        model = glm.mat4(1)
        model = glm.translate(model, glm.vec3(Config.WIDTH / 2, Config.HEIGHT / 2, 0))
        model = glm.scale(model, glm.vec3(2, Config.CROSSHAIR_SIZE, 1))
        self.shader.set_mat4("model", model)
        self.cube.draw()

    def draw_ui_panel(self):
        """Draw the puzzle UI panel background"""
        glDisable(GL_DEPTH_TEST)

        self.shader.use()

        ortho = glm.ortho(0, Config.WIDTH, 0, Config.HEIGHT)
        self.shader.set_mat4("projection", ortho)
        self.shader.set_mat4("view", glm.mat4(1))
        self.shader.set_vec3("objectColor", UIConfig.PANEL_BG_COLOR)

        # Disable texture
        glBindTexture(GL_TEXTURE_2D, 0)

        model = glm.mat4(1)

        # Centered panel
        model = glm.translate(
            model,
            glm.vec3(Config.WIDTH / 2, Config.HEIGHT / 2, 0)
        )

        model = glm.scale(
            model,
            glm.vec3(UIConfig.PANEL_WIDTH, UIConfig.PANEL_HEIGHT, 1)
        )

        self.shader.set_mat4("model", model)

        # Ensure blending is enabled
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        self.cube.draw()

    def draw_fullscreen_image(self, texture):
        if self.image_shader is None:
            print("❌ image_shader is None!")
            return

        glDisable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        self.image_shader.use()

        ortho = glm.ortho(0, Config.WIDTH, 0, Config.HEIGHT)
        self.image_shader.set_mat4("projection", ortho)

        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, texture)
        self.image_shader.set_int("image", 0)

        model = glm.mat4(1)
        model = glm.translate(
            model,
            glm.vec3(Config.WIDTH / 2, Config.HEIGHT / 2, 0)
        )
        model = glm.scale(
            model,
            glm.vec3(Config.WIDTH, Config.HEIGHT, 1)
        )

        self.image_shader.set_mat4("model", model)

        self.cube.draw()


# ======================================================
# PLAYER CONTROLLER
# ======================================================
class PlayerController:
    def __init__(self, camera, game):
        self.camera = camera
        self.game = game

    def update(self, window, delta_time):
        """Update player position and constraints"""
        self.camera.process_keyboard(window, delta_time)
        self.clamp_position()

    def clamp_position(self):
        """Keep player within room bounds"""
        self.camera.position.y = Config.PLAYER_HEIGHT

        # Room boundaries
        self.camera.position.x = max(
            -Config.ROOM_LIMIT + Config.PLAYER_RADIUS,
            min(Config.ROOM_LIMIT - Config.PLAYER_RADIUS, self.camera.position.x)
        )
        self.camera.position.z = max(
            -Config.ROOM_LIMIT + Config.PLAYER_RADIUS,
            min(Config.ROOM_LIMIT - Config.PLAYER_RADIUS, self.camera.position.z)
        )

    def is_looking_at_board(self, board_pos, board_size):
        """Check if player is looking at the board using ray-box intersection"""
        ray_origin = self.camera.position
        ray_dir = glm.normalize(self.camera.front)

        half = board_size * 0.5
        min_box = board_pos - half
        max_box = board_pos + half

        tmin = -float("inf")
        tmax = float("inf")

        for i in range(3):
            if abs(ray_dir[i]) < 1e-6:
                if ray_origin[i] < min_box[i] or ray_origin[i] > max_box[i]:
                    return False
            else:
                t1 = (min_box[i] - ray_origin[i]) / ray_dir[i]
                t2 = (max_box[i] - ray_origin[i]) / ray_dir[i]
                tmin = max(tmin, min(t1, t2))
                tmax = min(tmax, max(t1, t2))

        return tmax >= max(tmin, 0.0)


# ======================================================
# INPUT HANDLERS
# ======================================================
class InputHandler:
    def __init__(self, game, player_controller):
        self.game = game
        self.player = player_controller

    def handle_mouse_button(self, window, button, action, mods):
        """Handle mouse button clicks"""
        if button == glfw.MOUSE_BUTTON_LEFT and action == glfw.PRESS:
            if self.game.state == GameState.PLAYING and self.game.board_visible:
                if self.player.is_looking_at_board(
                        self.game.board_pos,
                        self.game.board_size
                ):
                    self.game.state = GameState.PUZZLE
                    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_NORMAL)

    def handle_key(self, window, key, scancode, action, mods):
        """Handle keyboard input for puzzle"""
        if self.game.state != GameState.PUZZLE or action != glfw.PRESS:
            return

        if key == glfw.KEY_ENTER:
            # Ignore empty answers
            if not self.game.current_answer.strip():
                return

            if self.game.check_answer():
                self.game.complete_level()
                glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)
            else:
                self.game.wrong_answer()
                self.game.reset_puzzle()

        elif key == glfw.KEY_BACKSPACE:
            self.game.current_answer = self.game.current_answer[:-1]

        # Numbers
        elif glfw.KEY_0 <= key <= glfw.KEY_9:
            self.game.current_answer += chr(key)

        # Letters A–Z
        elif glfw.KEY_A <= key <= glfw.KEY_Z:
            self.game.current_answer += chr(key).lower()

        # Space
        elif key == glfw.KEY_SPACE:
            self.game.current_answer += " "


# ======================================================
# MAIN APPLICATION
# ======================================================
class EscapeRoom:
    def __init__(self):
        self.window = None
        self.game = Game()
        self.camera = None
        self.player = None
        self.input_handler = None
        self.shader = None
        self.text_shader = None
        self.renderer = None
        self.cube = None
        self.text_renderer = None
        self.floor_texture = None
        self.wall_texture = None
        self.final_texture = None
        self.image_shader = None

    def init_glfw(self):
        """Initialize GLFW and create window"""
        if not glfw.init():
            raise RuntimeError("GLFW initialization failed")

        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL_TRUE)

        monitor = glfw.get_primary_monitor()
        video_mode = glfw.get_video_mode(monitor)

        Config.WIDTH = video_mode.size.width
        Config.HEIGHT = video_mode.size.height

        self.window = glfw.create_window(
            Config.WIDTH,
            Config.HEIGHT,
            "Escape Room - Board Puzzle",
            monitor,  # Fullscreen
            None
        )

        if not self.window:
            glfw.terminate()
            raise RuntimeError("Failed to create GLFW window")

        glfw.make_context_current(self.window)

        glViewport(0, 0, Config.WIDTH, Config.HEIGHT)

    def init_opengl(self):
        """Initialize OpenGL settings"""
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    def init_resources(self):
        """Load shaders, textures, and other resources"""

        # ===============================
        # MAIN 3D SHADER
        # ===============================
        self.shader = Shader("shaders/vertex.glsl", "shaders/fragment.glsl")

        # ===============================
        # TEXT SHADER
        # ===============================
        self.text_shader = Shader(
            "shaders/text_vertex.glsl",
            "shaders/text_fragment.glsl"
        )
        self.text_shader.use()

        projection = glm.ortho(
            0.0, float(Config.WIDTH),
            0.0, float(Config.HEIGHT)
        )
        self.text_shader.set_mat4("projection", projection)
        self.text_shader.set_int("text", 0)

        # ===============================
        # IMAGE SHADER (🔥 MUST BE BEFORE RENDERER)
        # ===============================
        self.image_shader = Shader(
            "shaders/image_vertex.glsl",
            "shaders/image_fragment.glsl"
        )

        # ===============================
        # MESH & CAMERA
        # ===============================
        self.cube = CubeMesh()
        self.camera = Camera(position=(0, Config.PLAYER_HEIGHT, 3))
        self.player = PlayerController(self.camera, self.game)
        self.input_handler = InputHandler(self.game, self.player)

        # ===============================
        # RENDERER (NOW image_shader IS VALID)
        # ===============================
        self.renderer = Renderer(self.shader, self.cube, self.image_shader)

        # ===============================
        # TEXTURES
        # ===============================
        self.floor_texture = TextureManager.load_texture(
            "assets/textures/floor.jpg"
        )
        self.wall_texture = TextureManager.load_texture(
            "assets/textures/wall.jpg"
        )
        self.final_texture = TextureManager.load_texture(
            "assets/textures/final_image.jpg"
        )

        # ===============================
        # TEXT RENDERER
        # ===============================
        self.text_renderer = TextRenderer(
            "fonts/about_font.TTF",
            72
        )

    def setup_input(self):
        """Setup input callbacks"""
        glfw.set_window_user_pointer(self.window, self)
        glfw.set_input_mode(self.window, glfw.CURSOR, glfw.CURSOR_DISABLED)

        glfw.set_mouse_button_callback(
            self.window,
            lambda w, b, a, m: self.input_handler.handle_mouse_button(w, b, a, m)
        )

        glfw.set_key_callback(
            self.window,
            lambda w, k, s, a, m: self.input_handler.handle_key(w, k, s, a, m)
        )

        glfw.set_cursor_pos_callback(
            self.window,
            lambda w, x, y: self.camera.process_mouse(x, y)
            if self.game.state == GameState.PLAYING else None
        )

    def render_scene(self):
        """Render the 3D scene"""
        self.shader.use()
        self.shader.set_vec3("lightPos", glm.vec3(2.5, 3.5, 1.5))
        self.shader.set_vec3("lightColor", glm.vec3(1))
        self.shader.set_vec3("viewPos", self.camera.position)

        projection = glm.perspective(
            glm.radians(60),
            Config.WIDTH / Config.HEIGHT,
            0.1, 100
        )
        self.shader.set_mat4("projection", projection)
        self.shader.set_mat4("view", self.camera.get_view_matrix())

        # Floor
        self.renderer.draw_textured_cube(
            glm.vec3(0, -1, 0),
            glm.vec3(10, 0.2, 10),
            self.floor_texture
        )

        # Walls with level-specific tinting
        level_tint = self.game.current_level.wall_color
        self.shader.set_vec3("objectColor", level_tint)

        # Back wall
        self.renderer.draw_textured_cube(
            glm.vec3(0, 1, -5),
            glm.vec3(10, 4, 0.2),
            self.wall_texture
        )

        # Front wall
        self.renderer.draw_textured_cube(
            glm.vec3(0, 1, 5),
            glm.vec3(10, 4, 0.2),
            self.wall_texture
        )

        # Left wall
        self.renderer.draw_textured_cube(
            glm.vec3(-5, 1, 0),
            glm.vec3(0.2, 4, 10),
            self.wall_texture
        )

        # Right wall
        self.renderer.draw_textured_cube(
            glm.vec3(5, 1, 0),
            glm.vec3(0.2, 4, 10),
            self.wall_texture
        )

        # Draw the puzzle board if visible
        if self.game.board_visible:
            self.renderer.draw_board(
                self.game.board_pos,
                self.game.board_size
            )

    def render_ui(self):
        """Render UI elements with proper OpenGL state isolation"""

        # ============================================================
        # CRITICAL: HARD RESET OpenGL STATE FOR UI RENDERING
        # ============================================================
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_CULL_FACE)

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glActiveTexture(GL_TEXTURE0)

        # ============================================================
        # Display final image fullscreen (overrides everything else)
        # ============================================================
        if self.game.show_final_image:
            self.renderer.draw_fullscreen_image(self.final_texture)
            # Restore state before returning
            glDisable(GL_BLEND)
            glEnable(GL_DEPTH_TEST)
            return

        # ============================================================
        # PUZZLE UI
        # ============================================================
        if self.game.state == GameState.PUZZLE:
            # Draw dark overlay
            self.renderer.draw_dark_overlay(0.45)
            self.renderer.draw_ui_panel()

            # ---- FORCE TEXT SHADER STATE (DO NOT RELY ON PREVIOUS CALLS) ----
            ortho = glm.ortho(0, Config.WIDTH, 0, Config.HEIGHT)

            self.text_shader.use()
            self.text_shader.set_mat4("projection", ortho)
            self.text_shader.set_int("text", 0)

            panel_center_x = Config.WIDTH / 2
            panel_center_y = Config.HEIGHT / 2

            # Title
            self.text_renderer.render_text(
                self.text_shader,
                f"LEVEL {self.game.current_level.level_id}",
                panel_center_x - 160,
                panel_center_y + UIConfig.TITLE_Y_OFFSET,
                1.6,
                glm.vec3(1, 0.9, 0.2)
            )

            # Question
            self.text_renderer.render_text(
                self.text_shader,
                self.game.current_level.puzzle_question,
                panel_center_x - 300,
                panel_center_y + UIConfig.QUESTION_Y_OFFSET,
                0.9,
                glm.vec3(1, 1, 1)
            )

            # Answer label
            self.text_renderer.render_text(
                self.text_shader,
                "Your Answer:",
                panel_center_x - 300,
                panel_center_y + UIConfig.ANSWER_LABEL_Y_OFFSET,
                0.8,
                glm.vec3(0.7, 1, 0.7)
            )

            # Answer input (with blinking cursor)
            cursor = "_" if self.game.cursor_visible else ""
            answer_text = self.game.current_answer + cursor

            self.text_renderer.render_text(
                self.text_shader,
                answer_text,
                panel_center_x - 300,
                panel_center_y + UIConfig.ANSWER_TEXT_Y_OFFSET,
                1.0,
                glm.vec3(0.2, 1, 0.2)
            )

        # ============================================================
        # MESSAGE DISPLAY
        # ============================================================
        if self.game.show_message:
            # ---- FORCE TEXT SHADER STATE AGAIN ----
            ortho = glm.ortho(0, Config.WIDTH, 0, Config.HEIGHT)

            self.text_shader.use()
            self.text_shader.set_mat4("projection", ortho)
            self.text_shader.set_int("text", 0)

            # Choose color based on message type
            if "Complete" in self.game.message_text:
                color = glm.vec3(0.2, 1, 0.2)  # Green for success
            elif "Wrong" in self.game.message_text:
                color = glm.vec3(1, 0.3, 0.2)  # Red for wrong
            else:
                color = glm.vec3(1, 0.8, 0.2)  # Yellow for info

            self.text_renderer.render_text(
                self.text_shader,
                self.game.message_text,
                Config.WIDTH / 2 - 180,
                Config.HEIGHT / 2 - UIConfig.PANEL_HEIGHT / 2 - 50,
                1.1,
                color
            )

        # ============================================================
        # CROSSHAIR (PLAYING STATE)
        # ============================================================
        if self.game.state == GameState.PLAYING:
            self.renderer.draw_crosshair()

        # ============================================================
        # --- Restore state ---
        glDisable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)

    def run(self):
        """Main game loop"""
        self.init_glfw()
        self.init_opengl()
        self.init_resources()
        self.setup_input()

        last_time = time.time()

        while not glfw.window_should_close(self.window):
            current_time = time.time()
            delta_time = current_time - last_time
            last_time = current_time

            glfw.poll_events()

            # Update game state
            if self.game.state == GameState.PLAYING:
                self.player.update(self.window, delta_time)

            # Update timers and transitions
            self.game.update(delta_time, self.camera, self.window)

            # Render
            glClearColor(0.08, 0.08, 0.12, 1)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            self.render_scene()
            self.render_ui()

            glfw.swap_buffers(self.window)

        glfw.terminate()


# ======================================================
# ENTRY POINT
# ======================================================
def main():
    try:
        game = EscapeRoom()
        game.run()
    except Exception as e:
        print(f"Error: {e}")
        glfw.terminate()
        raise


if __name__ == "__main__":
    main()