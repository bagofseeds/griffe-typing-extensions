"""Tests for the typing_extensions to typing conversion."""

from textwrap import dedent

from griffe import load_extensions, temporary_visited_package

from griffe_typing_extensions import TypingExtensionsToTyping

CODE = dedent(
    """
    import typing
    import typing_extensions
    import typing_extensions as tx
    from typing_extensions import Literal

    AliasName: tx.TypeAlias = tx.Literal["a", "b", "c"]
    Unaliased: typing_extensions.TypeAlias = typing_extensions.Literal["a"]
    Imported: tx.TypeAlias = Literal["a"]
    Nested: tx.TypeAlias = tx.Optional[tx.Literal["a"]]
    Typing: typing.TypeAlias = typing.Literal["a"]

    def func(x: tx.Literal["a"] = "a") -> tx.Optional[int]: ...

    class Cls(tx.Protocol):
        attr: tx.Literal["a"] = "a"
    """
)


def load():
    extensions = load_extensions(TypingExtensionsToTyping)
    return temporary_visited_package(
        "package", {"__init__.py": CODE}, extensions=extensions
    )


def test_module_prefix_is_stripped() -> None:
    with load() as package:
        attr = package["AliasName"]
        assert str(attr.annotation) == "TypeAlias"
        assert str(attr.value) == "Literal['a', 'b', 'c']"
        assert attr.annotation.canonical_path == "typing.TypeAlias"
        assert attr.value.left.canonical_path == "typing.Literal"

        attr = package["Unaliased"]
        assert str(attr.value) == "Literal['a']"
        assert attr.value.left.canonical_path == "typing.Literal"


def test_nested_expressions() -> None:
    with load() as package:
        assert str(package["Nested"].value) == "Optional[Literal['a']]"

        func = package["func"]
        assert str(func.parameters["x"].annotation) == "Literal['a']"
        assert str(func.returns) == "Optional[int]"
        assert func.returns.left.canonical_path == "typing.Optional"

        cls = package["Cls"]
        assert [str(base) for base in cls.bases] == ["Protocol"]
        assert str(cls["attr"].annotation) == "Literal['a']"


def test_other_expressions_are_untouched() -> None:
    with load() as package:
        assert str(package["Imported"].value) == "Literal['a']"
        assert package["Imported"].value.left.canonical_path == "typing.Literal"
        assert str(package["Typing"].value) == "typing.Literal['a']"
