#!/usr/bin/env bash

echo "This will set up Wallpaper Engine Linux and its dependencies."

# Parse arguments
BRANCH="master"
for arg in "$@"; do
  case $arg in
    --devel)
      BRANCH="devel"
      echo "Using development branch."
      ;;
  esac
done

# Detect OS
if [ -f /etc/os-release ]; then
  . /etc/os-release
  OS_ID=$ID
else
  OS_ID=$(uname -s)
fi

engine_path=/usr/bin/linux-wallpaperengine
mkdir -p ~/.local/share/wallpaperengine-linux

build_linux_wallpaperengine() {
  git clone --recurse-submodules -b "$BRANCH" https://github.com/Poellebob/wallpaper-engine-linux-gui.git
  cd wallpaper-engine-linux-gui/linux-wallpaperengine
  mkdir build && cd build
  cmake ..
  make

  if [ $? -ne 0 ]; then
      echo "Build failed. Please check the output above for errors."
      exit 1
  else
      echo "Build completed successfully."
  fi
  
  mkdir -p ~/.local/share/wallpaperengine-linux/linux-wallpaperengine
  cp -r ./output/* ~/.local/share/wallpaperengine-linux/linux-wallpaperengine/
  chmod +x ~/.local/share/wallpaperengine-linux/linux-wallpaperengine/linux-wallpaperengine
  engine_path=~/.local/share/wallpaperengine-linux/linux-wallpaperengine/linux-wallpaperengine
  cd ../..
}

install_arch() {
  git clone -b "$BRANCH" https://github.com/Poellebob/wallpaper-engine-linux-gui.git
  cd wallpaper-engine-linux-gui

  echo "Detected Arch Linux."
  echo "Installing linux-wallpaperengine-git and dependencies with yay..."
  yay -Sy --needed linux-wallpaperengine-git git python python-gobject gtk4 gobject-introspection gtk4 gdk-pixbuf2 base-devil cmake
  engine_path=$(which linux-wallpaperengine)
}

install_debian() {
  echo "Detected Debian/Ubuntu."
  echo "Installing dependencies with apt..."
  sudo apt update
  sudo apt-get install -y \
    git python3 python3-gi python3-gi-cairo gir1.2-gtk-4.0 gir1.2-gdkpixbuf-2.0 gobject-introspection \
    build-essential cmake libxrandr-dev libxinerama-dev libxcursor-dev libxi-dev libgl-dev libglew-dev freeglut3-dev libsdl2-dev liblz4-dev libavcodec-dev libavformat-dev libavutil-dev libswscale-dev libxxf86vm-dev libglm-dev libglfw3-dev libmpv-dev mpv libmpv2 libpulse-dev libpulse0 libfftw3-dev libkissfft-dev
  build_linux_wallpaperengine
}

install_fedora() {
  echo "Detected Fedora."
  echo "Installing dependencies with dnf..."
  sudo dnf install -y \
    git python3-gobject gtk4 gobject-introspection \
    gcc-c++ make cmake \
    libXrandr-devel libXinerama-devel libXcursor-devel libXi-devel \
    mesa-libGL-devel glew-devel freeglut-devel \
    SDL2-devel lz4-devel \
    ffmpeg-free \
    libXxf86vm-devel glm-devel glfw-devel \
    mpv mpv-libs \
    pulseaudio-libs-devel fftw-devel \
    spirv-tools

  build_linux_wallpaperengine
}

install_suse() {
  echo "suse is not fully supported and the packages might be wrong."
  echo "If you know how suse works, consider opening a bug report or submitting a pull request. Thanks :)"
  read -p "Do you want to continue? [y/N]: " choice

  case "$choice" in
    [yY]|[yY][eE][sS])
      echo "Continuing..."
      ;;
    *)
      echo "Aborted."
      exit 1
      ;;
  esac

  echo "Detected openSUSE."
  echo "Installing dependencies with zypper..."

  sudo zypper addrepo https://download.opensuse.org/repositories/games/openSUSE_Tumbleweed/games.repo
  sudo zypper refresh

  sudo zypper install -y \
    git python3-gobject python3-gobject-Gdk typelib-1_0-Gtk-4_0 gtk4 \
    gcc-c++ make cmake \
    libXrandr-devel libXinerama-devel libXcursor-devel libXi-devel \
    Mesa-libGL-devel glew-devel freeglut-devel \
    liblz4-devel libSDL3_image0 \
    libavcodec-devel libavformat-devel libavutil-devel libswscale-devel \
    libXxf86vm-devel glm-devel \
    mpv \
    libpulse-devel fftw3-devel

  build_linux_wallpaperengine
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
touch ~/.config/wallpaperengine-linux/config.json
cat > ~/.config/wallpaperengine-linux/config.json << EOF
{
  "engine_path": "$engine_path",
  "fps": 25,
  "path": "$HOME/.steam/steam/steamapps/workshop/content/431960/",
  "fill": false,
  "MATURE_CONTENT": false
}
EOF

cp main.py ~/.local/share/wallpaperengine-linux/
cp icon.png ~/.local/share/wallpaperengine-linux/
cp main.ui ~/.local/share/wallpaperengine-linux/
cp main.ui.cmb ~/.local/share/wallpaperengine-linux/

echo "This will now make a .desktop file for the wallpaper engine linux."

if [ -f ~/.local/share/wallpaperengine-linux/main.py ]; then
  python3 ~/.local/share/wallpaperengine-linux/main.py --new-desktop
fi

mkdir -p ~/.local/bin
# Check if ~/.local/bin is already in PATH
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo "~/.local/bin is NOT in your PATH."
    read -p "Do you want me to add it to your shell config? [y/N]: " addpath

    if [[ "$addpath" =~ ^[yY]$ ]]; then
        echo "Adding ~/.local/bin to PATH..."

        if [ -f "$HOME/.bashrc" ]; then
            echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
            echo "Added to ~/.bashrc"
        fi

        if [ -f "$HOME/.zshrc" ]; then
            echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.zshrc"
            echo "Added to ~/.zshrc"
        fi

        export PATH="$HOME/.local/bin:$PATH"

    else
        echo "Not modifying your config."
        echo
        echo "If you change your mind, add this line to your shell config:"
        echo 'export PATH="$HOME/.local/bin:$PATH"'
    fi
else
    echo "~/.local/bin is already in your PATH."
fi

touch ~/.local/bin/welg
cat > ~/.local/bin/welg << 'EOF'
#!/usr/bin/env bash

MAIN_SCRIPT="$HOME/.local/share/wallpaperengine-linux/main.py"

# Check if --startup-command is in arguments
if [[ " $* " == *" --startup-command "* ]]; then
    # Echo the special startup command
    echo "$HOME/.local/bin/welg --apply"

    # Remove --startup-command from arguments
    args=()
    for arg in "$@"; do
        if [[ "$arg" != "--startup-command" ]]; then
            args+=("$arg")
        fi
    done

    # Only run the main script if there are other arguments
    if [[ ${#args[@]} -gt 0 ]]; then
        python3 "$MAIN_SCRIPT" "${args[@]}"
    fi
else
    # Run normally if --startup-command is not present
    python3 "$MAIN_SCRIPT" "$@"
fi
EOF

chmod +x ~/.local/bin/welg

echo "You can now run the wallpaper engine linux from the applications menu."

cd ..
# Clean up the cloned repository
rm -rf wallpaper-engine-linux-gui
echo "Installation complete. You can now run Wallpaper Engine Linux from your applications menu."
exit 0
