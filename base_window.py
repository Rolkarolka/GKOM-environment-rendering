import math
from argparse import ArgumentParser
from enum import IntEnum
from pathlib import Path

import imageio
import numpy as np
from _moderngl import Uniform
from moderngl import DEPTH_TEST, TRIANGLE_STRIP, Program, Buffer, VertexArray, Texture
from moderngl_window import WindowConfig
from numpy import ndarray, uint8
from pyrr import Matrix44, Vector4

from shader_utils import get_shaders, ShaderCollection


class MainWindowConfig(WindowConfig):
    gl_version: tuple[int, int] = (3, 3)
    title: str = 'Environment Rendering'
    resource_dir: Path = (Path(__file__).parent / 'resources').resolve()

    def __init__(self, **kwargs: dict[str, dict]) -> None:
        super(MainWindowConfig, self).__init__(**kwargs)

        shaders: dict[str, ShaderCollection] = get_shaders()
        self.program: Program = self.ctx.program(vertex_shader=shaders[self.argv.shader_name].vertex_shader,
                                                 fragment_shader=shaders[self.argv.shader_name].fragment_shader)

        self.height_scale: float = self.argv.height_scale if self.argv.height_scale is not None else 0.3

        self.sea_level: int = 23

        self.load_png_heightmap(self.argv.map_name)
        self.load_textures()
        self.generate_terrain()
        self.init_shaders_variables()

        self.viewer_pos: tuple[float, float, float] = (
            -self.x_range * 3 / 4, -self.y_range * 3 / 4, (self.x_range + self.y_range) / 3)

    def load_png_heightmap(self, map_name: str) -> None:
        raw_heightmap: ndarray = imageio.v3.imread(f"./resources/heightmaps/{map_name}.png")
        self.x_range: int = self.argv.N if self.argv.N is not None else 200
        self.y_range: int = self.argv.M if self.argv.M is not None else 200

        self.height_map: ndarray = np.empty([self.x_range, self.y_range, 3])
        x_factor: float = raw_heightmap.shape[0] / self.x_range
        y_factor: float = raw_heightmap.shape[1] / self.y_range
        for x_i in range(self.x_range):
            for y_i in range(self.y_range):
                # this is necessary because png files can store colours as rgb or grayscale values, which creates issues
                x: int = round(x_i * x_factor)
                y: int = round(y_i * y_factor)
                z_val: uint8 = raw_heightmap[x][y] if len(raw_heightmap.shape) == 2 else raw_heightmap[x][y][0]
                self.height_map[x_i][y_i] = np.array([x_i, y_i, z_val])

    def load_texture(self, texture_name: str, location: int) -> None:
        texture: Texture = self.load_texture_2d(f"./textures/{texture_name}.jpg")
        texture.use(location)

    def load_textures(self) -> None:
        class Textures(IntEnum):
            GRASS = 0,
            FOREST = 1,
            TREE_STONE = 2,
            GRANITE = 3,
            SNOW = 4,
            WATER = 5

        self.program["texture_grass"] = Textures.GRASS
        self.load_texture("grass", Textures.GRASS)

        self.program["texture_forest"] = Textures.FOREST
        self.load_texture("forest", Textures.FOREST)

        self.program["texture_tree_stone"] = Textures.TREE_STONE
        self.load_texture("forest_tree_stone", Textures.TREE_STONE)

        self.program["texture_granite"] = Textures.GRANITE
        self.load_texture("granite", Textures.GRANITE)

        self.program["texture_snow"] = Textures.SNOW
        self.load_texture("snow", Textures.SNOW)

        self.program["texture_water"] = Textures.WATER
        self.load_texture("water", Textures.WATER)

    def generate_terrain(self) -> None:
        vertices: ndarray = np.empty([self.x_range * self.y_range, 3])
        vertices_and_normals: ndarray = np.empty([self.x_range * self.y_range, 6])
        indices: ndarray = np.empty([3 * 2 * (self.x_range - 1) * (self.y_range - 1) + self.y_range - 1])

        def append_to_indices(vertex: int) -> None:
            indices[append_to_indices.counter] = vertex
            append_to_indices.counter += 1

        append_to_indices.counter = 0

        sea_bottom = self.sea_level - 3

        for x_i in range(self.x_range):
            for y_i in range(self.y_range):
                self.height_map[x_i][y_i][2] = max(self.height_map[x_i][y_i][2], sea_bottom)
                v_idx: int = y_i * self.x_range + x_i
                vertices[v_idx] = self.height_map[x_i][y_i]
                vertices_and_normals[v_idx] = [*self.height_map[x_i][y_i], 0, 0, 0]

        def create_triangle(v1: int, v2: int, v3: int) -> None:
            append_to_indices(v1)
            append_to_indices(v2)
            append_to_indices(v3)
            edge_1: ndarray = vertices[v2] - vertices[v1]
            edge_2: ndarray = vertices[v3] - vertices[v1]
            cross: ndarray = np.cross(edge_1, edge_2)

            for vertex in [v1, v2, v3]:
                for i in range(3):
                    vertices_and_normals[vertex][3 + i] += cross[i]

        for x_i in range(self.x_range - 1):
            for y_i in range(self.y_range - 1):
                # create two triangles forming a quadrangle (sorta, if you ignore the z-values)
                vertex_1: int = x_i + y_i * self.x_range
                vertex_2: int = x_i + 1 + y_i * self.x_range
                vertex_3: int = x_i + (y_i + 1) * self.x_range
                create_triangle(vertex_1, vertex_2, vertex_3)

                vertex_1 = x_i + 1 + y_i * self.x_range
                vertex_2 = x_i + 1 + (y_i + 1) * self.x_range
                vertex_3 = x_i + (y_i + 1) * self.x_range
                create_triangle(vertex_1, vertex_2, vertex_3)

            append_to_indices(-1)  # This is here to get rid of unwanted artifacts

        vbo: Buffer = self.ctx.buffer(np.array(vertices_and_normals).astype('float32').tobytes())
        ibo: Buffer = self.ctx.buffer(np.array(indices).astype('int32').tobytes())
        self.vao: VertexArray = self.ctx.vertex_array(
            self.program,
            [(vbo, '3f 3f', 'in_position', 'in_normal')],
            index_buffer=ibo,
            index_element_size=4,
        )

    def init_shaders_variables(self) -> None:
        self.tr_matrix: Uniform = self.program['tr_matrix']
        self.input_color: Uniform = self.program['obj_color']
        self.water_color: Uniform = self.program['water_color']


    @classmethod
    def add_arguments(cls, parser: ArgumentParser) -> None:
        parser.add_argument('--shader_name', type=str, required=True,
                            help='Name of the shader to look for in the shader_path directory')
        parser.add_argument('--map_name', type=str, required=True, help='Name of the map to load')
        parser.add_argument('--height_scale', type=float, required=False, help='[optional] Floating point number, '
                                                                               'that enables the user to scale the '
                                                                               'height of the map (defaults to 1.0)')
        parser.add_argument('-N', type=int, required=False, help='[optional] Length of the map')
        parser.add_argument('-M', type=int, required=False, help='[optional] Width of the map')

    def render(self, time: float, frame_time: float) -> None:
        self.ctx.clear(1.0, 1.0, 1.0, 0.0)
        self.ctx.enable(DEPTH_TEST)
        self.input_color.value = (0.75, 0.75, 0.75)
        waves_speed: float = 7
        self.water_color.value = (waves_speed * time, waves_speed * time, waves_speed * time)

        proj: Matrix44 = Matrix44.perspective_projection(45.0, self.aspect_ratio, 0.1, 2000.0)

        self.tr_matrix.write((proj * Matrix44.look_at(self.viewer_pos, (0.0, 0.0, 1.0),
                                                      (0.0, 0.0, 1.0), )
                              * Matrix44.from_z_rotation(1 / 10 * 2 * np.pi)
                              * Matrix44.from_translation((-self.x_range / 2, -self.x_range / 2, 1.0))
                              * Matrix44.from_scale((1.0, 1.0, self.height_scale))
                              ).astype('float32'))
        self.vao.render(TRIANGLE_STRIP)

    def mouse_drag_event(self, x: int, y: int, dx: int, dy: int) -> None:
        width, height = self.wnd.size
        if width > height * self.aspect_ratio:
            width = height * self.aspect_ratio
        else:
            height = width / self.aspect_ratio
        scaled_dx: float = dx * 2.0 / width
        scaled_dy: float = dy * 2.0 / height
        radius: float = math.sqrt(self.viewer_pos[0] ** 2 + self.viewer_pos[1] ** 2 + self.viewer_pos[2] ** 2)
        eye_vec4: Vector4 = Vector4(self.viewer_pos + (1.0,))
        current_angle_horizontal: float = math.atan2(self.viewer_pos[1], self.viewer_pos[0])
        new_eye: Vector4 = Matrix44.from_eulers((
            -4 * math.sin(current_angle_horizontal) * scaled_dy,
            4 * scaled_dx,
            4 * math.cos(current_angle_horizontal) * scaled_dy
        )) * eye_vec4
        # if camera is near the zenith or nadir, try to limit its "jumping" behavior
        new_radius_horizontal: float = math.sqrt(new_eye[0] ** 2 + new_eye[1] ** 2)
        if radius > 0.0 and new_radius_horizontal / radius > 0.1 and tuple(new_eye)[2] > self.sea_level:
            self.viewer_pos = tuple(new_eye)[:3]

    def mouse_scroll_event(self, x_offset: float, y_offset: float) -> None:
        # make the object appear bigger when scrolling up and smaller when scrolling down
        y_offset /= 2
        radius: float = math.sqrt(self.viewer_pos[0] ** 2 + self.viewer_pos[1] ** 2 + self.viewer_pos[2] ** 2)
        radius *= (1 - y_offset)
        viewer_pos: tuple[float, float, float] = (
                self.viewer_pos[0] * (1 - y_offset),
                self.viewer_pos[1] * (1 - y_offset),
                (self.viewer_pos[2] - self.sea_level) * (1 - y_offset) + self.sea_level
            )
        if radius >= 1.0 and viewer_pos[2] > self.sea_level:  # prevent unwanted scene rotation
            self.viewer_pos = viewer_pos
