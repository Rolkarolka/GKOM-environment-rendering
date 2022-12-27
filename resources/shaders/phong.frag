#version 330
out vec3 fr_color;

in vec3 pos;
in vec3 normal;

uniform vec3 viewer_pos = vec3(0, 0, 0);
uniform vec3 light_pos = vec3(-2, -0.7, -30);

uniform vec3 light_color = vec3(1.0, 0.75, 0.8);
uniform vec3 obj_color = vec3(1.0, 0.75, 0.8);

uniform float ambient_factor = 0.1;
uniform float diffuse_factor = 1.0;
uniform float specular_factor = 0.3;

uniform float shininess = 0.2;

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

    // Połączenie wyników działania wszystkich efektów
    fr_color = vec3(min(max((ambient + diffuse) * obj_color + specular, 0.0), 1.0));
}