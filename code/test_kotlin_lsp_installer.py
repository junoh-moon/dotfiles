import hashlib
import tarfile
import tempfile
import unittest
import zipfile
from argparse import Namespace
from pathlib import Path

from kotlin_lsp_installer import KotlinLspInstaller, ReleaseArtifact


class KotlinLspInstallerTest(unittest.TestCase):
    def setUp(self):
        self.installer = KotlinLspInstaller(Namespace())

    def test_get_artifact_prefers_standalone_across_release_formats(self):
        release_bodies = (
            (
                """
* [Download for Linux-x64](https://download-cdn.jetbrains.com/kotlin-lsp/262.2310.0/kotlin-lsp-262.2310.0-linux-x64.vsix)
* [Download for Linux-x64](https://download-cdn.jetbrains.com/kotlin-lsp/262.2310.0/kotlin-lsp-262.2310.0-linux-x64.zip) | [SHA-256 checksum](https://download-cdn.jetbrains.com/kotlin-lsp/262.2310.0/kotlin-lsp-262.2310.0-linux-x64.zip.sha256)
""",
                "https://download-cdn.jetbrains.com/kotlin-lsp/262.2310.0/kotlin-lsp-262.2310.0-linux-x64.zip",
                "zip",
            ),
            (
                """
* [Download for Linux-x64](https://download-cdn.jetbrains.com/language-server/kotlin-server/262.8190.0/kotlin-server-0.0.5-linux-amd64.vsix)
* [Download for Linux-x64](https://download-cdn.jetbrains.com/language-server/kotlin-server/262.8190.0/kotlin-server-262.8190.0.tar.gz) | [SHA-256 checksum](https://download-cdn.jetbrains.com/language-server/kotlin-server/262.8190.0/kotlin-server-262.8190.0.tar.gz.sha256)
""",
                "https://download-cdn.jetbrains.com/language-server/kotlin-server/262.8190.0/kotlin-server-262.8190.0.tar.gz",
                "tar.gz",
            ),
        )

        for body, expected_url, expected_archive_type in release_bodies:
            with self.subTest(expected_url=expected_url):
                artifact = self.installer._get_artifact_from_release_body(
                    body,
                    "linux",
                    "x64",
                )

                self.assertEqual(artifact.url, expected_url)
                self.assertEqual(artifact.checksum_url, f"{expected_url}.sha256")
                self.assertEqual(artifact.archive_type, expected_archive_type)

    def test_get_artifact_falls_back_to_vsix(self):
        body = """
* [Download for Linux-x64](https://downloads.example.com/kotlin-lsp.vsix) | [SHA-256 checksum](https://downloads.example.com/kotlin-lsp.vsix.sha256)
"""

        artifact = self.installer._get_artifact_from_release_body(
            body,
            "linux",
            "x64",
        )

        self.assertEqual(
            artifact.url,
            "https://downloads.example.com/kotlin-lsp.vsix",
        )
        self.assertEqual(artifact.archive_type, "zip")

    def test_get_artifact_uses_adjacent_checksum_link(self):
        body = """
* [Download for Linux-x64](https://downloads.example.com/kotlin-lsp.tar.gz) | [SHA-256 checksum](https://checksums.example.com/linux-x64.txt)
"""

        artifact = self.installer._get_artifact_from_release_body(
            body,
            "linux",
            "x64",
        )

        self.assertEqual(
            artifact.checksum_url,
            "https://checksums.example.com/linux-x64.txt",
        )

    def test_failed_install_keeps_current_launcher(self):
        with tempfile.TemporaryDirectory() as temporary_home:
            home = Path(temporary_home)
            self.installer.HOME = home
            old_server = home / ".local" / "kotlin-lsp" / "kotlin-server-previous"
            old_launcher = old_server / "bin" / "intellij-server"
            old_launcher.parent.mkdir(parents=True)
            old_launcher.write_text("previous installation")
            bin_dir = home / ".local" / "bin"
            bin_dir.mkdir(parents=True)
            current_link = bin_dir / "kotlin-lsp.sh"
            current_link.symlink_to(old_launcher)

            archive_path = home / "broken.tar.gz"
            archive_path.write_bytes(b"not a tar archive")
            checksum_path = home / "broken.tar.gz.sha256"
            checksum_path.write_text(
                f"{hashlib.sha256(archive_path.read_bytes()).hexdigest()}  "
                f"{archive_path.name}\n"
            )
            artifact = ReleaseArtifact(
                url=archive_path.as_uri(),
                checksum_url=checksum_path.as_uri(),
                archive_type="tar.gz",
            )

            with self.assertRaises(RuntimeError):
                self.installer._install_artifact(artifact, "262.9999.0")

            self.assertEqual(current_link.resolve(), old_launcher)
            self.assertEqual(old_launcher.read_text(), "previous installation")

    def test_successful_install_switches_to_verified_launcher(self):
        with tempfile.TemporaryDirectory() as temporary_home:
            home = Path(temporary_home)
            self.installer.HOME = home
            source_root = home / "unexpected-archive-root"
            source_launcher = source_root / "bin" / "intellij-server"
            source_launcher.parent.mkdir(parents=True)
            source_launcher.write_text(
                "#!/bin/sh\n"
                'test "$1" = "--version" || exit 1\n'
                'echo "Kotlin LSP LS-262.9999.0 (stable)"\n'
            )
            source_launcher.chmod(0o755)

            archive_path = home / "kotlin-lsp.tar.gz"
            with tarfile.open(archive_path, "w:gz") as archive:
                archive.add(source_root, arcname=source_root.name)
            checksum_path = home / "kotlin-lsp.tar.gz.sha256"
            checksum_path.write_text(
                f"{hashlib.sha256(archive_path.read_bytes()).hexdigest()}  "
                f"{archive_path.name}\n"
            )
            artifact = ReleaseArtifact(
                url=archive_path.as_uri(),
                checksum_url=checksum_path.as_uri(),
                archive_type="tar.gz",
            )

            installed_launcher = self.installer._install_artifact(
                artifact,
                "262.9999.0",
            )

            current_link = home / ".local" / "bin" / "kotlin-lsp.sh"
            self.assertEqual(current_link.resolve(), installed_launcher)
            ok, output, _ = self.installer.shell.run(f"'{current_link}' --version")
            self.assertTrue(ok)
            self.assertIn("LS-262.9999.0", output)

    def test_zip_container_and_vsix_layout_are_supported(self):
        with tempfile.TemporaryDirectory() as temporary_home:
            home = Path(temporary_home)
            self.installer.HOME = home
            source_root = home / "extension" / "server"
            source_launcher = source_root / "bin" / "intellij-server"
            source_launcher.parent.mkdir(parents=True)
            source_launcher.write_text(
                "#!/bin/sh\n"
                'test "$1" = "--version" || exit 1\n'
                'echo "LS-262.9999.0"\n'
            )

            archive_path = home / "kotlin-lsp.sit"
            with zipfile.ZipFile(archive_path, "w") as archive:
                for path in source_root.rglob("*"):
                    archive.write(path, path.relative_to(home))
            checksum_path = home / "kotlin-lsp.sit.sha256"
            checksum_path.write_text(
                f"{hashlib.sha256(archive_path.read_bytes()).hexdigest()}  "
                f"{archive_path.name}\n"
            )
            artifact = ReleaseArtifact(
                url=archive_path.as_uri(),
                checksum_url=checksum_path.as_uri(),
                archive_type="zip",
            )

            installed_launcher = self.installer._install_artifact(
                artifact,
                "262.9999.0",
            )

            self.assertTrue(installed_launcher.is_file())

    def test_cleanup_removes_obsolete_and_interrupted_install_directories(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            install_dir = Path(temporary_directory)
            current = install_dir / "kotlin-server-current"
            previous = install_dir / "kotlin-server-previous"
            obsolete = install_dir / "kotlin-server-obsolete"
            interrupted_staging = install_dir / ".staging-old"
            interrupted_backup = install_dir / ".backup-old"
            for directory in (
                current,
                previous,
                obsolete,
                interrupted_staging,
                interrupted_backup,
            ):
                directory.mkdir()

            self.installer._remove_obsolete_servers(
                install_dir,
                keep={current, previous},
            )

            self.assertTrue(current.exists())
            self.assertTrue(previous.exists())
            self.assertFalse(obsolete.exists())
            self.assertFalse(interrupted_staging.exists())
            self.assertFalse(interrupted_backup.exists())

    def test_run_skips_download_when_current_version_is_healthy(self):
        with tempfile.TemporaryDirectory() as temporary_home:
            home = Path(temporary_home)
            self.installer.HOME = home
            launcher = (
                home
                / ".local"
                / "kotlin-lsp"
                / "kotlin-server-262.9999.0"
                / "bin"
                / "intellij-server"
            )
            launcher.parent.mkdir(parents=True)
            launcher.write_text(
                "#!/bin/sh\n"
                'test "$1" = "--version" || exit 1\n'
                'echo "LS-262.9999.0"\n'
            )
            launcher.chmod(0o755)
            bin_dir = home / ".local" / "bin"
            bin_dir.mkdir(parents=True)
            (bin_dir / "kotlin-lsp.sh").symlink_to(launcher)
            self.installer._get_latest_release = lambda: {
                "tag_name": "kotlin-lsp/v262.9999.0",
                "body": "",
            }
            self.installer._get_platform_info = lambda: ("linux", "x64")

            def fail_if_installing(*_args):
                self.fail("healthy current release should not be downloaded")

            self.installer._install_artifact = fail_if_installing

            self.installer.run()


if __name__ == "__main__":
    unittest.main()
