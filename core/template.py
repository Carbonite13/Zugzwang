from jinja2 import Environment
from jinja2.loaders import FileSystemLoader

from config import config

__all__ = ["env"]

env = Environment(
    loader=FileSystemLoader(
        searchpath=config.TEMPLATE_DIRECTORY,
        encoding='utf-8',
        followlinks=False,
    ),
    auto_reload=True if config.PROFILE == "dev" else False,
)

