import subprocess
from pathlib import Path


EXAMPLE_DIR = Path.cwd() / "example"
PROJECT_DIR = EXAMPLE_DIR / "project"
PACKET_DIR = PROJECT_DIR / "packet"
MY_MODULE_PATH = PACKET_DIR / "my_module.py"


def test_all_cases():
    """Checks that the flake8 plugin finds the correct dependency injections in examples."""
    result = subprocess.run(
        ["flake8", "--select=DI", str(MY_MODULE_PATH)],
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0

    output = result.stdout or result.stderr
    assert "DI001 Dependency injection:" in output

    expected_injections = [
        "local_func()",
        "LocalKlass()",
        "lc = LocalKlass()",
        "LocalKlass().method2()",
        "x = LocalKlass.attr",
        "x2 = LocalKlass().attr",
        "func_from_other_module()",
        "alc = KlassFromOtherModule()",
        "KlassFromOtherModule().method2()",
        "a1 = KlassFromOtherModule.attr",
        "a2 = KlassFromOtherModule().attr",
        "other_module.func_from_other_module()",
        "ert = other_module.KlassFromOtherModule()",
        "other_module.KlassFromOtherModule().method2()",
        "f1 = other_module.KlassFromOtherModule.attr",
        "f2 = other_module.KlassFromOtherModule().attr",
        "project.packet.other_module.func_from_other_module()",
        "ghj = project.packet.other_module.KlassFromOtherModule()",
        "project.packet.other_module.KlassFromOtherModule().method2()",
        "g1 = project.packet.other_module.KlassFromOtherModule.attr",
        "g2 = project.packet.other_module.KlassFromOtherModule().attr",
        "with local_context_manager():",
        "with other_module_context_manager():",
        "with project.packet.other_module.other_module_context_manager():",
        "with other_module.other_module_context_manager():",
        "await async_local_func()",
        "async with async_local_context_manager():",
    ]

    for injection in expected_injections:
        assert f"DI001 Dependency injection: {injection}" in output, (
            f"Injection not found: {injection}"
        )

    not_expected_injections = [
        "raise LocalModuleException()",
        "raise OtherModuleException()",
        "FastAPI()",
        "analyze_param()",
        "local_func()  # di: skip",
        "func_in_args()",
        "KlassInArgs()",
    ]

    for not_injection in not_expected_injections:
        assert f"DI001 Dependency injection: {not_injection}" not in output, (
            f"False injection found: {not_injection}"
        )
