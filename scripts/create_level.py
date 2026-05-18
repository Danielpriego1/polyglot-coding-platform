import json
import os

LEVELS_DIR = "/home/ubuntu/skills/polyglot-coding-game/levels"
TEMPLATE_PATH = "/home/ubuntu/skills/polyglot-coding-game/templates/level_template.json"

def create_new_level():
    if not os.path.exists(LEVELS_DIR):
        os.makedirs(LEVELS_DIR)

    level_name = input("Introduce el nombre del nuevo nivel (ej. MiPrimerNivel): ")
    if not level_name:
        print("Nombre de nivel no puede estar vacío.")
        return
    
    file_name = f"{level_name.replace(" ", "_")}.json"
    new_level_path = os.path.join(LEVELS_DIR, file_name)

    if os.path.exists(new_level_path):
        print(f"Ya existe un nivel con el nombre {file_name}.")
        return

    try:
        with open(TEMPLATE_PATH, "r") as f:
            template_data = json.load(f)
        
        template_data["name"] = level_name

        with open(new_level_path, "w") as f:
            json.dump(template_data, f, indent=4)
        
        print(f"Nivel '{level_name}' creado exitosamente en {new_level_path}")
        print("Puedes editar este archivo JSON para personalizar el mapa, la posición del héroe, los ítems y el objetivo.")
    except FileNotFoundError:
        print(f"Error: No se encontró la plantilla de nivel en {TEMPLATE_PATH}")
    except Exception as e:
        print(f"Ocurrió un error al crear el nivel: {e}")

if __name__ == "__main__":
    create_new_level()
