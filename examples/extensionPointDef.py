from plugger import PluginManager, required

pm = PluginManager()

@pm.ExtensionPoint(foo=...)
def Highlighter(text):
    return Highlighter

@pm.ExtensionPoint
def Fetcher():
    return Fetcher


@pm.ExtensionPoint(foo=...)
class FileManager:

    @required
    def load_files(self, directory): ...

    def open_file(self, file_path):
        print('opening file', file_path)
