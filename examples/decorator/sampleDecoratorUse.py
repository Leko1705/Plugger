import asyncio
from plugger import decorator


@decorator
def MyDecorator_sync(fn):
    def inner(*args, **kwargs):
        print(f"Called {fn.__name__}")
        return fn(*args, **kwargs)
    return inner


@decorator
async def MyDecorator_async(fn):
    def inner(*args, **kwargs):
        print(f"Called {fn.__name__}")
        return fn(*args, **kwargs)
    return inner


@MyDecorator_sync
def MyDecoratedFunction_1():
    return "A"


@MyDecorator_sync
async def MyDecoratedFunction_2():
    return "B"


@MyDecorator_async
def MyDecoratedFunction_3():
    return "C"


@MyDecorator_async
async def MyDecoratedFunction_4():
    return "D"


print(MyDecoratedFunction_1())  # decorator decorates function
print(asyncio.run(MyDecoratedFunction_2()))  # decorator decorated async function
print(MyDecoratedFunction_3())  # async decorator decorates function
print(asyncio.run(MyDecoratedFunction_4()))  # async decorator decorates async function
