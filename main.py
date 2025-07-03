import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GdkPixbuf, Gdk
import configparser
import glob
import os
import json
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.ini")
GLADE_PATH = os.path.join(SCRIPT_DIR, "ui.glade")
USER_CONFIG_PATH = os.path.join(SCRIPT_DIR, "configuration.json")

def get_walls_path():
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    try:
        return config['config']['path']
    except Exception:
        return None

class CliFrontend(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="com.example.wallpaperengine")
        self.connect("activate", self.on_activate)

    def on_activate(self, app):
        self.builder = Gtk.Builder()
        self.builder.add_from_file(GLADE_PATH)
        self.window = self.builder.get_object("main")
        self.window.set_application(app)
        self.window.connect("close-request", self.on_close_request)

        # Set sidebar width (paned position)
        paned = self.window.get_child()
        if hasattr(paned, "set_position"):
            paned.set_position(220)  # Sidebar width (preview image + padding)

        self.image_grid = self.builder.get_object("image_grid")
        self.populate_images()

        self.display_selector = self.builder.get_object("display_selector")
        self.selected_image_preview = Gtk.Image()
        sidebar_box = self.display_selector.get_parent()
        sidebar_box.append(self.selected_image_preview)
        self.selected_image_preview.show()

        self.apply_button = Gtk.Button(label="Apply Wallpapers")
        sidebar_box.append(self.apply_button)
        self.apply_button.connect("clicked", self.on_apply_wallpapers_clicked)
        self.apply_button.show()

        self.populate_displays()
        self.display_selector.connect("changed", self.on_display_changed)

        self.window.present()
        self.update_selected_image_preview()

    def on_close_request(self, *args):
        self.quit()

    def populate_images(self):
        # Get UI scale (fallback to 1 if not set)
        scale = self.window.get_scale_factor() if hasattr(self.window, "get_scale_factor") else 1
        target_width = 60 * scale

        # Get workshop path from config
        workshop_base = get_walls_path()
        if not workshop_base:
            return
        workshop_dir = os.path.expanduser(workshop_base)
        subdirs = [os.path.join(workshop_dir, d) for d in os.listdir(workshop_dir) if os.path.isdir(os.path.join(workshop_dir, d))]

        for subdir in subdirs:
            project_json_path = os.path.join(subdir, "project.json")
            if not os.path.isfile(project_json_path):
                continue
            try:
                with open(project_json_path, "r", encoding="utf-8") as f:
                    project_data = json.load(f)
                preview_name = project_data.get("preview")
                if not preview_name:
                    continue
                img_path = os.path.join(subdir, preview_name)
                if not os.path.isfile(img_path):
                    continue
                # Load and scale image (preserve aspect ratio)
                pixbuf = GdkPixbuf.Pixbuf.new_from_file(img_path)
                width = pixbuf.get_width()
                height = pixbuf.get_height()
                scale_factor = target_width / width
                new_height = max(1, int(height * scale_factor))
                scaled_pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(img_path, width=target_width, height=new_height, preserve_aspect_ratio=True)
                image = Gtk.Image.new_from_pixbuf(scaled_pixbuf)
                image.set_size_request(target_width, new_height)

                button = Gtk.Button()
                button.set_child(image)
                button.connect("clicked", self.on_image_button_clicked, img_path)
                self.image_grid.append(button)
            except Exception:
                continue

    def get_image_parent_folder(self, img_path):
        return os.path.basename(os.path.dirname(img_path))

    def populate_displays(self):
        display = Gdk.Display.get_default()
        if display:
            # GTK4: Use get_monitors() which returns a GListModel
            monitors = display.get_monitors()
            n_monitors = monitors.get_n_items()
            for i in range(n_monitors):
                monitor = monitors.get_item(i)
                # You can use monitor.get_model() or geometry for more info if needed
                self.display_selector.append_text(f"Screen {i}")
            self.display_selector.set_active(0)

    def on_image_button_clicked(self, button, img_path):
        parent_folder = self.get_image_parent_folder(img_path)
        print(parent_folder)
        # Get selected screen id
        screen_id = self.display_selector.get_active()
        if screen_id < 0:
            return
        # Load or create configuration.json
        config_data = {}
        if os.path.isfile(USER_CONFIG_PATH):
            try:
                with open(USER_CONFIG_PATH, "r", encoding="utf-8") as f:
                    config_data = json.load(f)
            except Exception:
                config_data = {}
        # Store mapping
        config_data[str(screen_id)] = parent_folder
        with open(USER_CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=2)
        self.update_selected_image_preview()

    def on_display_changed(self, combo):
        self.update_selected_image_preview()

    def update_selected_image_preview(self):
        screen_id = self.display_selector.get_active()
        if screen_id < 0:
            self.selected_image_preview.clear()
            return
        # Load configuration.json
        config_data = {}
        if os.path.isfile(USER_CONFIG_PATH):
            try:
                with open(USER_CONFIG_PATH, "r", encoding="utf-8") as f:
                    config_data = json.load(f)
            except Exception:
                config_data = {}
        parent_folder = config_data.get(str(screen_id))
        if not parent_folder:
            self.selected_image_preview.clear()
            return
        # Find the preview image for this parent folder
        workshop_base = get_walls_path()
        if not workshop_base:
            self.selected_image_preview.clear()
            return
        subdir = os.path.join(os.path.expanduser(workshop_base), parent_folder)
        project_json_path = os.path.join(subdir, "project.json")
        if not os.path.isfile(project_json_path):
            self.selected_image_preview.clear()
            return
        try:
            with open(project_json_path, "r", encoding="utf-8") as f:
                project_data = json.load(f)
            preview_name = project_data.get("preview")
            if not preview_name:
                self.selected_image_preview.clear()
                return
            img_path = os.path.join(subdir, preview_name)
            if not os.path.isfile(img_path):
                self.selected_image_preview.clear()
                return
            # Load and scale image for preview (use width 200)
            target_width = 200
            pixbuf = GdkPixbuf.Pixbuf.new_from_file(img_path)
            width = pixbuf.get_width()
            height = pixbuf.get_height()
            scale_factor = target_width / width
            new_height = max(1, int(height * scale_factor))
            scaled_pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(img_path, width=target_width, height=new_height, preserve_aspect_ratio=True)
            self.selected_image_preview.set_from_pixbuf(scaled_pixbuf)
            self.selected_image_preview.set_size_request(target_width, new_height)
        except Exception:
            self.selected_image_preview.clear()

    def on_apply_wallpapers_clicked(self, button):
        # Get engine path and fps from config
        config = configparser.ConfigParser()
        config.read(CONFIG_PATH)
        try:
            engine_path = config['config']['engine_path']
        except Exception:
            print("Engine path not set in config.ini")
            return
        fps = config['config'].get('fps', None)

        # Load configuration.json
        config_data = {}
        if os.path.isfile(USER_CONFIG_PATH):
            try:
                with open(USER_CONFIG_PATH, "r", encoding="utf-8") as f:
                    config_data = json.load(f)
            except Exception:
                print("Could not read configuration.json")
                return

        # Get screen names from Gdk
        display = Gdk.Display.get_default()
        if not display:
            print("No display found")
            return

        monitors = display.get_monitors()
        n_monitors = monitors.get_n_items()
        args = [engine_path]
        for i in range(n_monitors):
            monitor = monitors.get_item(i)
            # Use get_connector() for X11/Wayland style IDs (e.g., HDMI-1, DP-1)
            screen_id = None
            if hasattr(monitor, "get_connector"):
                screen_id = monitor.get_connector()
            if not screen_id and hasattr(monitor, "get_physical_monitor"):
                phys = monitor.get_physical_monitor()
                if phys and hasattr(phys, "get_name"):
                    screen_id = phys.get_name()
            if not screen_id and hasattr(monitor, "get_name"):
                screen_id = monitor.get_name()
            if not screen_id:
                screen_id = f"Screen{i}"

            print(f"Screen {i} ID: {screen_id}")
            args += ["--screen-root", screen_id]
            bg_id = config_data.get(str(i), "")
            if bg_id:
                args += ["--bg", bg_id]

        # Add fps limit if set
        if fps:
            args += ["--fps", str(fps)]

        # If no backgrounds, do nothing
        if len(args) == 1:
            print("No backgrounds selected.")
            return

        print("Running:", " ".join(args))
        try:
            subprocess.Popen(args)
        except Exception as e:
            print("Failed to launch wallpaper engine:", e)

def main():
    app = CliFrontend()
    app.run()

if __name__ == "__main__":
    main()
