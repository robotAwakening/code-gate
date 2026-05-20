from urllib.parse import urlparse

BLOCKED_APP_PACKAGES = {
    "com.google.android.youtube",
    "com.instagram.android",
}

BLOCKED_DOMAINS = {
    "youtube.com",
    "m.youtube.com",
    "youtu.be",
    "instagram.com",
    "www.instagram.com",
}

_BLOCKED_DOMAIN_SUFFIXES = ("youtube.com", "instagram.com", "youtu.be")


def is_blocked_app(package_name: str) -> bool:
    return package_name.strip().lower() in BLOCKED_APP_PACKAGES


def is_blocked_domain(host: str) -> bool:
    hostname = host.strip().lower().rstrip(".")
    if not hostname:
        return False
    if hostname in BLOCKED_DOMAINS:
        return True
    return any(hostname.endswith(f".{suffix}") for suffix in _BLOCKED_DOMAIN_SUFFIXES)


def _extract_hostname(value: str) -> str:
    raw = value.strip()
    if not raw:
        return ""

    parsed = urlparse(raw if "://" in raw else f"//{raw}", scheme="https")
    return (parsed.hostname or "").strip().lower().rstrip(".")


def is_blocked_url(url_or_host: str) -> bool:
    return is_blocked_domain(_extract_hostname(url_or_host))
