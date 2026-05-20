import unittest

from code_gate.blocking_targets import is_blocked_app, is_blocked_domain, is_blocked_url


class BlockingTargetsTests(unittest.TestCase):
    def test_blocked_apps_match_expected_packages(self) -> None:
        self.assertTrue(is_blocked_app("com.google.android.youtube"))
        self.assertTrue(is_blocked_app("com.instagram.android"))

    def test_blocked_apps_are_normalized(self) -> None:
        self.assertTrue(is_blocked_app(" COM.GOOGLE.ANDROID.YOUTUBE "))
        self.assertFalse(is_blocked_app("com.google.android.apps.youtube.music"))

    def test_blocked_domains_include_subdomains(self) -> None:
        self.assertTrue(is_blocked_domain("youtube.com"))
        self.assertTrue(is_blocked_domain("m.youtube.com"))
        self.assertTrue(is_blocked_domain("watch.youtube.com"))
        self.assertTrue(is_blocked_domain("www.instagram.com"))
        self.assertTrue(is_blocked_domain("help.instagram.com"))
        self.assertTrue(is_blocked_domain("youtu.be"))
        self.assertTrue(is_blocked_domain("foo.youtu.be"))

    def test_non_blocked_domain_returns_false(self) -> None:
        self.assertFalse(is_blocked_domain("example.com"))
        self.assertFalse(is_blocked_domain(""))

    def test_url_matching_handles_full_urls_and_hosts(self) -> None:
        self.assertTrue(is_blocked_url("https://youtube.com/watch?v=abc"))
        self.assertTrue(is_blocked_url("http://m.youtube.com/shorts/123"))
        self.assertTrue(is_blocked_url("www.instagram.com/reel/xyz"))
        self.assertTrue(is_blocked_url("youtu.be/abc"))
        self.assertFalse(is_blocked_url("https://github.com/"))
        self.assertFalse(is_blocked_url("   "))


if __name__ == "__main__":
    unittest.main()
