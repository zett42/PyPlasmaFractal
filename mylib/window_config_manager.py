import configparser
from appdirs import user_config_dir
from pathlib import Path

class WindowConfigManager:
    
    def __init__(self, app_name: str, app_author: str) -> None:
        config_dir = Path(user_config_dir(app_name, app_author))
        config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = config_dir / 'window_config.ini'
        self.config = configparser.ConfigParser()
        self.load_config()

    def load_config(self) -> None:
        if self.config_file.exists():
            self.config.read(self.config_file)
        if 'Window' not in self.config:
            self.config['Window'] = {
                'width': '800',  # default width
                'height': '600',  # default height
                'pos_x': '100',  # default x position
                'pos_y': '100'   # default y position
            }

    def save_config(self, width: int, height: int, pos_x: int, pos_y: int) -> None:
        self.config['Window'] = {
            'width': str(width),
            'height': str(height),
            'pos_x': str(pos_x),
            'pos_y': str(pos_y)
        }
        with open(self.config_file, 'w') as configfile:
            self.config.write(configfile)

    def get_config(self) -> tuple[int, int, int, int]:
        width = self.config.getint('Window', 'width')
        height = self.config.getint('Window', 'height')
        pos_x = self.config.getint('Window', 'pos_x')
        pos_y = self.config.getint('Window', 'pos_y')
        return width, height, pos_x, pos_y
