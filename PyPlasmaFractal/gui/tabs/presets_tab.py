import logging
from pathlib import Path
import imgui
from PyPlasmaFractal.mylib.config.config_path_manager import ConfigPathManager
import PyPlasmaFractal.mylib.gui.imgui_helper as ih

from PyPlasmaFractal.gui.utils.common_controls import confirm_dialog, open_folder_button
from PyPlasmaFractal.mylib.config.json_file_storage import JsonFileStorage
from PyPlasmaFractal.mylib.config.source_manager import StorageSourceManager
from PyPlasmaFractal.gui.utils.common_types import GuiNotification
from PyPlasmaFractal.mylib.gui.notification_manager import NotificationManager
from PyPlasmaFractal.plasma_fractal_params import PlasmaFractalParams

class PresetTab:
    """
    Manages the UI controls for preset management in the plasma fractal visualization.
    """

    def __init__(self, path_manager: ConfigPathManager, notifications: NotificationManager[GuiNotification]):
        
        self.app_storage  = JsonFileStorage(Path(path_manager.app_specific_path)  / 'presets', list_extension=False)
        self.user_storage = JsonFileStorage(Path(path_manager.user_specific_path) / 'presets', list_extension=False)
        self.storage_manager = StorageSourceManager(self.app_storage, self.user_storage)        
        
        self.notifications = notifications
        
        self.preset_list = []
        self.selected_preset_index = -1
        self.current_preset_name = "new_file"
        self.preset_error_message = None
        self.preset_last_saved_file_path = None      


    def draw(self, params: PlasmaFractalParams):
        
        # Fetch the initial list of presets if it hasn't been done yet
        if not self.preset_list:
            self.update_presets_list()

        self.preset_selection_ui(params)

        if (current_preset := self.get_current_preset()):
            # Controls that depend on a selected preset
            imgui.spacing()
            self.preset_load_ui(params)
            imgui.same_line()
            self.preset_delete_ui()
            imgui.same_line()
            open_folder_button(current_preset.storage.directory)
        
        imgui.spacing()
        self.preset_save_ui(params)

        self.handle_preset_error()


    def preset_selection_ui(self, params: PlasmaFractalParams):
        """
        Displays the available presets in a list box.
        """
        width = imgui.get_content_region_available_width()

        imgui.spacing()
        imgui.text("Available Presets (* marks built-ins):")
        imgui.spacing()

        if imgui.begin_list_box("##AvailablePresets", width, 450):
            
            for i, preset in enumerate(self.preset_list):

                display_name = f"* {preset.name}" if preset.storage == self.storage_manager.app_storage else preset.name
                opened, _ = imgui.selectable(display_name, self.selected_preset_index == i, flags=imgui.SELECTABLE_ALLOW_DOUBLE_CLICK)

                if opened:
                    self.selected_preset_index = i
                    self.current_preset_name = preset.name

                    if imgui.is_mouse_double_clicked(0):
                        self.apply_current_preset(params)

            imgui.end_list_box()


    def preset_load_ui(self, params: PlasmaFractalParams):

        if imgui.button("Load"):
            self.apply_current_preset(params)


    def preset_save_ui(self, params: PlasmaFractalParams):
        
        confirm_dlg_title = "Confirm Overwrite Preset"

        if ih.input_text("##PresetName", self, 'current_preset_name'):
            self.current_preset_name = Path(self.current_preset_name).stem  

        imgui.same_line()

        if imgui.button("Save"):
            if self.storage_manager.user_storage.exists(self.current_preset_name):
                imgui.open_popup(confirm_dlg_title)
            else:
                self.save_preset(params)

        if confirm_dialog(f'A preset with this name already exists:\n"{self.current_preset_name}"\n\nDo you want to overwrite it?',
                          confirm_dlg_title):
            self.save_preset(params)
            
        if self.preset_last_saved_file_path:
            imgui.spacing()
            imgui.text_colored(f"Preset saved to:", 0.2, 1.0, 1.0)
            ih.display_trimmed_path_with_tooltip(self.preset_last_saved_file_path)


    def preset_delete_ui(self):
        
        if self.get_current_preset().storage == self.storage_manager.user_storage:
            if imgui.button("Delete"):
                imgui.open_popup("Confirm Deletion")

            if confirm_dialog(f'Are you sure you want to delete the preset "{self.current_preset_name}" ?', "Confirm Deletion"):
                self.delete_selected_preset()


    def handle_preset_error(self):
        
        if self.preset_error_message:
            imgui.spacing()
            imgui.separator()
            imgui.push_text_wrap_pos()
            imgui.text_colored(f"ERROR: {self.preset_error_message}", 1.0, 0.2, 0.2)
            imgui.pop_text_wrap_pos()


    def get_current_preset(self) -> StorageSourceManager.Item:
        
        return self.preset_list[self.selected_preset_index] if self.selected_preset_index >= 0 else None


    def update_presets_list(self):
        
        self.preset_list = self.storage_manager.list()
        self.selected_preset_index = -1


    def apply_current_preset(self, params: PlasmaFractalParams):
        
        self.preset_error_message = None
        self.preset_last_saved_file_path = None

        try:
            preset = self.get_current_preset()
            preset_data = preset.storage.load(preset.name)
            params.apply_defaults()
            params.merge_dict(preset_data)
            
            self.notifications.push_notification(GuiNotification.NEW_PRESET_LOADED)
            
            logging.info(f'Preset "{preset.name}" applied successfully.')
            
        except Exception as e:
            self.preset_error_message = f"Failed to apply preset: {str(e)}"
            logging.error(self.preset_error_message)


    def save_preset(self, params: PlasmaFractalParams):
        
        self.preset_error_message = None
        self.preset_last_saved_file_path = None

        try:
            storage = self.user_storage
            logging.info(f'Saving preset: "{self.current_preset_name}" to "{storage.directory}"')
            
            data = params.to_dict()
            storage.save(data, self.current_preset_name)
            
            self.preset_last_saved_file_path = storage.get_full_path(self.current_preset_name)
            self.update_presets_list()
            
        except Exception as e:
            self.preset_error_message = f"Failed to save preset: {str(e)}"
            logging.error(self.preset_error_message)


    def delete_selected_preset(self):
        
        assert self.selected_preset_index != -1, "No preset is selected."

        self.preset_error_message = None
        self.preset_last_saved_file_path = None

        try:
            self.user_storage.delete(self.get_current_preset().name)
        except Exception as e:
            self.preset_error_message = f"Failed to delete preset: {str(e)}"
            logging.error(self.preset_error_message)

        self.update_presets_list()
