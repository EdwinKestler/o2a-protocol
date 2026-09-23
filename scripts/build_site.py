#!/usr/bin/env python3
"""Validate and export only the curated public site. No third-party packages."""
from html.parser import HTMLParser
from pathlib import Path
import re
import shutil
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "site"
DEST = ROOT / ".site-dist"
PUBLIC_FILES = (
    "index.html", "guide.html", "assets/style.css", "assets/site.js",
    "assets/mark.svg", "assets/protocol-flow.svg", "assets/protocol-stack.svg",
    "assets/protocol-pipeline.svg", "robots.txt", ".nojekyll",
)


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.links = []
        self.h1_count = 0
        self.lang = None
        self.title = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            assert attrs["id"] not in self.ids, f"Duplicate id: {attrs['id']}"
            self.ids.add(attrs["id"])
        if tag == "html":
            self.lang = attrs.get("lang")
        if tag == "title":
            self.title = True
        if tag == "h1":
            self.h1_count += 1
        if tag == "img":
            assert "alt" in attrs, "Image missing alternative text"
        for key in ("href", "src"):
            if key in attrs:
                self.links.append(attrs[key])


def main():
    assert not SOURCE.is_symlink(), "Site source must not be a symlink"
    actual = {str(p.relative_to(SOURCE)) for p in SOURCE.rglob("*") if p.is_file()}
    assert actual == set(PUBLIC_FILES), f"Review public file allowlist: {actual ^ set(PUBLIC_FILES)}"
    pages = {}
    for name in PUBLIC_FILES:
        path = SOURCE / name
        assert all(not p.is_symlink() for p in (path, *path.parents)), "Symlinks are not publishable"
        content = path.read_text()
        assert not re.search(r"/home/|/media/|\.palimnex|PRIVATE KEY", content), f"Private path/material: {name}"
        # Avoid publishing identifiable artist records or social-account URLs.
        assert not re.search(
            r"https?://(?:open\.spotify\.com/(?:[^/]+/)?artist/|"
            r"music\.apple\.com/[^/]+/artist/|music\.amazon\.com/artists/|"
            r"(?:www\.)?deezer\.com/(?:[^/]+/)?artist/|tidal\.com/artist/|"
            r"musicbrainz\.org/artist/|(?:www\.)?youtube\.com/(?:channel/|@))",
            content, re.I,
        ), f"Individual artist URL in {name}"
        if name.endswith(".html"):
            page = Page()
            page.feed(content)
            assert page.lang == "en" and page.title and page.h1_count == 1, f"Document structure: {name}"
            pages[name] = page
    for name, page in pages.items():
        for link in page.links:
            url = urlsplit(link)
            if url.scheme or url.netloc:
                assert url.scheme == "https", f"Unexpected external URL: {link}"
                continue
            assert not url.path.startswith("/"), f"Use project-relative URLs: {link}"
            target = ((SOURCE / name).parent / unquote(url.path)).resolve() if url.path else SOURCE / name
            relative = str(target.relative_to(SOURCE))
            assert relative in PUBLIC_FILES, f"Missing public file: {name} -> {link}"
            if url.fragment:
                assert relative in pages and unquote(url.fragment) in pages[relative].ids, f"Missing anchor: {link}"
    assert not DEST.is_symlink(), "Output directory must not be a symlink"
    if DEST.exists():
        shutil.rmtree(DEST)
    for name in PUBLIC_FILES:
        destination = DEST / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(SOURCE / name, destination)
    print(f"Validated {len(pages)} pages; exported {len(PUBLIC_FILES)} public files to {DEST.name}/")


if __name__ == "__main__":
    main()
