import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GdkPixbuf, Gdk, Gio
import configparser
import glob
import os
import json
import subprocess
import signal
import sys

# Use XDG config directory for configs
XDG_CONFIG_HOME = os.path.expanduser("~/.config")
CONFIG_DIR = os.path.join(XDG_CONFIG_HOME, "wallpaperengine-linux")
os.makedirs(CONFIG_DIR, exist_ok=True)

CONFIG_PATH = os.path.join(CONFIG_DIR, "config.ini")
USER_CONFIG_PATH = os.path.join(CONFIG_DIR, "configuration.json")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
UI_PATH = os.path.join(SCRIPT_DIR, "main.ui")

def get_walls_path():
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    try:
        return config['config']['path']
    except Exception:
        print("No workshop path set in config.ini")
        return None

class CliFrontend(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="com.example.wallpaperengine")
        self.connect("activate", self.on_activate)

    def on_activate(self, app):
        # Load UI from Cambalache .ui file
        builder = Gtk.Builder()
        builder.add_from_file(UI_PATH)
        self.builder = builder
        self.window = builder.get_object("main")
        self.window.set_application(app)
        self.window.connect("close-request", self.on_close_request)

        # Set sidebar width (paned position)
        paned = self.window.get_child()
        if hasattr(paned, "set_position"):
            paned.set_position(220)  # Sidebar width (preview image + padding)

        config_data = {}
        if os.path.isfile(USER_CONFIG_PATH):
            try:
                with open(USER_CONFIG_PATH, "r", encoding="utf-8") as f:
                    config_data = json.load(f)
            except Exception:
                config_data = {}

        self.image_grid = self.builder.get_object("image_grid")
        self.populate_images()

        self.display_selector = self.builder.get_object("display_selector")
        self.selected_image_preview = Gtk.Image()
        sidebar_box = self.display_selector.get_parent()
        sidebar_box.append(self.selected_image_preview)
        self.selected_image_preview.show()

        self.apply_button = Gtk.Button(label="Apply Wallpaper")
        sidebar_box.append(self.apply_button)
        self.apply_button.connect("clicked", self.apply_walls)
        self.apply_button.show()

        # Add "Clear" button under the kill button
        self.clear_button = Gtk.Button(label="Clear")
        sidebar_box.append(self.clear_button)
        self.clear_button.connect("clicked", self.on_clear_wallpaper_clicked)
        self.clear_button.show()

        # Add "Kill Wallpapers" button under the apply button
        self.kill_button = Gtk.Button(label="Kill")
        sidebar_box.append(self.kill_button)
        self.kill_button.connect("clicked", self.kill_walls)
        self.kill_button.show()

        # Add a separator with padding top and bottom
        separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        separator.set_margin_top(6)
        separator.set_margin_bottom(6)
        sidebar_box.append(separator)
        separator.show()

        # Add toggle button for mature content
        self.mature_toggle = Gtk.ToggleButton(label="Mature Content")
        self.mature_toggle.set_active(False)
        self.mature_toggle.connect("toggled", self.toggle_mature_content)
        sidebar_box.append(self.mature_toggle)
        self.mature_toggle.show()

        if "MATURE_CONTENT" in config_data:
            self.mature_toggle.set_active(config_data["MATURE_CONTENT"])
            if config_data["MATURE_CONTENT"]:
                self.mature_toggle.set_css_classes(["suggested-action"])
            else:
                self.mature_toggle.set_css_classes(["destructive-action"])
        else:
            self.mature_toggle.set_css_classes(["destructive-action"])

        self.populate_displays()
        self.display_selector.connect("changed", self.on_display_changed)

        self.window.present()
        self.update_selected_image_preview()

    def on_close_request(self, *args):
        self.quit()

    def toggle_mature_content(self, button):
        config_data = {}
        if os.path.isfile(USER_CONFIG_PATH):
            try:
                with open(USER_CONFIG_PATH, "r", encoding="utf-8") as f:
                    config_data = json.load(f)
            except Exception:
                config_data = {}
        
        if "MATURE_CONTENT" in config_data:
            config_data["MATURE_CONTENT"] = not config_data["MATURE_CONTENT"]
        else:
            config_data["MATURE_CONTENT"] = True
        
        with open(USER_CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=2)

        # Update toggle button color
        if config_data.get("MATURE_CONTENT", False):
            self.mature_toggle.set_css_classes(["suggested-action"])
        else:
            self.mature_toggle.set_css_classes(["destructive-action"])

        
        # Refresh images based on new mature content setting
        child = self.image_grid.get_first_child()
        while child:
            next_child = child.get_next_sibling()
            self.image_grid.remove(child)
            child = next_child
        self.populate_images()    

    def populate_images(self):
        # Get UI scale (fallback to 1 if not set)
        scale = self.window.get_scale_factor() if hasattr(self.window, "get_scale_factor") else 1
        target_width = 60 * scale

        # Get workshop path from config
        workshop_base = get_walls_path()
        if not workshop_base:
            return
        workshop_dir = os.path.expanduser(workshop_base)

        # Use glob to recursively find all project.json files in all subdirectories
        project_json_files = []
        for root, dirs, files in os.walk(workshop_dir):
            if "project.json" in files:
                project_json_files.append(os.path.join(root, "project.json"))

        for project_json_path in project_json_files:
            subdir = os.path.dirname(project_json_path)
            try:
                with open(project_json_path, "r", encoding="utf-8") as f:
                    project_data = json.load(f)
                preview_name = project_data.get("preview")
                if not preview_name:
                    continue

                # Try all possible locations for the preview image
                img_path = os.path.join(subdir, preview_name)
                found = os.path.isfile(img_path)
                if not found:
                    if os.path.isabs(preview_name) and os.path.isfile(preview_name):
                        img_path = preview_name
                        found = True
                if not found:
                    for root2, dirs2, files2 in os.walk(subdir):
                        for file2 in files2:
                            if file2 == preview_name:
                                img_path = os.path.join(root2, file2)
                                found = True
                                break
                        if found:
                            break
                if not found:
                    continue

                if (project_data.get("contentrating", False) == "Mature" or 
                    project_data.get("contentrating", False) == "Questionable"):
                    config_data = {}
                    if os.path.isfile(USER_CONFIG_PATH):
                        try:
                            with open(USER_CONFIG_PATH, "r", encoding="utf-8") as f:
                                config_data = json.load(f)
                        except Exception:
                            config_data = {}
                    if not config_data.get("MATURE_CONTENT", False):
                        continue

                # Only render the first frame if it's a GIF
                if img_path.lower().endswith(".gif"):
                    loader = GdkPixbuf.PixbufAnimation.new_from_file(img_path)
                    pixbuf = loader.get_static_image()
                    width = pixbuf.get_width()
                    height = pixbuf.get_height()
                    scale_factor = target_width / width
                    new_height = max(1, int(height * scale_factor))
                    scaled_pixbuf = pixbuf.scale_simple(target_width, new_height, GdkPixbuf.InterpType.BILINEAR)
                    image = Gtk.Image.new_from_pixbuf(scaled_pixbuf)
                    image.set_size_request(target_width, new_height)
                else:
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
                button.set_hexpand(False)
                button.set_halign(Gtk.Align.FILL)
                button.set_valign(Gtk.Align.CENTER)
                button.set_size_request(-1, -1)
                button.connect("clicked", self.on_image_button_clicked, img_path)
                self.image_grid.append(button)
            except Exception:
                continue
        # ...existing code...
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
            # Only render the first frame if it's a GIF
            if img_path.lower().endswith(".gif"):
                loader = GdkPixbuf.PixbufAnimation.new_from_file(img_path)
                pixbuf = loader.get_static_image()
                target_width = 200
                width = pixbuf.get_width()
                height = pixbuf.get_height()
                scale_factor = target_width / width
                new_height = max(1, int(height * scale_factor))
                scaled_pixbuf = pixbuf.scale_simple(target_width, new_height, GdkPixbuf.InterpType.BILINEAR)
                self.selected_image_preview.set_from_pixbuf(scaled_pixbuf)
                self.selected_image_preview.set_size_request(target_width, new_height)
            else:
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

    def apply_walls(self, button):
        # Kill all running linux-wallpaperengine processes before starting new one
        try:
            import psutil
            for proc in psutil.process_iter(['name', 'exe', 'cmdline']):
                try:
                    if (
                        proc.info['name'] == 'linux-wallpaperengine'
                        or (proc.info['exe'] and 'linux-wallpaperengine' in proc.info['exe'])
                        or (proc.info['cmdline'] and any('linux-wallpaperengine' in arg for arg in proc.info['cmdline']))
                    ):
                        proc.kill()
                except Exception:
                    continue
        except ImportError:
            # Fallback if psutil is not installed
            os.system("pkill -9 linux-wallpaperengine")

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

            bg_id = config_data.get(str(i), "")
            if bg_id:
                print(f"Screen {i} ID: {screen_id}")
                args += ["--screen-root", screen_id, "--bg", bg_id]
            # If no bg_id, skip this screen

        # Add fps limit if set
        if fps:
            args += ["--fps", str(fps)] 

        # If only engine_path is present, do nothing
        if len(args) == 1:
            print("No backgrounds selected.")
            return

        print("Running:", " ".join(args))
        try:
            subprocess.Popen(args)
        except Exception as e:
            print("Failed to launch wallpaper engine:", e)

    def kill_walls(self, button):
        try:
            import psutil
            for proc in psutil.process_iter(['name', 'exe', 'cmdline']):
                try:
                    if (
                        proc.info['name'] == 'linux-wallpaperengine'
                        or (proc.info['exe'] and 'linux-wallpaperengine' in proc.info['exe'])
                        or (proc.info['cmdline'] and any('linux-wallpaperengine' in arg for arg in proc.info['cmdline']))
                    ):
                        proc.kill()
                except Exception:
                    continue
        except ImportError:
            os.system("pkill -9 linux-wallpaperengine")

    def on_clear_wallpaper_clicked(self, button):
        # Remove the wallpaper assignment for the selected screen
        screen_id = self.display_selector.get_active()
        if screen_id < 0:
            return
        config_data = {}
        if os.path.isfile(USER_CONFIG_PATH):
            try:
                with open(USER_CONFIG_PATH, "r", encoding="utf-8") as f:
                    config_data = json.load(f)
            except Exception:
                config_data = {}
        if str(screen_id) in config_data:
            del config_data[str(screen_id)]
            with open(USER_CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=2)
        self.update_selected_image_preview()

def main():
    # Check for --apply flag

    # Check if the .desktop file exists
    desktop_file = os.path.expanduser("~/.local/share/applications/wallpaperengine-linux.desktop")
    desktop_dir = os.path.dirname(desktop_file)
    if not os.path.isdir(desktop_dir):
        try:
            os.makedirs(desktop_dir, exist_ok=True)
        except Exception as e:
            print(f"Failed to create directory {desktop_dir}: {e}")
            sys.exit(1)
    if not os.path.isfile(desktop_file) or "--new-desktop" in sys.argv:
        try:
            with open(desktop_file, "w", encoding="utf-8") as f:
                f.write("[Desktop Entry]\n")
                f.write("Type=Application\n")
                f.write("Name=Wallpaper Engine Linux\n")
                f.write(f"Exec=python3 '{os.path.abspath(__file__)}'\n")
                f.write(f"Icon={os.path.dirname(__file__)}/icon.png\n")
                f.write("Categories=Utility;\n")
                print(f"Created .desktop file at {desktop_file}")
            os.chmod(desktop_file, 0o755)
            sys.exit(0)
        except Exception as e:
            print(f"Failed to write .desktop file: {e}")
            sys.exit(1)
    
    if "--help" in sys.argv or "-h" in sys.argv:
        print("Usage: python main.py [--apply] [--kill]")
        print("Options:")
        print("  --apply   Apply the selected wallpapers and exit")
        print("  --kill    Kill all running wallpaper engine processes and exit")
        print("  --new-desktop Create or update the .desktop file for the application")
        print("  --help, -h Show this help message")
        sys.exit(0)

    if "--apply" in sys.argv:
        class DummyButton: pass
        app = CliFrontend()
        app.apply_walls(DummyButton())
        print("Applied wallpapers and exited.")
        sys.exit(0)

    # Check for --kill flag
    if "--kill" in sys.argv:
        class DummyButton: pass
        app = CliFrontend()
        app.kill_walls(DummyButton())
        print("Killed wallpapers and exited.")
        sys.exit(0)

    app = CliFrontend()
    app.run()

if __name__ == "__main__":
    main()
