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


if __name__ == "__main__":
    unittest.main()
