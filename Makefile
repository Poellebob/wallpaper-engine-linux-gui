# ...existing code...

flatpak-build:
	flatpak-builder --force-clean --user --install-deps-from=flathub --repo=repo --install builddir flatpak.yml

clean:
	rm -rf .flatpak-builder
	rm -rf builddir

remove:
	flatpak remove com.poellebob.wallpaperengine-linux

.PHONY: flatpak-build


