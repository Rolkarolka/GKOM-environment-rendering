# GKOM-environment-rendering

Prowadzący: dr inż. Michał Chwesiuk

W ramach projektu należy stworzyć program, który będzie renderował teren
przy wykorzystaniu mapy wysokości.
W tym celu należy zaimplementować następujące punkty:
1. Przygotowanie geometrii środowiska opartą o wczytaną mapę głębokości [Grzesiek]
- Wybór pliku zawierającego mapę głębokości może być zaimplementowana w kodzie, występować jako parametr programu, bądź nazwa pliku wczytywana jest z pliku konfiguracyjnego
2. Geometria powinna zawierać macierz punktów N x M, gdzie M i N to ilość próbek z mapy głębokości. [Grzesiek]
- Punkty powinny być oddalone od siebie we współrzędnych X i Y o stałą odległość, najlepiej definiowaną przez zmienną.
- Współrzędna Z pozycji wierzchołka powinna być wczytywana z mapy głębokości.
- Kolejność renderowania wierzchołków powinna być przekazana do GPU jako Element Buffer Object.
3. Cieniowanie Phong’a [Krzysiek]
4. Kontekstowe teksturowanie [Karolina]
- Przekazanie do shaderów mininum trzech tekstur.
- Pobranie koloru dla wszystkich tekstur w fragment shaderze.
- Wybranie, bądź blending tekstur w zależności od parametrów danego wierzchołka (np. pozycja, wysokość, nachylenie powierzchni itd.)
5. Dodanie do sceny obiektu imitującą wodę [Marianka]
- Geometria wody jako quad rozciągający się na całą scenę.
- Quad powinien mieć naniesioną teksturę wody.
- Opcjonalnie: Teksturę wody można wykorzystać jako normal mapę, zaaplikowaną we fragment shaderze wody.
- Dodać poruszanie się fal wody np. jako dodanie UV do tekstury modyfikowanej z czasem zmiennej uniform.

# Uruchamianie programu

Program jest uruchamiany poprzez wywołanie skryptu `main.py` oraz podanie mu niezbędnych parametrów:
- shader_name - nazwa wybranego shadera
- map_name - nazwa wybranej mapy wysokości

Skrypt przyjmuje też opcjonalne parametry:
- height_scale - odpowiada za skalowanie "górzystości" renderowanego terenu (w szczególności: jej zmniejszanie). Przyjmuje wartości zmiennoprzecinkowe. Domyślnie wynosi `1.0`.

Należy pamiętać, że wszystkie shadery powinny znajdować się w katalogu `resources/shaders/`, natomiast wszystkie mapy wysokości w katalogu `resources/heightmaps/`.

### Przykładowe wywołania programu

`python3 main.py --shader_name phong --map_name heightmap_1`

`python3 main.py --shader_name phong --map_name heightmap_uk_2 --height_scale 0.1`