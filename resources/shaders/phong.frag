#version 330
out vec3 fr_color;

in vec3 pos;
in vec3 normal;

uniform vec3 viewer_pos = vec3(0, 0, 0);
uniform vec3 light_pos = vec3(-2, -0.7, -30);

uniform vec3 light_color = vec3(1.0, 0.75, 0.8);
uniform vec3 obj_color = vec3(1.0, 0.75, 0.8);
uniform vec3 water_color = vec3(1.0, 0.75, 0.8);

uniform float ambient_factor = 0.1;
uniform float diffuse_factor = 1.0;
uniform float specular_factor = 0.3;

uniform float shininess = 0.2;

uniform sampler2D texture_grass;
uniform sampler2D texture_forest;
uniform sampler2D texture_tree_stone;
uniform sampler2D texture_granite;
uniform sampler2D texture_snow;
uniform sampler2D texture_water;


void main() {
    // Ustawienie ambientu światła dla symulacji
    vec3 ambient = ambient_factor * light_color;

    vec3 norm = normalize(normal);
    // Wyliczanie kierunku padania swiatla
    vec3 light_vector = normalize(light_pos - pos);
    // Wyznaczenie jak mocny ma być efekt rozproszenia światła (w zakresie wartości od 0 do 1)
    float diffuse_param = min(max(dot(norm, light_vector), 0.0), 1.0);
    // Uwzględnienie koloru światła i zadanego współczynnika rozproszenia w symulacji
    vec3 diffuse = diffuse_param * light_color * diffuse_factor;

    // Wyznaczenie kierunku patrzenia na obiekt
    vec3 view_vector = normalize(viewer_pos - pos);
    // Wyznaczenie kierunku, w którym odbije się światło
    vec3 reflect_vector = reflect(-light_vector, norm);
    // Wyznaczenie jak będzie wyglądał efekt odbicia światła na kuli
    float specular_param = pow(min(max(dot(view_vector, reflect_vector), 0.0), 1.0), shininess);
    // Uzwględnienie koloru światła padającego oraz współczynnika zadanego w symulacji
    vec3 specular = specular_param * light_color * specular_factor;
    // Skalowanie tekstury do większych rozmiarów
    vec2 texture_position = vec2(pos[0]/20, pos[1]/20);

    if (pos[2] < 23) {
        vec3 water_texture =  vec3(texture(texture_water, texture_position));
        fr_color = vec3(min(max((ambient + diffuse + water_texture) * (sin(0.5 * (water_color + pos[1])) / 10 + 0.9) + specular, 0.0), 1.0));
    } else if (pos[2] < 40){
        // Dodanie tekstury
        vec3 grass_texture = vec3(texture(texture_grass, texture_position));
        // Połączenie wyników działania wszystkich efektów
        fr_color = vec3(min(max((ambient + diffuse + grass_texture) * obj_color + specular, 0.0), 1.0));
    } else if (pos[2] < 80){
        vec3 forest_texture =  vec3(texture(texture_forest, texture_position));
        fr_color = vec3(min(max((ambient + diffuse + forest_texture) * obj_color + specular, 0.0), 1.0));
    } else if (pos[2] < 160){
        vec3 tree_stone_texture =  vec3(texture(texture_tree_stone, texture_position));
        fr_color = vec3(min(max((ambient + diffuse + tree_stone_texture) * obj_color + specular, 0.0), 1.0));
    } else if (pos[2] < 200){
        vec3 granite_texture =  vec3(texture(texture_granite, texture_position));
        fr_color = vec3(min(max((ambient + diffuse + granite_texture) * obj_color + specular, 0.0), 1.0));
    } else {
        vec3 snow_texture =  vec3(texture(texture_snow, texture_position));
        fr_color = vec3(min(max((ambient + diffuse + snow_texture) * obj_color + specular, 0.0), 1.0));
    }
}