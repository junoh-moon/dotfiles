#!/usr/bin/env python3
from argparse import ArgumentParser

from script import Script


class KotlinLspInstaller(Script):
    def run(self):
        ok, _, _ = self.shell.exec(
            "Installing the latest Kotlin LSP from Open VSX",
            r"""
            set -euo pipefail

            # Common setup; this block also runs directly in bash.
            case "$(uname -s)" in
                Linux) os_name=linux; product_os=Linux ;;
                Darwin) os_name=darwin; product_os=macOS ;;
                MINGW*|MSYS*|CYGWIN*) os_name=win32; product_os=Windows ;;
                *) echo "Unsupported operating system" >&2; exit 1 ;;
            esac
            case "$(uname -m)" in
                x86_64|amd64) arch=x64 ;;
                arm64|aarch64) arch=arm64 ;;
                *) echo "Unsupported architecture" >&2; exit 1 ;;
            esac
            install_dir="$HOME/.local/kotlin-lsp"
            bin_dir="$HOME/.local/bin"
            mkdir -p -- "$install_dir" "$bin_dir"
            stage=$(mktemp -d "$install_dir/.staging-XXXXXX")
            identity=${stage##*/.staging-}
            current="$bin_dir/kotlin-lsp.sh"
            target="$install_dir/kotlin-server-$identity"
            temporary_link="$bin_dir/.kotlin-lsp.sh-$identity"
            launcher=
            cleanup() {
                status=$?
                trap - EXIT
                rm -f -- "$temporary_link"
                if [ -d "$target" ] && [ "$(readlink "$current" || true)" != "$target/$launcher" ]; then
                    rm -rf -- "$target"
                fi
                rm -rf -- "$stage"
                exit "$status"
            }
            trap cleanup EXIT
            trap 'exit 130' INT
            trap 'exit 143' TERM

            # Resolve the platform-specific extension and its server download URL.
            curl -fLsS --retry 3 --connect-timeout 15 --max-time 600 \
                --proto '=https' --proto-redir '=https' \
                -o "$stage/extension.json" \
                "https://open-vsx.org/api/JetBrains/kotlin-server/$os_name-$arch/latest"
            url=$(jq -er --arg platform "$os_name-$arch" '
                select(.namespace == "JetBrains" and .name == "kotlin-server"
                    and .targetPlatform == $platform) | .files.download
            ' "$stage/extension.json")
            curl -fLsS --retry 3 --connect-timeout 15 --max-time 600 \
                --proto '=https' --proto-redir '=https' \
                -o "$stage/extension.vsix" "$url"
            unzip -p "$stage/extension.vsix" extension/server-bundle.json > "$stage/bundle.json"

            # Download and extract the server; the filename does not determine the format.
            url=$(jq -er '.url' "$stage/bundle.json")
            curl -fLsS --retry 3 --connect-timeout 15 --max-time 600 \
                --proto '=https' --proto-redir '=https' -o "$stage/archive" "$url"
            mkdir -- "$stage/extracted"
            if unzip -Z -1 "$stage/archive" >/dev/null 2>&1; then
                unzip -q "$stage/archive" -d "$stage/extracted"
            else
                tar -xf "$stage/archive" -C "$stage/extracted"
            fi
            find "$stage/extracted" -type f -name product-info.json > "$stage/products"
            [ "$(wc -l < "$stage/products" | tr -d '[:space:]')" = 1 ] || {
                echo "Expected exactly one product-info.json" >&2
                exit 1
            }
            product=$(cat "$stage/products")
            launcher=$(jq -er --arg os "$product_os" --arg arch "$arch" '
                {"x64":"x64", "amd64":"x64", "x86_64":"x64",
                 "arm64":"arm64", "aarch64":"arm64"} as $arches |
                [.launch[] | select(.os == $os and $arches[.arch] == $arch)] |
                if length == 1 then .[0].launcherPath else error("Expected one launcher") end
            ' "$product")
            case "$launcher" in
                /*|../*|*/../*|*/..) echo "Invalid launcher path: $launcher" >&2; exit 1 ;;
            esac
            server=$(dirname "$product")
            [ -f "$server/$launcher" ]
            chmod +x "$server/$launcher"

            # Switch the launcher only after extraction succeeds; keep the previous install.
            previous=$(readlink "$current" || true)
            previous=${previous#"$install_dir"/}
            previous="$install_dir/${previous%%/*}"
            mv -- "$server" "$target"
            ln -s "$target/$launcher" "$temporary_link"
            mv -f -- "$temporary_link" "$current"
            find "$install_dir" -mindepth 1 -maxdepth 1 -type d \
                -name 'kotlin-server-*' ! -path "$target" ! -path "$previous" \
                -exec rm -rf -- {} + || echo "Could not remove old Kotlin LSP installs" >&2
            """,
        )
        if not ok:
            raise RuntimeError("Failed to install Kotlin LSP")


if __name__ == "__main__":
    KotlinLspInstaller(ArgumentParser().parse_args()).run()
