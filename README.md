# 🔌 Plugger

**A lightweight, type-safe Plugin Management Framework for Python.**

Plugger allows you to build extensible applications using a "Registry and Extension" pattern. Define extension points using decorators, enforce interfaces with `@required`, and manage plugin lifecycles (load/unload) with ease.

---

## ✨ Features

* 🏗️ **Extension Points**: Define what can be extended using functions or classes.
* 🛡️ **Interface Enforcement**: Use `@required` to ensure plugins implement the necessary logic.
* 🔄 **Lifecycle Management**: Context-managed plugin loading and explicit unloading.
* 🧩 **Universal Decorators**: A built-in, `eval()`-free decorator utility to handle metadata and signature preservation.
* ⚡ **Async Native**: Supports asynchronous extension points out of the box.

---

## 🚀 Quick Start

### 1. Define Extension Points
Use the `PluginManager` to define what your application "hooks" into.

```python
from plugger import PluginManager, required

pm = PluginManager()

@pm.ExtensionPoint(foo=...)  # use Ellipsis to define a required argument without a default value
def Highlighter(text):
    return Highlighter

@pm.ExtensionPoint
class FileManager:
    @required
    def load_files(self, directory): ...
```

### 2. Implement a Plugin

```python
@Highlighter(foo=4)
def MyHighlighter(text):
    print(f"Highlighting: {text}")

class PythonFileManager(FileManager, foo=3):
    def load_files(self, directory):
        return ['script.py']
```

### 3. Manage and Execute

Load files dynamically or access extensions through the manager

```python
with pm.new_plugin("MyPlugin") as plugin:
    plugin.load_files("./addons.py")

# Iterate through all registered highlighters
for highlighter in pm.get_extensions(extension_point=Highlighter):
    highlighter('Hello World!')
    print(highlighter.foo)  # 4
```

## 🛡️ The "Decorator" Utility

Included in Plugger is a professional-grade decorator factory used internally to power the extension system. It ensures that when you wrap a function as an extension:

- Signatures are preserved for IDEs.

- Async functions remain awaitable.

- Class methods bind correctly to self.

## 📦 Installation

```shell
pip install plugger
```

## ⚖️ License

Distributed under the MIT License. See LICENSE for more information.
