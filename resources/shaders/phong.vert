#version 330

in vec3 in_position;
in vec3 in_normal;

out vec3 pos;
out vec3 normal;

uniform mat4 tr_matrix;

void main()
{
    pos = in_position;
    normal = in_normal;
    gl_Position = tr_matrix * vec4(in_position, 1.0);
}
