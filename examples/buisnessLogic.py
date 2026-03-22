import asyncio
from extensionPointDef import pm, Highlighter, FileManager, Fetcher


with pm.new_plugin("MyPluginName") as plugin:
    print(plugin.name)
    plugin.load_files("./samplePlugin.py")

for highlighter in pm.get_extensions(extension_point=Highlighter):
    print(highlighter.__name__)
    print(highlighter.foo)
    highlighter('Hello Extension!')
    print(highlighter.__file__)

print("=" * 20)

for highlighter in pm.get_extensions(extension_point=FileManager):
    extension_instance = highlighter("Im a python file manager")
    print(highlighter)
    print(highlighter.__file__)

print("=" * 20)

for fetcher in pm.get_extensions(extension_point=Fetcher):
    print(asyncio.run(fetcher()))

print("=" * 20)

pm.get_plugin("MyPluginName").unload()  # remove the plugin
print(pm.has_plugin("MyPluginName"))

