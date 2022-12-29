import os
from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class ShaderCollection:
    fragment_shader: str = None
    vertex_shader: str = None

    def assign_shader(self, extension: str, shader_text: str) -> None:
        if extension in ['.frag']:
            self.fragment_shader = shader_text

        if extension in ['.vert']:
            self.vertex_shader = shader_text

    def is_valid_collection(self) -> str:
        return self.vertex_shader and self.fragment_shader


def _gather_shader_files(shader_directory_path: str) -> dict[str, list[str]]:
    file_names: list[str] = os.listdir(shader_directory_path)

    shaders: dict[str, list[str]] = {}

    for file_name in file_names:
        basename: str = os.path.splitext(file_name)[0]
        shaders.setdefault(basename, [])
        shaders[basename].append(os.path.join(shader_directory_path, file_name))

    return shaders


def _load_shader(shader_path: str) -> str:
    with open(shader_path) as f:
        shader_text: str = f.read()

    return shader_text


def get_shaders() -> dict[str, ShaderCollection]:
    shaders: dict[str, ShaderCollection] = {}
    gathered_files: dict[str, list[str]] = _gather_shader_files("./resources/shaders/")

    for identifier, shader_path_list in gathered_files.items():
        shader_collection: ShaderCollection = ShaderCollection()

        for shader_path in shader_path_list:
            extension: str = os.path.splitext(shader_path)[1]
            shader_text: str = _load_shader(shader_path)
            shader_collection.assign_shader(extension, shader_text)

        if not shader_collection.is_valid_collection():
            raise RuntimeError('Missing vertex or fragment shader')

        shaders[identifier] = shader_collection

    return shaders
