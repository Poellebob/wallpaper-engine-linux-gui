#!/bin/bash

echo "This will set up Wallpaper Engine Linux and its dependencies."

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS_ID=$ID
else
    OS_ID=$(uname -s)
fi

install_arch() {
    echo "Detected Arch Linux."
    echo "Installing linux-wallpaperengine-git and dependencies with yay..."
    yay -Sy --needed linux-wallpaperengine-git python python-gobject gtk4 gobject-introspection gtk4 gdk-pixbuf2
}

install_debian() {
    echo "Detected Debian/Ubuntu."
    echo "Installing dependencies with apt..."
    sudo apt update
    sudo apt install -y python3 python3-gi python3-gi-cairo gir1.2-gtk-4.0 gir1.2-gdkpixbuf-2.0 gobject-introspection
    echo "You must install linux-wallpaperengine manually (see https://github.com/Almamu/linux-wallpaperengine), build or install it and then set engine_path=<path to bin> in config.ini."
}

install_fedora() {
    echo "Detected Fedora."
    echo "Installing dependencies with dnf..."
    sudo dnf install -y python3-gobject gtk4 gtk4-gdk-pixbuf2 gobject-introspection
    echo "You must install linux-wallpaperengine manually (see https://github.com/Almamu/linux-wallpaperengine), build or install it and then set engine_path=<path to bin> in config.ini."
}

install_suse() {
    echo "Detected openSUSE."
    echo "Installing dependencies with zypper..."
    sudo zypper install -y python3-gobject python3-gobject-Gdk typelib-1_0-Gtk-4_0 gtk4
    echo "You must install linux-wallpaperengine manually (see https://github.com/Almamu/linux-wallpaperengine), build or install it and then set engine_path=<path to bin> in config.ini."
}

case "$OS_ID" in
    arch|manjaro|endeavouros)
        install_arch
        ;;
    debian|ubuntu|linuxmint|pop)
        install_debian
        ;;
    fedora)
        install_fedora
        ;;
    opensuse*|suse)
        install_suse
        ;;
    *)
        echo "Unknown or unsupported OS: $OS_ID"
        echo "Please install the following dependencies manually:"
        echo "  - python3"
        echo "  - python3-gi"
        echo "  - python3-gobject"
        echo "  - GTK+ 4 (libgtk-4-1 or gtk4)"
        echo "  - GdkPixbuf (gir1.2-gdkpixbuf-2.0 or gdk-pixbuf2)"
        echo "  - wallpaperengine-linux (https://github.com/Almamu/linux-wallpaperengine)"
        ;;
esac

mkdir -p ~/.config/wallpaperengine-linux
# Create config.ini if it doesn't exist
if [ ! -f ~/.config/wallpaperengine-linux/config.ini ]; then
    echo "[Settings]" > ~/.config/wallpaperengine-linux/config.ini
    echo "path = ~/.steam/steam/steamapps/workshop/content/431960/" >> ~/.config/wallpaperengine-linux/config.ini
    echo "engine_path = /usr/bin/linux-wallpaperengine" >> ~/.config/wallpaperengine-linux/config.ini
    echo "fps=25" >> ~/.config/wallpaperengine-linux/config.ini
fi

git clone --branch remote-install git@github.com:Poellebob/wallpaper-engine-linux-gui.git
cd wallpaper-engine-linux-gui

mkdir -p ~/.local/share/wallpaperengine-linux
cp main.py ~/.local/share/wallpaperengine-linux/
cp icon.png ~/.local/share/wallpaperengine-linux/
cp ui.glade ~/.local/share/wallpaperengine-linux/

echo "This will now make a .desktop file for the wallpaper engine linux."

if [ -f ~/.local/share/wallpaperengine-linux/main.py ]; then
    python3 ~/.local/share/wallpaperengine-linux/main.py --new-desktop
fi

echo "You can now run the wallpaper engine linux from the applications menu."

cd ..
# Clean up the cloned repository
rm -rf wallpaper-engine-linux-gui
echo "Installation complete. You can now run Wallpaper Engine Linux from your applications menu."
exit 0