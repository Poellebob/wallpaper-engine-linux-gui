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

echo "This will make a .desktop file for the wallpaper engine linux."
echo "If you move the wallpaper engine linux folder, you will have to run this script again to update the .desktop file."
echo "You can now run the wallpaper engine linux from the applications menu."
python3 main.py --new-desktop
