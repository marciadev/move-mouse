import json
import os
import sys

class SettingsManager:
    def __init__(self, filename="config.json"):
        self.filename = filename
        self.defaults = {
            "interval_s": 30,
            "action_type": "move",  # move, click, key
            "opacity": 1.0,
            "auto_start": False,
            "minimize_on_close": True,
            "loader_color": "#0078d4", # Color por defecto (Azul)
            "total_moves": 0
        }
        self.settings = self.load()

    def load(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    data = json.load(f)
                    # Aseguramos que todas las llaves por defecto existan
                    return {**self.defaults, **data}
            except Exception as e:
                print(f"Error cargando config: {e}")
                return self.defaults.copy()
        return self.defaults.copy()

    def save(self):
        try:
            with open(self.filename, 'w') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Error guardando config: {e}")

    def get(self, key):
        return self.settings.get(key, self.defaults.get(key))

    def set(self, key, value):
        self.settings[key] = value
        self.save()

    def toggle_auto_start(self, enabled):
        """Configura el inicio automático en el registro de Windows."""
        if sys.platform != "win32":
            return
            
        import winreg
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        app_name = "MoveMousePro"
        app_path = os.path.abspath(sys.argv[0])
        
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
            if enabled:
                winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, f'"{app_path}"')
            else:
                try:
                    winreg.DeleteValue(key, app_name)
                except FileNotFoundError:
                    pass
            winreg.CloseKey(key)
        except Exception as e:
            print(f"Error configurando auto-start: {e}")
