from samplePlugins import Highlighter, FileManager, Fetcher

@Highlighter(foo=4)
def MyHighlighter(text):
    print(f"highlighted text '{text}'")

@Fetcher()
async def MyFetcher():
    return "Data"


class PythonFileManager(FileManager, foo=3):
    def __init__(self, directory):
        print(directory)
    def load_files(self, directory):
        return ['script.py']
