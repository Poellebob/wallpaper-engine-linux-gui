# Wallpaper Engine GTK Frontend

A GTK-based frontend for managing and applying wallpapers using [linux-wallpaperengine](https://github.com/Almamu/linux-wallpaperengine) on Linux.

## Features

- Browse and preview wallpapers from your Steam Workshop directory.
- Assign different wallpapers to different screens.
- Set framerate and engine path via configuration.
- GTK4-based UI with image grid and per-screen preview.
- One-click apply wallpapers to all screens.
- CLI flags for automation (`--apply`, `--kill`, `--setup`).

## Installation

### Arch Linux (yay required)

```sh
yay -Sy --needed wallpaperengine-linux-git python python-gobject gtk4 gobject-introspection gtk4 gdk-pixbuf2
./install.sh
```

### Debian/Ubuntu

```sh
sudo apt update
sudo apt install -y python3 python3-gi python3-gi-cairo gir1.2-gtk-4.0 gir1.2-gdkpixbuf-2.0 gobject-introspection
# Download and build wallpaperengine-linux manually: https://github.com/Almamu/linux-wallpaperengine
./install.sh
```

### Fedora

```sh
sudo dnf install -y python3-gobject gtk4 gtk4-gdk-pixbuf2 gobject-introspection
# Download and build wallpaperengine-linux manually: https://github.com/Almamu/linux-wallpaperengine
./install.sh
```

### openSUSE

```sh
sudo zypper install -y python3-gobject python3-gobject-Gdk typelib-1_0-Gtk-4_0 gtk4
# Download and build wallpaperengine-linux manually: https://github.com/Almamu/linux-wallpaperengine
./install.sh
```

### Other Distributions

Install the following dependencies manually:
- python3
- python3-gi
- python3-gobject
- GTK+ 4 (libgtk-4-1 or gtk4)
- GdkPixbuf (gir1.2-gdkpixbuf-2.0 or gdk-pixbuf2)
- wallpaperengine-linux (https://github.com/Almamu/linux-wallpaperengine)

Then run:
```sh
./install.sh
```

## Configuration

Edit `config.ini`:

```ini
[config]
first_run=true
path=~/.steam/steam/steamapps/workshop/content/431960/
engine_path=/usr/bin/linux-wallpaperengine
fps=25
```

- `path`: Path to your Steam Workshop wallpapers.
- `engine_path`: Path to the linux-wallpaperengine executable.
- `fps`: Framerate limit for wallpapers.

## Usage

1. Run the application:
    ```sh
    python3 main.py
    ```
2. Select a screen from the dropdown.
3. Click a wallpaper to assign it to the selected screen.
4. Click "Apply Wallpaper" to set wallpapers using linux-wallpaperengine.
5. Use "Kill" to stop all running wallpaperengine-linux processes.
6. Use "Clear" to remove the wallpaper assignment for the selected screen.

### CLI Flags

- `--apply` : Apply the selected wallpapers and exit (no GUI).
- `--kill` : Kill all running wallpaperengine-linux processes and exit.
- `--setup` : Create or update the .desktop file for the application and exit.
- `--new-desktop` : Same as `--setup`.
- `--help` or `-h` : Show help message.

Example:
```sh
python3 main.py --apply
python3 main.py --kill
python3 main.py --setup
```

## Desktop Integration

The install script (`install.sh`) will create a `.desktop` file in `~/.local/share/applications/wallpaperengine-linux.desktop` so you can launch the app from your applications menu.

If you move the folder, re-run `install.sh` to update the .desktop file.

## License

MIT