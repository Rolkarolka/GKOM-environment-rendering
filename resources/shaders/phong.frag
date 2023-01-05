#version 330
out vec3 fr_color;

in vec3 pos;
in vec3 normal;

uniform vec3 viewer_pos;
uniform vec3 light_pos = vec3(-2, -0.7, 300);

uniform vec3 light_color = vec3(1, 1, 1);
uniform vec3 obj_color = vec3(0.86, 0.86, 0.86);
uniform vec3 water_color = vec3(1.0, 0.75, 0.8);

uniform float ambient_factor = 0.6;
uniform float diffuse_factor = 1.0;
uniform float specular_factor = 0.1;

uniform float shininess = 0.1;

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
    float diffuse_param = clamp(dot(norm, light_vector), 0.0, 1.0);
    // Uwzględnienie koloru światła i zadanego współczynnika rozproszenia w symulacji
    vec3 diffuse = diffuse_param * light_color * diffuse_factor;

    // Wyznaczenie kierunku patrzenia na obiekt
    vec3 view_vector = normalize(viewer_pos - pos);
    // Wyznaczenie kierunku, w którym odbije się światło
    vec3 reflect_vector = reflect(-light_vector, norm);
    // Wyznaczenie jak będzie wyglądał efekt odbicia światła na kuli
    float specular_param = pow(clamp(dot(view_vector, reflect_vector), 0.0, 1.0), shininess);
    // Uzwględnienie koloru światła padającego oraz współczynnika zadanego w symulacji
    vec3 specular = specular_param * light_color * specular_factor;
    // Skalowanie tekstury do większych rozmiarów
    vec2 texture_position = vec2(pos[0]/20, pos[1]/20);

    vec3 water_texture = vec3(texture(texture_water, texture_position));
    vec3 grass_texture = vec3(texture(texture_grass, texture_position));
    vec3 forest_texture =  vec3(texture(texture_forest, texture_position));
    vec3 tree_stone_texture =  vec3(texture(texture_tree_stone, texture_position));
    vec3 granite_texture =  vec3(texture(texture_granite, texture_position));
    vec3 snow_texture =  vec3(texture(texture_snow, texture_position));

    float water_texture_alpha = 0;
    float grass_texture_alpha = 0;
    float forest_texture_alpha = 0;
    float tree_stone_texture_alpha = 0;
    float granite_texture_alpha = 0;
    float snow_texture_alpha = 0;
    // Połączenie wyników działania wszystkich efektów
    if (pos[2] < 40) {
        grass_texture_alpha = 1.0;
    } else if (pos[2] < 60) {
        grass_texture_alpha = (60.0 - pos[2]) / 20.0;
        forest_texture_alpha = (pos[2] - 40.0)/ 20.0;
    } else if (pos[2] < 80) {
        forest_texture_alpha = 1.0;
    } else if (pos[2] < 120) {
        forest_texture_alpha = (120.0 - pos[2]) / 40.0;
        tree_stone_texture_alpha = (pos[2] - 80.0) / 40.0;
    } else if (pos[2] < 160) {
        tree_stone_texture_alpha = 1.0;
    } else if (pos[2] < 180) {
        tree_stone_texture_alpha = (180.0 - pos[2]) / 20.0;
        granite_texture_alpha = (pos[2] - 160.0) / 20.0;
    } else if (pos[2] < 200) {
        granite_texture_alpha = 1.0;
    } else if (pos[2] < 220) {
        granite_texture_alpha = (220.0 - pos[2]) / 20.0;
        snow_texture_alpha = (pos[2] - 200.0) / 20.0;
    } else {
        snow_texture_alpha = 1.0;
    }

    float alpha_sum = grass_texture_alpha + forest_texture_alpha + tree_stone_texture_alpha + granite_texture_alpha +
                    snow_texture_alpha;
    grass_texture_alpha /= alpha_sum;
    forest_texture_alpha /= alpha_sum;
    tree_stone_texture_alpha /= alpha_sum;
    granite_texture_alpha /= alpha_sum;
    snow_texture_alpha /= alpha_sum;

    vec3 final_texture = vec3(grass_texture * grass_texture_alpha) +
                        vec3(forest_texture * forest_texture_alpha) +
                        vec3(tree_stone_texture * tree_stone_texture_alpha) +
                        vec3(granite_texture * granite_texture_alpha) +
                        vec3(snow_texture * snow_texture_alpha);

    if (pos[2] < 23) {
        fr_color = vec3(clamp(
            (ambient + diffuse) * water_texture * (0.15 * sin(0.5 * (water_color + pos[1])) + 0.85) + specular,
            0.0, 1.0));
    }
    else {
        fr_color = vec3(clamp((ambient + diffuse) * final_texture * obj_color + specular, 0.0, 1.0));
    }
}