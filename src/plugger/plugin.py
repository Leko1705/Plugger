import functools
import importlib.util
import inspect
import sys
from pathlib import Path
from typing import List, Any, Callable, Iterable
import abc

from plugger.exceptions import InvalidSignatureException, InvalidExtensionPointError, NoSuchExtensionPointError
from plugger.decorator import decorator


class Extension:

    def __init__(self, impl, ext_pt, **kwargs):
        self.__impl = impl
        self.__name = impl.__name__
        self._extension_point = ext_pt
        for k, v in kwargs.items():
            setattr(self, k, v)
        functools.update_wrapper(self, impl)
        try:
            self.__file__ = inspect.getfile(impl)
        except (TypeError, OSError):
            self.__file__ = "unknown"

    def __str__(self):
        return str(self.__impl)

    def __repr__(self):
        return repr(self.__impl)

    def __call__(self, *args, **kwargs):
        return self.__impl(*args, **kwargs)


class Plugin:
    def __init__(self, name, manager):
        self.name = name
        self.enabled = True
        self._extensions = {}
        self._manager = manager
        self.files = set()

    @property
    def extensions(self):
        return [ext for exts in self._extensions.values() for ext in exts]

    def __enter__(self):
        self._manager._plugin_init_stack.append(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._manager._plugin_init_stack.pop()
        pass

    def load_files(self, file_path):
        with self:
            try:
                path = Path(file_path)
                module_name = path.stem  # e.g., 'my_plugin' from 'my_plugin.py'

                spec = importlib.util.spec_from_file_location(module_name, path)
                if spec is None:
                    raise ImportError(f"Could not find spec for {file_path}")

                module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module
                spec.loader.exec_module(module)
                self.files.add(str(path.absolute()))
                return module
            except RuntimeError:
                self.unload_files(file_path)

    def unload_files(self, file_paths):
        if not isinstance(file_paths, Iterable):
            file_paths = [file_paths]
        for file_path in [f for f in file_paths]:
            file_path = str(Path(file_path).absolute())
            if file_path in self.files:
                self.files.remove(file_path)
            for ext_key, extensions in [pair for pair in self._extensions.items()]:
                for extension in extensions:
                    ext_file = str(Path(extension.__file__).absolute())
                    if ext_file == file_path:
                        del self._extensions[ext_key]

    def unload(self):
        self.unload_files(self.files)
        self.enabled = False
        del self._manager._plugin_cache[self.name]

    def __hash__(self):
        return hash(self.name)


def prepare_extension_arguments_for_ep(ep, ep_kwargs, ext_kwargs):
    missing_ext_kwargs = ep_kwargs.copy()
    for k, v in ext_kwargs.items():
        if k not in ep_kwargs:
            raise SyntaxError(f"unexpected argument '{k}' for extension point {ep.__name__}")
        del missing_ext_kwargs[k]
    for k, v in missing_ext_kwargs.items():
        if v is Ellipsis:
            raise SyntaxError(f"missing argument '{k}' for extension point {ep.__name__}")
        ext_kwargs[k] = v

class PluginManager:

    _plugin_cache = {}
    _plugin_init_stack = []
    _extension_points = set()

    def new_plugin(self, name):
        if name in self._plugin_cache:
            raise ValueError(f"Plugin {name} already exists")
        plugin = Plugin(name, self)
        self._plugin_cache[name] = plugin
        return plugin

    def get_plugin(self, name) -> Plugin:
        if name not in self._plugin_cache:
            raise ValueError(f"Plugin {name} does not exist")
        return self._plugin_cache[name]

    def has_plugin(self, name):
        return name in self._plugin_cache

    def get_extensions(self, extension_point: str | Callable | type = None, enabled=True, disabled=False) -> List[Any]:
        if extension_point is None:
            return [extension for plugin in self._plugin_cache.values() for extension in plugin.extensions]

        if extension_point not in self._extension_points:
            raise NoSuchExtensionPointError(extension_point)

        extensions = []
        for plugin in self._plugin_cache.values():
            if enabled and plugin.enabled:
                extensions.extend(plugin.extensions)
            elif disabled and not plugin.enabled:
                extensions.extend(plugin.extensions)

        return list(filter(lambda ext: ext._extension_point == extension_point, extensions))

    @decorator
    def ExtensionPoint(self, ep, **ep_kwargs):
        if inspect.isfunction(ep):

            @decorator
            def extensionPointDecorator(ext, **ext_kwargs):
                extensionPointDecorator.__name__ = ep.__name__

                ep_sig = inspect.signature(ep)
                ext_sig = inspect.signature(ext)

                if [v.kind for v in ep_sig.parameters.values()] != [v.kind for v in ext_sig.parameters.values()]:
                    if not (list(ep_sig.parameters.values())[0].name == '_' and len(ext_sig.parameters) == 0):
                        raise InvalidSignatureException("signature of extension does not match the one of the extension point")
                prepare_extension_arguments_for_ep(ep, ep_kwargs, ext_kwargs)
                extension_cache = self._plugin_init_stack[-1]._extensions
                if extensionPointDecorator not in extension_cache:
                    extension_cache[extensionPointDecorator] = []
                extension_cache[extensionPointDecorator].append(Extension(ext, extensionPointDecorator, **ext_kwargs))
                return ext

            self._extension_points.add(extensionPointDecorator)
            return extensionPointDecorator

        elif inspect.isclass(ep):

            # Capture the original attributes and bases
            orig_vars = dict(ep.__dict__)
            orig_bases = ep.__bases__

            # Remove items that shouldn't be copied to a new class
            for key in ['__dict__', '__weakref__', '__init_subclass__']:
                orig_vars.pop(key, None)

            def __init_subclass__(cls, **ext_kwargs):
                super(ep, cls).__init_subclass__()
                prepare_extension_arguments_for_ep(ep, ep_kwargs, ext_kwargs)
                extension_cache = self._plugin_init_stack[-1]._extensions
                if ep not in extension_cache:
                    extension_cache[ep] = []
                extension_cache[ep].append(Extension(cls, ep))

            ep = abc.ABCMeta(ep.__name__, (abc.ABC,) + orig_bases, orig_vars)
            ep.__init_subclass__ = classmethod(__init_subclass__)
            self._extension_points.add(ep)
            return ep

        else:
            raise InvalidExtensionPointError()