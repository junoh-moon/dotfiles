import unittest
from argparse import Namespace

from kotlin_lsp_installer import KotlinLspInstaller


class KotlinLspInstallerTest(unittest.TestCase):
    def setUp(self):
        self.installer = KotlinLspInstaller(Namespace())

    def test_get_vsix_url_from_current_release_body(self):
        release_body = """### v262.8190.0
- :test_tube: "Kotlin by JetBrains" extension v0.0.5 for VS Code

  Includes Kotlin Language Server bundled for use with Visual Studio Code.

    * [Download for Linux-x64](https://download-cdn.jetbrains.com/language-server/kotlin-server/262.8190.0/kotlin-server-0.0.5-linux-amd64.vsix)&nbsp;&nbsp;|&nbsp;&nbsp;[SHA-256 checksum](https://download-cdn.jetbrains.com/language-server/kotlin-server/262.8190.0/kotlin-server-0.0.5-linux-amd64.vsix.sha256)

- :card_index_dividers: **Standalone Kotlin LSP Archive**

  Standalone Kotlin Language Server version for editors other than VS Code.

    * [Download for Linux-x64](https://download-cdn.jetbrains.com/language-server/kotlin-server/262.8190.0/kotlin-server-262.8190.0.tar.gz)&nbsp;&nbsp;|&nbsp;&nbsp;[SHA-256 checksum](https://download-cdn.jetbrains.com/language-server/kotlin-server/262.8190.0/kotlin-server-262.8190.0.tar.gz.sha256)
"""

        url = self.installer._get_vsix_url_from_release_body(
            release_body,
            "linux",
            "x64",
        )

        self.assertEqual(
            url,
            "https://download-cdn.jetbrains.com/language-server/kotlin-server/262.8190.0/kotlin-server-0.0.5-linux-amd64.vsix",
        )

    def test_get_vsix_url_ignores_standalone_archive_when_it_appears_first(self):
        release_body = """
    * [Download for Linux-x64](https://download-cdn.jetbrains.com/language-server/kotlin-server/262.8190.0/kotlin-server-262.8190.0.tar.gz)
    * [Download for Linux-x64](https://download-cdn.jetbrains.com/language-server/kotlin-server/262.8190.0/kotlin-server-0.0.5-linux-amd64.vsix)
"""

        url = self.installer._get_vsix_url_from_release_body(
            release_body,
            "linux",
            "x64",
        )

        self.assertEqual(
            url,
            "https://download-cdn.jetbrains.com/language-server/kotlin-server/262.8190.0/kotlin-server-0.0.5-linux-amd64.vsix",
        )

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


if __name__ == "__main__":
    unittest.main()
