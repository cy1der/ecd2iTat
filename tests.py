import ast
from pathlib import Path
from types import SimpleNamespace
from typing import Callable, cast

import pytest


def _load_strip_keyword_function():
    module_path = Path(__file__).resolve().parent / "__init__.py"
    source = module_path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(module_path))

    function_node = next(
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "strip_keyword_from_disambiguation"
    )

    isolated_module = ast.Module(
        body=[
            ast.Import(names=[ast.alias(name="re")]),
            function_node,
        ],
        type_ignores=[],
    )
    ast.fix_missing_locations(isolated_module)

    namespace: dict[str, object] = {
        "log": SimpleNamespace(debug=lambda *args, **kwargs: None),
    }
    exec(compile(isolated_module, str(module_path), "exec"), namespace)
    return cast(Callable[[str, str], str], namespace["strip_keyword_from_disambiguation"])


strip_keyword_from_disambiguation = _load_strip_keyword_function()


@pytest.mark.parametrize(
    "disambiguation, keyword, expected",
    [
        ("explicit", "explicit", ""),
        ("original mix, explicit", "explicit", "original mix"),
        ("original mix explicit", "explicit", "original mix"),
        ("explicit, original mix", "explicit", "original mix"),
        ("explicit album version", "explicit", "album version"),
        ("explicit - original mix", "explicit", "original mix"),
        ("original mix,explicit", "explicit", "original mix"),
        ("original mix - explicit", "explicit", "original mix"),
        ("original mix (explicit)", "explicit", "original mix"),
        ("original mix ( explicit )", "explicit", "original mix"),
        ("original explicit mix", "explicit", "original mix"),
        ("album version, explicit, remix", "explicit", "album version, remix"),
        ("album version - explicit - remix", "explicit", "album version - remix"),
        ("album version | explicit | remix", "explicit", "album version | remix"),
    ],
)
def test_strip_keyword_supported_patterns(disambiguation, keyword, expected):
    assert strip_keyword_from_disambiguation(disambiguation, keyword) == expected


def test_strip_keyword_is_case_insensitive():
    result = strip_keyword_from_disambiguation("Original Mix, EXPLICIT", "explicit")
    assert result == "Original Mix"


def test_strip_keyword_returns_original_when_not_found():
    original = "original mix, clean"
    assert strip_keyword_from_disambiguation(original, "explicit") == original


@pytest.mark.parametrize(
    "disambiguation, keyword",
    [
        ("", "explicit"),
        ("original mix", ""),
        ("", ""),
    ],
)
def test_strip_keyword_handles_empty_inputs(disambiguation, keyword):
    assert strip_keyword_from_disambiguation(disambiguation, keyword) == disambiguation
