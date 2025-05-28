import contextlib
import functools
from functools import lru_cache

import fastapi.dependencies.models
import project.packet.other_module
from fastapi import FastAPI, APIRouter
from fastapi.dependencies.utils import analyze_param
from project.packet import other_module
from project.packet.other_module import (
    KlassFromOtherModule,
    func_from_other_module,
    OtherModuleException,
    other_module_context_manager,
)

api_router = APIRouter()


class LocalKlass:
    attr = 0

    def method2(self):
        pass


class LocalModuleException(Exception): ...


def local_func(): ...


async def async_local_func(): ...


@contextlib.contextmanager
def local_context_manager():
    yield


@contextlib.asynccontextmanager
async def async_local_context_manager():
    yield


def examples_dependency_injection():
    # These are examples of addiction injections,
    # because they are called within other objects and because they are prohibited for project objects:
    local_func()
    LocalKlass()
    lc = LocalKlass()
    LocalKlass().method2()
    x = LocalKlass.attr
    x2 = LocalKlass().attr

    func_from_other_module()
    alc = KlassFromOtherModule()
    KlassFromOtherModule().method2()
    a1 = KlassFromOtherModule.attr
    a2 = KlassFromOtherModule().attr

    other_module.func_from_other_module()
    ert = other_module.KlassFromOtherModule()
    other_module.KlassFromOtherModule().method2()
    f1 = other_module.KlassFromOtherModule.attr
    f2 = other_module.KlassFromOtherModule().attr

    project.packet.other_module.func_from_other_module()
    ghj = project.packet.other_module.KlassFromOtherModule()
    project.packet.other_module.KlassFromOtherModule().method2()
    g1 = project.packet.other_module.KlassFromOtherModule.attr
    g2 = project.packet.other_module.KlassFromOtherModule().attr

    with local_context_manager():
        pass
    with other_module_context_manager():
        pass
    with project.packet.other_module.other_module_context_manager():
        pass
    with other_module.other_module_context_manager():
        pass


async def examples_dependency_injection_async():
    # These are examples of addiction injections,
    # because they are called within other objects and because they are prohibited for project objects:
    await async_local_func()
    async with async_local_context_manager():
        pass


@functools.lru_cache  # Not an injection
def examples_not_dependency_injection():
    # These are examples of not injection of dependence, because they are exceptions.
    if 0:
        raise LocalModuleException()
    if 0:
        raise OtherModuleException()
    if 0:
        raise project.packet.other_module.OtherModuleException()
    if 0:
        raise other_module.OtherModuleException()

    # These are examples of not injections of dependence,
    # because they are permitted for third -party and standard modules:
    apr = api_router
    FastAPI()
    analyze_param()
    fastapi.dependencies.models.field()
    str()

    # These are examples of not injections of dependencies, because the comment indicates the exclusion flag/
    local_func()  # di: skip


@lru_cache(maxsize=None)  # Not an injection
def examples_not_dependency_injection_via_args(
    func_in_args,
    KlassInArgs,
):
    # These are examples of not injections of dependencies, because they are transmitted through arguments, so allowed.
    func_in_args()
    KlassInArgs()
    a = KlassInArgs.attr
    b = KlassInArgs().attr
    KlassInArgs.method2()
    KlassInArgs().method2()


examples_not_dependency_injection_via_args(
    func_in_args=func_from_other_module,
    KlassInArgs=KlassFromOtherModule,
)

examples_not_dependency_injection_via_args(
    func_in_args=other_module.func_from_other_module,
    KlassInArgs=other_module.KlassFromOtherModule,
)

examples_not_dependency_injection_via_args(
    func_in_args=project.packet.other_module.func_from_other_module,
    KlassInArgs=project.packet.other_module.KlassFromOtherModule,
)

examples_not_dependency_injection_via_args(
    func_in_args=local_func,
    KlassInArgs=LocalKlass,
)


class MyKlass:
    # This is not injections of dependencies, because it is transmitted through class attributes.
    attr1 = LocalKlass.attr
    attr3 = KlassFromOtherModule.attr
    attr5 = other_module.KlassFromOtherModule.attr
    attr7 = project.packet.other_module.KlassFromOtherModule.attr
    klass1 = LocalKlass
    klass2 = KlassFromOtherModule
    klass3 = other_module.KlassFromOtherModule
    klass4 = project.packet.other_module.KlassFromOtherModule
    func1 = local_func
    func2 = func_from_other_module
    func3 = other_module.func_from_other_module
    func4 = project.packet.other_module.func_from_other_module


# This is not injections of dependencies, because they are caused not within other objects.
LocalKlass()
local_func()
KlassFromOtherModule()
func_from_other_module()
other_module.KlassFromOtherModule()
other_module.func_from_other_module()
project.packet.other_module.KlassFromOtherModule()
project.packet.other_module.func_from_other_module()

lattr1 = LocalKlass.attr
lattr3 = KlassFromOtherModule.attr
lattr5 = other_module.KlassFromOtherModule.attr
lattr7 = project.packet.other_module.KlassFromOtherModule.attr

with local_context_manager():
    pass
with other_module_context_manager():
    pass
with project.packet.other_module.other_module_context_manager():
    pass
with other_module.other_module_context_manager():
    pass
