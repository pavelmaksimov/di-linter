import contextlib


def func_from_other_module(): ...


class KlassFromOtherModule:
    attr = 0

    def method2(self): ...


class OtherModuleException(Exception): ...


@contextlib.contextmanager
def other_module_context_manager():
    yield
