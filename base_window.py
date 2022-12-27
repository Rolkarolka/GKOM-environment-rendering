import math
from pathlib import Path
import imageio
import numpy as np
from moderngl import DEPTH_TEST, TRIANGLE_STRIP
from moderngl_window import WindowConfig
from pyrr import Matrix44, Vector4

from shader_utils import get_shaders


class MainWindowConfig(WindowConfig):
    gl_version = (3, 3)
    title = 'Environment Rendering'
    resource_dir = (Path(__file__).parent / 'resources').resolve()

    def __init__(self, **kwargs):
        super(MainWindowConfig, self).__init__(**kwargs)

        shaders = get_shaders()
        self.program = self.ctx.program(vertex_shader=shaders[self.argv.shader_name].vertex_shader,
                                        fragment_shader=shaders[self.argv.shader_name].fragment_shader)

        self.height_scale = self.argv.height_scale if self.argv.height_scale is not None else 1.0

        self.load_png_heightmap(self.argv.map_name)
        self.generate_terrain()
        self.init_shaders_variables()

        self.lookat = (-self.x_range * 3 / 4, -self.y_range * 3 / 4, (self.x_range + self.y_range) / 3)

    def load_png_heightmap(self, map_name):
        raw_heightmap = imageio.v3.imread(f"./resources/heightmaps/{map_name}.png")
        self.x_range = raw_heightmap.shape[0]
        self.y_range = raw_heightmap.shape[1]

        self.height_map = np.empty([self.x_range, self.y_range, 3])
        for x_i in range(self.x_range):
            for y_i in range(self.y_range):
                # this is necessary because png files can store colours as rgb or grayscale values, which creates issues
                z_val = raw_heightmap[x_i][y_i] if len(raw_heightmap.shape) == 2 else raw_heightmap[x_i][y_i][0]
                self.height_map[x_i][y_i] = np.array([x_i, y_i, z_val])  # add ' / 3' to z_val if stuff's too darn high

    def generate_terrain(self):
        vertices = np.empty([self.x_range * self.y_range, 3])
        vertices_and_normals = np.empty([self.x_range * self.y_range, 6])
        indices = np.empty([3 * 2 * (self.x_range - 1) * (self.y_range - 1) + self.y_range - 1])

        def append_to_indices(vertex):
            indices[append_to_indices.counter] = vertex
            append_to_indices.counter += 1

        append_to_indices.counter = 0

        for x_i in range(self.x_range):
            for y_i in range(self.y_range):
                v_idx = y_i * self.x_range + x_i
                vertices[v_idx] = self.height_map[x_i][y_i]
                vertices_and_normals[v_idx] = [*self.height_map[x_i][y_i], 0, 0, 0]

        def create_triangle(vertex_1, vertex_2, vertex_3):
            append_to_indices(vertex_1)
            append_to_indices(vertex_2)
            append_to_indices(vertex_3)
            edge_1 = vertices[vertex_2] - vertices[vertex_1]
            edge_2 = vertices[vertex_3] - vertices[vertex_1]
            cross = np.cross(edge_1, edge_2)

            for vertex in [vertex_1, vertex_2, vertex_3]:
                for i in range(3):
                    vertices_and_normals[vertex][3 + i] += cross[i]

        for x_i in range(self.x_range - 1):
            for y_i in range(self.y_range - 1):
                # create two triangles forming a quadrangle (sorta, if you ignore the z-values)
                vertex_1 = x_i + y_i * self.x_range
                vertex_2 = x_i + 1 + y_i * self.x_range
                vertex_3 = x_i + (y_i + 1) * self.x_range
                create_triangle(vertex_1, vertex_2, vertex_3)

                vertex_1 = x_i + 1 + y_i * self.x_range
                vertex_2 = x_i + 1 + (y_i + 1) * self.x_range
                vertex_3 = x_i + (y_i + 1) * self.x_range
                create_triangle(vertex_1, vertex_2, vertex_3)

            append_to_indices(-1)  # This is here to get rid of unwanted artifacts

        vbo = self.ctx.buffer(np.array(vertices_and_normals).astype('float32').tobytes())
        ibo = self.ctx.buffer(np.array(indices).astype('int32').tobytes())
        self.vao = self.ctx.vertex_array(
            self.program,
            [(vbo, '3f 3f', 'in_position', 'in_normal')],
            index_buffer=ibo,
            index_element_size=4,
        )

    def init_shaders_variables(self):
        self.tr_matrix = self.program['tr_matrix']
        self.input_color = self.program['obj_color']

    @classmethod
    def add_arguments(cls, parser):
        parser.add_argument('--shader_name', type=str, required=True,
                            help='Name of the shader to look for in the shader_path directory')
        parser.add_argument('--map_name', type=str, required=True, help='Name of the map to load')
        parser.add_argument('--height_scale', type=float, required=False, help='[optional] Floating point number, '
                                                                               'that enables the user to scale the '
                                                                               'height of the map (defaults to 1.0)')

    def render(self, time: float, frame_time: float):
        self.ctx.clear(1.0, 1.0, 1.0, 0.0)
        self.ctx.enable(DEPTH_TEST)
        self.input_color.value = (np.sin(time) / 2 + 0.5, 1.0, 0.0)

        proj = Matrix44.perspective_projection(45.0, self.aspect_ratio, 0.1, 2000.0)

        self.tr_matrix.write((proj * Matrix44.look_at(self.lookat, (0.0, 0.0, 1.0),
                                                      (0.0, 0.0, 1.0), )
                              * Matrix44.from_z_rotation(1 / 10 * 2 * np.pi)
                              * Matrix44.from_translation((-self.x_range / 2, -self.x_range / 2, 1.0))
                              * Matrix44.from_scale((1.0, 1.0, self.height_scale))
                              ).astype('float32'))
        self.vao.render(TRIANGLE_STRIP)

    def mouse_drag_event(self, x, y, dx, dy):
        # rotate camera around the robot
        width, height = self.wnd.size
        if width > height * self.aspect_ratio:
            width = height * self.aspect_ratio
        else:
            height = width / self.aspect_ratio
        scaled_dx = dx * 2.0 / width
        scaled_dy = dy * 2.0 / height
        radius = math.sqrt(self.lookat[0] ** 2 + self.lookat[1] ** 2 + self.lookat[2] ** 2)
        eye_vec4 = Vector4(self.lookat + (1.0,))
        current_angle_horizontal = math.atan2(self.lookat[1], self.lookat[0])
        new_eye = Matrix44.from_eulers((
            -4 * math.sin(current_angle_horizontal) * scaled_dy,
            4 * scaled_dx,
            4 * math.cos(current_angle_horizontal) * scaled_dy
        )) * eye_vec4
        # if camera is near the zenith or nadir, try to limit its "jumping" behavior
        new_radius_horizontal = math.sqrt(new_eye[0] ** 2 + new_eye[1] ** 2)
        if radius > 0.0 and new_radius_horizontal / radius > 0.1:
            self.lookat = tuple(new_eye)[:3]

    def mouse_scroll_event(self, x_offset, y_offset):
        # make the object appear bigger when scrolling up and smaller when scrolling down
        y_offset /= 2
        radius = math.sqrt(self.lookat[0] ** 2 + self.lookat[1] ** 2 + self.lookat[2] ** 2)
        radius *= (1 - y_offset)
        if radius >= 1.0:  # prevent unwanted scene rotation
            self.lookat = (
                self.lookat[0] * (1 - y_offset),
                self.lookat[1] * (1 - y_offset),
                self.lookat[2] * (1 - y_offset)
            )
