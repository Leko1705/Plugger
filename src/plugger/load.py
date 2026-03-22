import os.path
from typing import Callable, List, Any

from plugger.exceptions import NoSuchExtensionPointError

plugin_cache = {}
extension_cache = {}


def set_plugin_enabled(plugin: str, enabled: bool):
    plugin = os.path.abspath(plugin)
    plugin_cache[plugin]['enabled'] = enabled


def get_extensions(extension_point: str | Callable | type, enabled=True) -> List[Any]:
    if extension_point not in extension_cache:
        raise NoSuchExtensionPointError(extension_point)
    enabled_filter = lambda ext: plugin_cache[ext.plugin]['enabled'] == enabled
    return list(filter(enabled_filter, extension_cache[extension_point]))
