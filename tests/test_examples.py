import subprocess
from pathlib import Path

import pytest


EXAMPLE_DIR = Path.cwd().parent / "example"
PROJECT_DIR = EXAMPLE_DIR / "project"
PACKET_DIR = PROJECT_DIR / "packet"
MY_MODULE_PATH = PACKET_DIR / "my_module.py"


def test_flake8_plugin_on_my_module():
    """Проверяет, что flake8 плагин находит правильные инъекции зависимостей в my_module.py."""
    # Запускаем flake8 с плагином DI на тестовом файле
    result = subprocess.run(
        ["flake8", "--select=DI", str(MY_MODULE_PATH)],
        capture_output=True,
        text=True,
    )

    # Проверяем, что процесс завершился с ошибкой (найдены инъекции зависимостей)
    assert result.returncode != 0

    # Проверяем, что в выводе есть сообщения об инъекциях зависимостей
    output = result.stdout or result.stderr
    assert "DI001 Dependency injection:" in output

    # Проверяем, что найдены ожидаемые инъекции зависимостей
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
        assert f"DI001 Dependency injection: {injection}" in output, f"Не найдена инъекция: {injection}"

    # Проверяем, что не найдены ложные инъекции зависимостей
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
        assert f"DI001 Dependency injection: {not_injection}" not in output, f"Найдена ложная инъекция: {not_injection}"


def test_di_linter_on_packet():
    """Проверяет, что di-linter находит правильные инъекции зависимостей в директории packet."""
    # Запускаем di-linter на тестовой директории
    result = subprocess.run(
        ["di-linter", str(PACKET_DIR)],
        capture_output=True,
        text=True,
    )

    # Проверяем, что процесс завершился с ошибкой (найдены инъекции зависимостей)
    assert result.returncode != 0

    # Проверяем, что в выводе есть сообщения об инъекциях зависимостей
    # Сообщения об инъекциях зависимостей выводятся в stderr
    output = result.stderr
    assert "Dependency injection:" in output

    # Проверяем, что найдены ожидаемые инъекции зависимостей
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
        assert f"Dependency injection: {injection}" in output, f"Не найдена инъекция: {injection}"

    # Проверяем, что не найдены ложные инъекции зависимостей
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
        assert f"Dependency injection: {not_injection}" not in output, f"Найдена ложная инъекция: {not_injection}"


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
