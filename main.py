"""
Kivy app folder structure generator

MIT License

Copyright (c) 2020 KrYmZiN

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

__version__ = "0.1"
from os import system, name, getcwd, path, makedirs
import sys


class Main:
    use_md = 'md'
    cwd = ""
    screen_count = 1
    screens = []
    user_inputs = {"App": ""}

    def __init__(self):
        if __name__ != "__main__":
            return

        # ----- Basic Information -----
        self.cwd = getcwd()

        self.clear_screen()

        print(f"\nKivy app folder structure generator version {__version__}\n")
        if input(f"Proceed generating folder structure in directory {self.cwd}? [Y/n]: ").lower() == 'n':
            return

        self.clear_screen()

        app_path = path.join(self.cwd, 'app')
        if path.isdir(app_path):
            print('App folder already exists.')
            input()
            return
        # -----------------------------

        # --------- Questions ---------
        if input("Use kivyMD? [Y/n]: ").lower() == 'n':
            self.use_md = ''

        self.clear_screen()

        while True:
            try:
                if int((screen_count_input := input("Number of screens (int): "))) < 1 or int(screen_count_input) > 24:
                    self.clear_screen()
                    print("Please enter a valid number of screens.")
                    continue
                self.screen_count = int(screen_count_input)
                self.clear_screen()
                break
            except BaseException:
                if screen_count_input == "":
                    self.clear_screen()
                    break
                self.clear_screen()
                print("Please enter a valid number of screens.")

        for screen in range (1, self.screen_count+1):
            self.user_inputs[f"Screen {screen}"] = ""

        for i in self.user_inputs:
            while True:
                self.user_inputs[i] = input(f"{i} name: ").strip()
                self.clear_screen()
                if not self.validate_string(self.user_inputs.get(i)):
                    print(f"Invalid {i.lower()} name.")
                    continue
                break

        for screen in range (1, self.screen_count+1):
            self.screens.append(self.user_inputs.get(f"Screen {screen}"))
        # -----------------------------

        # ----- Generate structure ----
        mainpy_content = self.get_main_content()
        screen_py_files = self.get_py_content()
        screen_kv_files = self.get_kv_content()

        makedirs(app_path)

        with open(path.join(app_path, 'main.py'), 'w') as f:
            f.write(mainpy_content)

        for i in range(1, self.screen_count+1):
            filename = self.format_string(self.user_inputs.get(f"Screen {i}"), False)
            makedirs(path.join(app_path, 'screens', filename))
            with open(path.join(app_path, 'screens', filename, f'{filename}.py'), 'w') as py:
                py.write(screen_py_files[i-1])
            with open(path.join(app_path, 'screens', filename, f'{filename}.kv'), 'w') as kv:
                kv.write(screen_kv_files[i-1])

        print('Generated folder structure successfully.')
        input()
        return
        # -----------------------------

    def validate_string(self, key):
        chars = "abcdefghijklmnopqrstuvwxyz1234567890 "
        if any(not(ele in chars) for ele in key.lower()):
            return False
        if key[0].isdigit():
            return False
        if len(key) < 1 and len(key) > 248:
            return False
        return True

    def format_string(self, key, camel=True):
        if not any(ele.isupper() for ele in key) and camel:
            key = key.title()
        return key.replace(" ", "") if camel else key.replace(" ", "_").lower()

    def clear_screen(self):
        if name == 'nt': 
            system('cls') 
        else: 
            system('clear') 

    def resource_path(self, relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = path.abspath(path.dirname(sys.argv[0]))

        return path.join(base_path, relative_path)

    def get_py_content(self):
        pytmpl = open(self.resource_path(f"screen{self.use_md}.tmpl"), "r", encoding="utf8")
        py_content = pytmpl.read()
        pytmpl.close()
        screen_py_files = []
        for screen in self.screens:
            screen_py_files.append(py_content.format(screen_camel=self.format_string(screen), screen_snake=self.format_string(screen, False)))
        return screen_py_files

    def get_kv_content(self):
        kvtmpl = open(self.resource_path(f"screenkv{self.use_md}.tmpl"), "r", encoding="utf8")
        kv_content = kvtmpl.read()
        kvtmpl.close()
        screen_kv_files = []
        for screen in self.screens:
            screen_kv_files.append(kv_content.format(screen_camel=self.format_string(screen), screen_snake=self.format_string(screen, False)))
        return screen_kv_files

    def get_main_content(self):
        maintmpl = open(self.resource_path(f"main{self.use_md}.tmpl"), "r", encoding="utf8")
        app = self.user_inputs.get("App")
        app_camel = self.format_string(app)
        resource_add_paths = ""
        screen_imports = ""
        screen_class_definitions = ""
        screens_dict = ""
        first_screen = self.format_string(self.user_inputs.get(f"Screen 1"), False)
        for screen in self.screens:
            screen_snake = self.format_string(screen, False)
            resource_add_paths += f"resource_add_path(resource_path(os.path.join('screens', '{screen_snake}')))\n"
            screen_imports += f"from screens.{screen_snake} import {screen_snake}\n        "
            screen_class_definitions += f"self.{screen_snake} = {screen_snake}.{self.format_string(screen)}()\n        "
            screens_dict += f'"{screen_snake}": self.{screen_snake},\n            '
        mainpy = maintmpl.read().format(
            app_camel=app_camel,
            app_name=app,
            resource_add_paths=resource_add_paths.strip(),
            screen_imports=screen_imports.strip(),
            screen_class_definitions=screen_class_definitions.strip(),
            screens_dict=screens_dict.strip(),
            first_screen=first_screen,
        )
        maintmpl.close()
        return mainpy


Main()
