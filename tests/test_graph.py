from pathlib import Path

from di_linter.graph import build_dependency_graph

EXAMPLE_DIR = Path.cwd() / "example"
PROJECT_DIR = EXAMPLE_DIR / "project"


def test_all_cases():
    """Checks that the flake8 plugin finds the correct dependency injections in examples."""
    graph = build_dependency_graph(PROJECT_DIR)
    assert graph == {
        "project.packet.my_module.LocalKlass": set(),
        "project.packet.my_module.LocalModuleException": set(),
        "project.packet.my_module.MyKlass": {
            "project.packet",
            "project.packet.KlassFromOtherModule",
            "project.packet.KlassFromOtherModule.attr",
            "project.packet.func_from_other_module",
            "project.packet.my_module.LocalKlass",
            "project.packet.my_module.LocalKlass.attr",
            "project.packet.my_module.local_func",
            "project.packet.other_module",
            "project.packet.other_module.attr",
            "project.packet.other_module.packet",
            "project.packet.other_module.packet.other_module",
            "project.packet.other_module.packet.other_module.KlassFromOtherModule",
            "project.packet.other_module.packet.other_module.KlassFromOtherModule.attr",
            "project.packet.other_module.packet.other_module.func_from_other_module",
        },
        "project.packet.my_module.api_router": set(),
        "project.packet.my_module.async_local_context_manager": set(),
        "project.packet.my_module.async_local_func": set(),
        "project.packet.my_module.examples_dependency_injection": {
            "project.packet",
            "project.packet.KlassFromOtherModule",
            "project.packet.KlassFromOtherModule.attr",
            "project.packet.func_from_other_module",
            "project.packet.my_module.LocalKlass",
            "project.packet.my_module.LocalKlass.attr",
            "project.packet.my_module.local_context_manager",
            "project.packet.my_module.local_func",
            "project.packet.my_module.method2",
            "project.packet.other_module",
            "project.packet.other_module.attr",
            "project.packet.other_module.packet",
            "project.packet.other_module.packet.other_module",
            "project.packet.other_module.packet.other_module.KlassFromOtherModule",
            "project.packet.other_module.packet.other_module.KlassFromOtherModule.attr",
            "project.packet.other_module.packet.other_module.func_from_other_module",
            "project.packet.other_module.packet.other_module.other_module_context_manager",
            "project.packet.other_module_context_manager",
        },
        "project.packet.my_module.examples_dependency_injection_async": {
            "project.packet.my_module.async_local_context_manager",
            "project.packet.my_module.async_local_func",
        },
        "project.packet.my_module.examples_not_dependency_injection": {
            "project.packet",
            "project.packet.OtherModuleException",
            "project.packet.my_module.LocalModuleException",
            "project.packet.my_module.api_router",
            "project.packet.my_module.local_func",
            "project.packet.other_module",
            "project.packet.other_module.packet",
            "project.packet.other_module.packet.other_module",
            "project.packet.other_module.packet.other_module.OtherModuleException",
        },
        "project.packet.my_module.examples_not_dependency_injection_via_args": {
            "project.packet.my_module.inner_func",
            "project.packet.my_module.method2"
        },
        "project.packet.my_module.lattr1": {
            "project.packet.my_module.LocalKlass",
            "project.packet.my_module.LocalKlass.attr",
        },
        "project.packet.my_module.lattr3": {
            "project.packet.other_module",
            "project.packet.other_module.attr",
        },
        "project.packet.my_module.lattr5": {
            "project.packet",
            "project.packet.KlassFromOtherModule",
            "project.packet.KlassFromOtherModule.attr",
        },
        "project.packet.my_module.lattr7": {
            "project.packet.other_module",
            "project.packet.other_module.packet",
            "project.packet.other_module.packet.other_module",
            "project.packet.other_module.packet.other_module.KlassFromOtherModule",
            "project.packet.other_module.packet.other_module.KlassFromOtherModule.attr",
        },
        "project.packet.my_module.local_context_manager": set(),
        "project.packet.my_module.local_func": set(),
        "project.packet.my_module.method2": set(),
        "project.packet.my_module.inner_func": set(),
        "project.packet.other_module.KlassFromOtherModule": set(),
        "project.packet.other_module.OtherModuleException": set(),
        "project.packet.other_module.func_from_other_module": set(),
        "project.packet.other_module.method2": set(),
        "project.packet.other_module.other_module_context_manager": set(),
    }
