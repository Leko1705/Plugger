import os
import sys

from plugger.plugin import PluginManager, Plugin
from plugger.exceptions import NoSuchExtensionPointError, InvalidSignatureException
from plugger.decorator import decorator

def required(fn):
    fn.__isabstractmethod__ = True
    return fn


__all__ = [
    'PluginManager',
    'Plugin',
    'NoSuchExtensionPointError',
    'InvalidSignatureException',
    'decorator',
    'required'
]


def _fix_main_module_alias():
    """
    Detects if the current __main__ file corresponds to a module
    name that might be imported later, and aliases it.
    """
    main_module = sys.modules.get('__main__')
    if not main_module or not hasattr(main_module, '__file__'):
        return

    main_path = os.path.abspath(main_module.__file__)
    module_name = os.path.splitext(os.path.basename(main_path))[0]

    if module_name not in sys.modules:
        sys.modules[module_name] = main_module

_fix_main_module_alias()
