import json
import subprocess
import os
import sys
import time

import openai

class AITutor:
    def __init__(self):
        self.client = None
        if os.getenv("OPENAI_API_KEY"):
            self.client = openai.OpenAI()

    def get_advice(self, game_state, lang, user_code):
        if not self.client:
            if "pared" in game_state.message:
                return "Parece que chocaste con una pared. Intenta cambiar la dirección o el número de movimientos."
            elif "llave" in game_state.message:
                return "Necesitas una llave para abrir esa puerta. Asegúrate de recogerla primero."
            elif "Error" in game_state.message:
                return f"Tu código en {lang} tiene un error. Revisa la sintaxis o la lógica."
            return "Hmm, parece que hay un problema. Revisa tu código y el objetivo del nivel."

        prompt = f"""
Eres un tutor de programación para un juego de terminal. El jugador controla un héroe en un laberinto.
Estado: {game_state.to_dict()}
Objetivo: {game_state.goal}
Lenguaje: {lang}
Código: {user_code}
Mensaje: {game_state.message}

Proporciona una pista concisa en español sin dar la solución directa.
"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": "Eres un tutor de programación útil."}, {"role": "user", "content": prompt}],
                max_tokens=100
            )
            return response.choices[0].message.content.strip()
        except:
            return "No pude contactar al asistente AI."

class GameState:
    def __init__(self, level_data):
        self.map = [list(row) for row in level_data["map"]]
        self.hero_pos = level_data["hero_pos"]
        self.items = level_data.get("items", [])
        self.inventory = []
        self.goal = level_data["goal"]
        self.finished = False
        self.message = "¡Bienvenido al nivel!"
        self.score = 0

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
                self.message = "❌ ¡BLOQUEADO! Chocaste con una pared."
            elif cell == "D" and "key" not in self.inventory:
                self.message = "🔒 PUERTA CERRADA. Necesitas una llave (K)."
            else:
                self.hero_pos = [new_x, new_y]
                self.score += 10
                if cell == "K":
                    self.inventory.append("key")
                    self.map[new_y][new_x] = "."
                    self.message = "🔑 ¡LLAVE RECOGIDA! Ahora puedes abrir puertas."
                    self.score += 100
                elif cell == "E":
                    self.finished = True
                    self.message = "🏆 ¡NIVEL COMPLETADO! Excelente trabajo."
                    self.score += 500
                else:
                    self.message = f"✅ Movido a {direction}."
        else:
            self.message = "⚠️ ¡LÍMITE! No puedes salir del mapa."

    def to_dict(self):
        return {"hero_pos": self.hero_pos, "inventory": self.inventory, "map": ["".join(row) for row in self.map]}

class Executor:
    def execute(self, code, state): pass

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
        js_code = f"""
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
        with open("temp.js", "w") as f: f.write(js_code)
        try:
            result = subprocess.run(["node", "temp.js"], capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                for cmd in json.loads(result.stdout): state.move(cmd)
            else: state.message = f"Error de JS: {result.stderr}"
        except Exception as e: state.message = f"Error al ejecutar JS: {e}"

class RustExecutor(Executor):
    def execute(self, code, state):
        rust_code = f"""
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
    for cmd in commands {{ println!("{{}}", cmd); }}
}}
"""
        with open("temp.rs", "w") as f: f.write(rust_code)
        try:
            subprocess.run(["rustc", "temp.rs", "-o", "temp_rust"], capture_output=True, text=True)
            result = subprocess.run(["./temp_rust"], capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                for cmd in result.stdout.strip().split("\n"):
                    if cmd: state.move(cmd)
            else: state.message = f"Error de Rust: {result.stderr}"
        except Exception as e: state.message = f"Error al ejecutar Rust: {e}"

class GoExecutor(Executor):
    def execute(self, code, state):
        go_code = f"""
package main
import "fmt"
type Hero struct {{ commands []string }}
func (h *Hero) MoveUp() {{ h.commands = append(h.commands, "up") }}
func (h *Hero) MoveDown() {{ h.commands = append(h.commands, "down") }}
func (h *Hero) MoveLeft() {{ h.commands = append(h.commands, "left") }}
func (h *Hero) MoveRight() {{ h.commands = append(h.commands, "right") }}
func main() {{
    hero := Hero{{}}
    {code}
    for _, cmd := range hero.commands {{ fmt.Println(cmd) }}
}}
"""
        with open("temp.go", "w") as f: f.write(go_code)
        try:
            result = subprocess.run(["go", "run", "temp.go"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                for cmd in result.stdout.strip().split("\n"):
                    if cmd: state.move(cmd)
            else: state.message = f"Error de Go: {result.stderr}"
        except Exception as e: state.message = f"Error al ejecutar Go: {e}"

class CPPExecutor(Executor):
    def execute(self, code, state):
        cpp_code = f"""
#include <iostream>
#include <vector>
#include <string>
class Hero {{
public:
    std::vector<std::string> commands;
    void move_up() {{ commands.push_back("up"); }}
    void move_down() {{ commands.push_back("down"); }}
    void move_left() {{ commands.push_back("left"); }}
    void move_right() {{ commands.push_back("right"); }}
}};
int main() {{
    Hero hero;
    {code}
    for(const auto& cmd : hero.commands) {{ std::cout << cmd << std::endl; }}
    return 0;
}}
"""
        with open("temp.cpp", "w") as f: f.write(cpp_code)
        try:
            subprocess.run(["g++", "temp.cpp", "-o", "temp_cpp"], capture_output=True, text=True)
            result = subprocess.run(["./temp_cpp"], capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                for cmd in result.stdout.strip().split("\n"):
                    if cmd: state.move(cmd)
            else: state.message = f"Error de C++: {result.stderr}"
        except Exception as e: state.message = f"Error al ejecutar C++: {e}"

class Game:
    def __init__(self):
        self.levels_dir = "/home/ubuntu/skills/polyglot-coding-game/levels"
        self.levels = self.load_levels()
        self.current_level_idx = 0
        self.executors = {
            "python": PythonExecutor(), "javascript": JSExecutor(), 
            "rust": RustExecutor(), "go": GoExecutor(), "cpp": CPPExecutor()
        }
        self.ai_tutor = AITutor()

    def load_levels(self):
        levels = []
        if os.path.exists(self.levels_dir):
            for filename in sorted(os.listdir(self.levels_dir)):
                if filename.endswith(".json"):
                    with open(os.path.join(self.levels_dir, filename), "r") as f:
                        levels.append(json.load(f))
        return levels or [{"name": "Nivel 1", "map": ["#######", "#H...E#", "#######"], "hero_pos": [1, 1], "goal": "Llega a E"}]

    def render(self, state, lang):
        os.system('clear' if os.name == 'posix' else 'cls')
        print("\033[95m╔" + "═"*50 + "╗\033[0m")
        print(f"\033[95m║\033[0m \033[96m🚀 {self.levels[self.current_level_idx]['name']:<46}\033[0m \033[95m║\033[0m")
        print(f"\033[95m║\033[0m \033[93m🎯 Objetivo: {self.levels[self.current_level_idx]['goal']:<44}\033[0m \033[95m║\033[0m")
        print("\033[95m╠" + "═"*50 + "╣\033[0m")
        
        temp_map = [list(row) for row in state.map]
        hx, hy = state.hero_pos
        temp_map[hy][hx] = "\033[92mH\033[0m"
        
        for row in temp_map:
            line = " ".join(row).replace("#", "\033[90m#\033[0m").replace("K", "\033[93mK\033[0m").replace("D", "\033[31mD\033[0m").replace("E", "\033[94mE\033[0m")
            print(f"\033[95m║\033[0m  {line:<48} \033[95m║\033[0m")
        
        print("\033[95m╠" + "═"*50 + "╣\033[0m")
        inv = ', '.join(state.inventory) if state.inventory else 'Vacío'
        print(f"\033[95m║\033[0m 🎒 Inventario: {inv:<35} \033[95m║\033[0m")
        print(f"\033[95m║\033[0m ⭐ Puntuación: {state.score:<36} \033[95m║\033[0m")
        print(f"\033[95m║\033[0m 💬 Mensaje: \033[97m{state.message:<37}\033[0m \033[95m║\033[0m")
        print(f"\033[95m║\033[0m 🛠️  Lenguaje: \033[94m{lang.upper():<37}\033[0m \033[95m║\033[0m")
        print("\033[95m╚" + "═"*50 + "╝\033[0m")

    def play(self):
        os.system('clear')
        print("\033[96m" + r"""
  _____      _             _       _      _____                      
 |  __ \    | |           | |     | |    / ____|                     
 | |__) |__ | |_   _  __ _| | ___ | |_  | |  __  __ _ _ __ ___   ___ 
 |  ___/ _ \| | | | |/ _` | |/ _ \| __| | | |_ |/ _` | '_ ` _ \ / _ \
 | |  | (_) | | |_| | (_| | | (_) | |_  | |__| | (_| | | | | | |  __/
 |_|   \___/|_|\__, |\__, |_|\___/ \__|  \_____|\__,_|_| |_| |_|\___|
                __/ | __/ |                                          
               |___/ |___/                                           
        """ + "\033[0m")
        
        lang = input("\033[93mElige lenguaje (python/javascript/rust/go/cpp): \033[0m").lower()
        if lang not in self.executors: return print("No soportado.")

        level_data = self.levels[self.current_level_idx]
        state = GameState(level_data)
        executor = self.executors[lang]

        while not state.finished:
            self.render(state, lang)
            code = input("\033[92mEscribe tu código (o 'exit'): \033[0m")
            if code.lower() == "exit": break
            executor.execute(code, state)
            if state.message.startswith("❌") or state.message.startswith("Error"):
                advice = self.ai_tutor.get_advice(state, lang, code)
                if advice: print(f"\033[96m🤖 Tutor: {advice}\033[0m"); time.sleep(2)
            
            if state.finished:
                self.render(state, lang)
                print("\033[92m🎉 ¡NIVEL COMPLETADO!\033[0m")
                time.sleep(2)
                self.current_level_idx += 1
                if self.current_level_idx < len(self.levels):
                    state = GameState(self.levels[self.current_level_idx])
                else:
                    print("\033[96m🏆 ¡HAS GANADO EL JUEGO!\033[0m")
                    break

if __name__ == "__main__":
    Game().play()
