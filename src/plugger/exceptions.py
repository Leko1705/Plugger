
class InvalidSignatureException(RuntimeError):
    def __init__(self, message):
        super().__init__(message)


class NoSuchExtensionPointError(Exception):
    def __init__(self, extension_point):
        super().__init__(str(extension_point))

class InvalidExtensionPointError(Exception):
    def __init__(self):
        super().__init__("Only functions or classes can be extension points")
