# Wallpaper Engine GTK Frontend

A GTK-based frontend for managing and applying wallpapers using [linux-wallpaperengine](https://github.com/catsout/wallpaper-engine-kde) on Linux.

## Features

- Browse and preview wallpapers from your Steam Workshop directory.
- Assign different wallpapers to different screens.
- Set framerate and engine path via configuration.
- GTK4-based UI with image grid and per-screen preview.
- One-click apply wallpapers to all screens.

## Requirements

- linux-wallpaperengine  
    - OpenGL 3.3 support  
    - CMake  
    - LZ4, Zlib  
    - SDL2  
    - FFmpeg  
    - X11 or Wayland  
    - Xrandr (for X11)  
    - GLFW3, GLEW, GLUT, GLM  
    - MPV  
    - PulseAudio  
    - FFTW3  
- Python 3
- PyGObject (`python3-gi`)
- GTK+ 4 (`libgtk-4-1`)
- GdkPixbuf (`gir1.2-gdkpixbuf-2.0`)
- python3-gobject

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
4. Click "Apply Wallpapers" to set wallpapers using linux-wallpaperengine.