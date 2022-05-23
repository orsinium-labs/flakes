from dataclasses import dataclass
from email.message import Message
from functools import cached_property
from pathlib import Path
import flake8_codes
from importlib.metadata import metadata

from jinja2 import Environment, FileSystemLoader


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
    def url(self):
        return self.meta.get('home-page')

    @cached_property
    def short_url(self):
        url: str = self.url
        url = url.removeprefix('http://')
        url = url.removeprefix('https://')
        url = url.removeprefix('github.com/')
        url = url.removesuffix('/')
        return url

    @cached_property
    def author(self):
        return self.meta.get('author')

    @cached_property
    def version(self):
        return self.meta.get('version')

    @property
    def codes(self):
        codes = flake8_codes.extract(self.name)
        return sorted(codes.items())


plugins = [Plugin(p) for p in flake8_codes.get_installed()]
plugins.sort(key=lambda p: p.name)
env = Environment(loader=FileSystemLoader('templates'))
template = env.get_template('index.html.j2')
content = template.render(plugins=plugins)
public_path = Path('public')
public_path.mkdir(exist_ok=True)
(public_path / 'index.html').write_text(content)
