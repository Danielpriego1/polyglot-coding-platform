import json
import subprocess
import os
import sys

import openai

class AITutor:
    def __init__(self):
        self.client = None
        if os.getenv("OPENAI_API_KEY"):
            self.client = openai.OpenAI()

    def get_advice(self, game_state, lang, user_code):
        if not self.client:
            # Simular respuesta si no hay API key
            if "pared" in game_state.message:
                return "Parece que chocaste con una pared. Intenta cambiar la dirección o el número de movimientos."
            elif "llave" in game_state.message:
                return "Necesitas una llave para abrir esa puerta. Asegúrate de recogerla primero."
            elif "Error" in game_state.message:
                return f"Tu código en {lang} tiene un error. Revisa la sintaxis o la lógica. Recuerda que en {lang} los comandos son case-sensitive."
            return "Hmm, parece que hay un problema. Revisa tu código y el objetivo del nivel."

        # Si hay API key, usar el LLM
        prompt = f"""
Eres un tutor de programación para un juego de terminal. El jugador controla un héroe en un laberinto.
El estado actual del juego es: {game_state.to_dict()}
El objetivo del nivel es: {game_state.goal}
El lenguaje de programación que está usando el jugador es: {lang}
El último código que el jugador intentó ejecutar fue: {user_code}
El mensaje de error o estado actual del juego es: {game_state.message}

Por favor, proporciona una pista o consejo educativo al jugador. NO le des la solución directa. Enfócate en guiarlo para que aprenda del error o mejore su código. Mantén la respuesta concisa y en español.
"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini", # Usar un modelo ligero para feedback rápido
                messages=[
                    {"role": "system", "content": "Eres un tutor de programación útil y paciente."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error al llamar a la API de OpenAI: {e}")
            return "No pude contactar al asistente AI. Revisa tu conexión o la API Key."

class GameState:
    def __init__(self, level_data):
        self.map = [list(row) for row in level_data["map"]]
        self.hero_pos = level_data["hero_pos"]
        self.items = level_data["items"]
        self.inventory = []
        self.goal = level_data["goal"]
        self.finished = False
        self.message = ""

    def move(self, direction):
        x, y = self.hero_pos
        dx, dy = 0, 0
        if direction == "up": dy = -1
        elif direction == "down": dy = 1
        elif direction == "left": dx = -1
        elif direction == "right": dx = 1
        
        new_x, new_y = x + dx, y + dy
        if 0 <= new_y < len(self.map) and 0 <= new_x < len(self.map[0]):
            cell = self.map[new_y][new_x]
            if cell == "#":
                self.message = "¡Chocaste con una pared!"
            elif cell == "D" and "key" not in self.inventory:
                self.message = "La puerta está cerrada. Necesitas una llave."
            else:
                self.hero_pos = [new_x, new_y]
                if cell == "K":
                    self.inventory.append("key")
                    self.map[new_y][new_x] = "."
                    self.message = "¡Recogiste una llave!"
                elif cell == "E":
                    self.finished = True
                    self.message = "¡Nivel completado!"
                else:
                    self.message = f"Movido a {direction}"
        else:
            self.message = "¡Fuera de los límites!"

    def to_dict(self):
        return {
            "hero_pos": self.hero_pos,
            "inventory": self.inventory,
            "map": ["".join(row) for row in self.map]
        }

class Executor:
    def execute(self, code, state):
        pass

class PythonExecutor(Executor):
    def execute(self, code, state):
        class Hero:
            def __init__(self, state): self.state = state
            def move_up(self): self.state.move("up")
            def move_down(self): self.state.move("down")
            def move_left(self): self.state.move("left")
            def move_right(self): self.state.move("right")

        hero = Hero(state)
        try:
            exec(code, {"hero": hero, "print": lambda *args: None})
        except Exception as e:
            state.message = f"Error de Python: {e}"

class JSExecutor(Executor):
    def execute(self, code, state):
        # Generar un script temporal que simule el objeto hero
        js_code = f"""
const state = {json.dumps(state.to_dict())};
const commands = [];
const hero = {{
    move_up: () => commands.push("up"),
    move_down: () => commands.push("down"),
    move_left: () => commands.push("left"),
    move_right: () => commands.push("right")
}};
{code}
console.log(JSON.stringify(commands));
"""
        with open("temp.js", "w") as f:
            f.write(js_code)
        
        try:
            result = subprocess.run(["node", "temp.js"], capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                commands = json.loads(result.stdout)
                for cmd in commands:
                    state.move(cmd)
            else:
                state.message = f"Error de JS: {result.stderr}"
        except Exception as e:
            state.message = f"Error al ejecutar JS: {e}"

class RustExecutor(Executor):
    def execute(self, code, state):
        # Rust es más complejo porque requiere compilación. 
        # Usaremos un enfoque de "scripting" con rustc para rapidez en el prototipo.
        rust_code = f"""
use std::collections::VecDeque;

struct Hero {{
    commands: Vec<String>,
}}

impl Hero {{
    fn move_up(&mut self) {{ self.commands.push("up".to_string()); }}
    fn move_down(&mut self) {{ self.commands.push("down".to_string()); }}
    fn move_left(&mut self) {{ self.commands.push("left".to_string()); }}
    fn move_right(&mut self) {{ self.commands.push("right".to_string()); }}
}}

fn main() {{
    let mut hero = Hero {{ commands: vec![] }};
    {code}
    println!("{{}}", serde_json::to_string(&hero.commands).unwrap());
}}
"""
        # Nota: Para que esto funcione necesitamos serde_json, lo cual complica el script simple.
        # Simplificaremos la salida para el prototipo de Rust.
        rust_code_simple = f"""
fn main() {{
    let mut commands = Vec::new();
    {{
        let mut move_up = || commands.push("up");
        let mut move_down = || commands.push("down");
        let mut move_left = || commands.push("left");
        let mut move_right = || commands.push("right");
        
        macro_rules! move_up {{ () => {{ move_up() }} }}
        macro_rules! move_down {{ () => {{ move_down() }} }}
        macro_rules! move_left {{ () => {{ move_left() }} }}
        macro_rules! move_right {{ () => {{ move_right() }} }}

        {code}
    }}
    for cmd in commands {{
        println!("{{}}", cmd);
    }}
}}
"""
        with open("temp.rs", "w") as f:
            f.write(rust_code_simple)
        
        try:
            subprocess.run(["rustc", "temp.rs", "-o", "temp_rust"], capture_output=True, text=True)
            result = subprocess.run(["./temp_rust"], capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                commands = result.stdout.strip().split("\n")
                for cmd in commands:
                    if cmd: state.move(cmd)
            else:
                state.message = f"Error de Rust: {result.stderr}"
        except Exception as e:
            state.message = f"Error al ejecutar Rust: {e}"

import requests

class Game:
    def __init__(self, mode="local", api_url=None):
        self.mode = mode # "local" o "remote"
        self.api_url = api_url
        self.levels_dir = "/home/ubuntu/skills/polyglot-coding-game/levels"
        self.levels = self.load_levels()
        self.current_level_idx = 0
        self.executors = {
            "python": PythonExecutor(),
            "javascript": JSExecutor(),
            "rust": RustExecutor(),
            "go": GoExecutor(),
            "cpp": CPPExecutor()
        }
        self.ai_tutor = AITutor()

    def execute_remote(self, lang, code, state):
        """Envía el código al backend de InsForge en el VPS."""
        try:
            response = requests.post(
                f"{self.api_url}/functions/execute_{lang}",
                json={"code": code, "state": state.to_dict()},
                timeout=10
            )
            if response.status_code == 200:
                result = response.json()
                # Aquí se actualizaría el estado local con la respuesta del servidor
                state.message = result.get("message", "Ejecutado remotamente")
            else:
                state.message = f"Error en servidor remoto: {response.status_code}"
        except Exception as e:
            state.message = f"Error de conexión con VPS: {e}"

    def load_levels(self):
        levels = []
        if os.path.exists(self.levels_dir):
            for filename in sorted(os.listdir(self.levels_dir)):
                if filename.endswith(".json"):
                    try:
                        with open(os.path.join(self.levels_dir, filename), "r") as f:
                            levels.append(json.load(f))
                    except Exception as e:
                        print(f"Error al cargar nivel {filename}: {e}")
        
        # Niveles por defecto si no hay archivos
        if not levels:
            levels = [
                {
                    "name": "Nivel 1: El Comienzo (Default)",
                    "map": ["#######", "#H...E#", "#######"],
                    "hero_pos": [1, 1],
                    "items": [],
                    "goal": "Llega a la salida E."
                }
            ]
        return levels

    def render(self, state, lang):
        os.system('clear' if os.name == 'posix' else 'cls')
        print("\033[95m" + "="*40 + "\033[0m")
        print(f"\033[96m🚀 {self.levels[self.current_level_idx]['name']}\033[0m")
        print(f"\033[93m🎯 Objetivo: {self.levels[self.current_level_idx]['goal']}\033[0m")
        print("\033[95m" + "="*40 + "\033[0m")
        
        temp_map = [list(row) for row in state.map]
        hx, hy = state.hero_pos
        temp_map[hy][hx] = "\033[92mH\033[0m" # Héroe en verde
        
        for row in temp_map:
            line = " ".join(row)
            line = line.replace("#", "\033[90m#\033[0m") # Paredes gris
            line = line.replace("K", "\033[93mK\033[0m") # Llave amarillo
            line = line.replace("D", "\033[31mD\033[0m") # Puerta rojo
            line = line.replace("E", "\033[94mE\033[0m") # Salida azul
            print(line)
        
        print("\033[95m" + "-"*40 + "\033[0m")
        print(f"🎒 Inventario: {', '.join(state.inventory) if state.inventory else 'Vacío'}")
        print(f"💬 Mensaje: \033[97m{state.message}\033[0m")
        print(f"🛠️  Lenguaje: \033[94m{lang.upper()}\033[0m")
        print("\033[95m" + "="*40 + "\033[0m")

    def get_educational_tip(self, lang):
        tips = {
            "python": "Tip: En Python, puedes usar 'for i in range(3):' para repetir acciones.",
            "javascript": "Tip: En JS, puedes usar 'for(let i=0; i<3; i++) { ... }' para bucles.",
            "rust": "Tip: En Rust, las macros terminan en \'!\', como \'move_right!();\'.",
            "go": "Tip: En Go, los nombres de funciones públicas empiezan con mayúscula, como \'hero.MoveRight()\'.",
            "cpp": "Tip: En C++, las sentencias terminan con punto y coma, como \'hero.move_right();\'."
        }
        return tips.get(lang, "")

    def play(self):
        lang = input("Elige lenguaje (python/javascript/rust): ").lower()
        if lang not in self.executors:
            print("Lenguaje no soportado.")
            return

        print("\n--- Selecciona un Nivel ---")
        for i, level in enumerate(self.levels):
            print(f"{i+1}. {level["name"]}")
        
        while True:
            try:
                choice = int(input("Elige un número de nivel: ")) - 1
                if 0 <= choice < len(self.levels):
                    self.current_level_idx = choice
                    break
                else:
                    print("Opción inválida. Intenta de nuevo.")
            except ValueError:
                print("Entrada inválida. Por favor, ingresa un número.")

        level_data = self.levels[self.current_level_idx]
        state = GameState(level_data)
        executor = self.executors[lang]

        while not state.finished:
            self.render(state, lang)
            print(f"\033[90m{self.get_educational_tip(lang)}\033[0m")
            print(f"Escribe tu código en {lang}:")
            
            if state.message.startswith("Error"):
                ai_advice = self.ai_tutor.get_advice(state, lang, code)
                if ai_advice:
                    print(f"\033[96m🤖 Asistente AI: {ai_advice}\033[0m")
            
            code = input("\033[92m>>> \033[0m")
            if code.lower() == "exit": break
            
            if self.mode == "remote":
                self.execute_remote(lang, code, state)
            else:
                executor.execute(code, state)
            
            if state.finished:
                self.render(state, lang)
                print("\033[92m🎉 ¡Felicidades! Has superado el nivel.\033[0m")
                input("Presiona Enter para continuar al siguiente nivel o salir...")
                self.current_level_idx += 1
                if self.current_level_idx < len(self.levels):
                    # Reiniciar el juego con el siguiente nivel
                    self.play() 
                else:
                    print("\033[96m🏆 ¡Has completado todos los niveles disponibles!\033[0m")
                    break

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Juego de Codificación Políglota")
    parser.add_argument("--mode", choices=["local", "remote"], default="local", help="Modo de ejecución")
    parser.add_argument("--api", help="URL de la API de InsForge (requerido para modo remote)")
    
    args = parser.parse_args()
    
    if args.mode == "remote" and not args.api:
        print("Error: Debes proporcionar la URL de la API (--api) para el modo remoto.")
        sys.exit(1)
        
    game = Game(mode=args.mode, api_url=args.api)
    game.play()

class GoExecutor(Executor):
    def execute(self, code, state):
        go_code = f"""
package main

import (
	"fmt"
)

type Hero struct {
	commands []string
}

func (h *Hero) MoveUp()    { h.commands = append(h.commands, "up") }
func (h *Hero) MoveDown()  { h.commands = append(h.commands, "down") }
func (h *Hero) MoveLeft()  { h.commands = append(h.commands, "left") }
func (h *Hero) MoveRight() { h.commands = append(h.commands, "right") }

func main() {
	hero := Hero{}
	// User code starts here
	{code}
	// User code ends here
	for _, cmd := range hero.commands {
		fmt.Println(cmd)
	}
}
"""
        with open("temp.go", "w") as f:
            f.write(go_code)
        
        try:
            result = subprocess.run(["go", "run", "temp.go"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                commands = result.stdout.strip().split("\n")
                for cmd in commands:
                    if cmd: state.move(cmd)
            else:
                state.message = f"Error de Go: {result.stderr}"
        except Exception as e:
            state.message = f"Error al ejecutar Go: {e}"

class CPPExecutor(Executor):
    def execute(self, code, state):
        cpp_code = f"""
#include <iostream>
#include <vector>
#include <string>

class Hero {
public:
    std::vector<std::string> commands;
    void move_up()    { commands.push_back("up"); }
    void move_down()  { commands.push_back("down"); }
    void move_left()  { commands.push_back("left"); }
    void move_right() { commands.push_back("right"); }
};

int main() {
    Hero hero;
    // User code starts here
    {code}
    // User code ends here
    for (const std::string& cmd : hero.commands) {
        std::cout << cmd << std::endl;
    }
    return 0;
}
"""
        with open("temp.cpp", "w") as f:
            f.write(cpp_code)
        
        try:
            compile_result = subprocess.run(["g++", "temp.cpp", "-o", "temp_cpp"], capture_output=True, text=True, timeout=10)
            if compile_result.returncode != 0:
                state.message = f"Error de compilación C++: {compile_result.stderr}"
                return
            
            run_result = subprocess.run(["./temp_cpp"], capture_output=True, text=True, timeout=5)
            if run_result.returncode == 0:
                commands = run_result.stdout.strip().split("\n")
                for cmd in commands:
                    if cmd: state.move(cmd)
            else:
                state.message = f"Error de ejecución C++: {run_result.stderr}"
        except Exception as e:
            state.message = f"Error al ejecutar C++: {e}"
