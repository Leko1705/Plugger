import functools
import inspect
import asyncio

from plugger.exceptions import InvalidSignatureException


def has_leading_positional(func):
    sig = inspect.signature(func)
    params = list(sig.parameters.values())

    if not params:
        return False

    first_param = params[0]

    valid_kinds = {
        inspect.Parameter.POSITIONAL_OR_KEYWORD,
        inspect.Parameter.POSITIONAL_ONLY
    }

    return first_param.kind in valid_kinds and first_param.default is inspect.Parameter.empty


class Decorator:
    def __init__(self, decorator_logic):
        if not has_leading_positional(decorator_logic):
            sig = inspect.signature(decorator_logic)
            sig_str = f"def {decorator_logic.__name__}{sig}:"
            raise InvalidSignatureException(f"decorated function '{sig_str}' must have at least one positional parameter")

        self.decorator_logic = decorator_logic
        functools.update_wrapper(self, decorator_logic)
        self.__signature__ = inspect.signature(decorator_logic)

    def __call__(self, *args, **kwargs):
        # Case 1: @decorator (No parens)
        if len(args) == 1 and callable(args[0]) and not kwargs:
            decorated = args[0]
            if inspect.iscoroutinefunction(self.decorator_logic):
                return asyncio.run(self.decorator_logic(decorated))

            return self.decorator_logic(decorated)

        # Case 2: @decorator(args) (With parens)
        def secondary_wrapper(decorated_after_params):
            if inspect.iscoroutinefunction(self.decorator_logic):
                return asyncio.run(self.decorator_logic(decorated, *args, **kwargs))
            return self.decorator_logic(decorated_after_params, *args, **kwargs)

        return secondary_wrapper

    def __get__(self, instance, owner):
        if instance is None:
            return self
        # When accessed as a method (obj.decorator), we return a version
        # that knows about 'instance' (self)
        @functools.wraps(self.decorator_logic)
        def bound_master_wrapper(*args, **kwargs):
            # If called as obj.decorator(target_func)
            if len(args) == 1 and callable(args[0]) and not kwargs:
                return self.decorator_logic(instance, args[0])

            # If called as obj.decorator(meta_args)(target_func)
            def secondary_wrapper(func):
                return self.decorator_logic(instance, func, *args, **kwargs)

            return secondary_wrapper

        return bound_master_wrapper


def decorator(f):
    """
    Transforms a function into a decorator
    :param f: the function to be a decorator
    :return: the function as a decorator
    """
    return Decorator(f)
