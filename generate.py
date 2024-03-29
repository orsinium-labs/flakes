from dataclasses import dataclass
from datetime import date
from email.message import Message
from functools import cached_property
from pathlib import Path
import flake8_codes
from importlib.metadata import metadata

from jinja2 import Environment, FileSystemLoader


# TODO: remove when netlify supports Python 3.9

def remove_prefix(string: str, prefix: str) -> str:
    if string.startswith(prefix):
        return string[len(prefix):]
    return string


def remove_suffix(string: str, suffix: str) -> str:
    if suffix and string.endswith(suffix):
        return string[:-len(suffix)]
    return string


@dataclass
class Plugin:
    _plugin:  flake8_codes.Plugin

    @property
    def name(self):
        return self._plugin.name

    @cached_property
    def meta(self) -> Message:
        return metadata(self.name)

    @cached_property
    def url(self) -> str:
        url = self.meta.get('home-page')
        if url == 'UNKNOWN':
            url = None
        if url is None:
            return f'https://pypi.org/project/{self.name}'
        return url

    @cached_property
    def license(self):
        license = self.meta.get('license')
        if license == 'UNKNOWN':
            license = None
        return license

    @cached_property
    def short_url(self):
        url: str = self.url
        url = remove_prefix(url, 'http://')
        url = remove_prefix(url, 'https://')
        url = remove_prefix(url, 'github.com/')
        url = remove_suffix(url, '/')
        return url

    @property
    def author(self):
        author = self.meta.get('author')
        if author is None:
            author = self.meta.get('maintainer')
        return author

    @property
    def version(self):
        return self.meta.get('version')

    @property
    def summary(self):
        return self.meta.get('summary')

    @property
    def codes(self):
        codes = flake8_codes.extract(self.name)
        return sorted(codes.items())


plugins = [Plugin(p) for p in flake8_codes.get_installed()]
plugins.sort(key=lambda p: p.name)
env = Environment(loader=FileSystemLoader('templates'))
template = env.get_template('index.html.j2')
content = template.render(
    plugins=plugins,
    today=date.today(),
    len=len,
)
public_path = Path('public')
public_path.mkdir(exist_ok=True)
(public_path / 'index.html').write_text(content)
