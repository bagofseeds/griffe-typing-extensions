# Authored with Claude
from ast import Import, ImportFrom
from dataclasses import fields

from griffe import Expr, ExprAttribute, ExprName, Extension


class TypingExtensionsToTyping(Extension):
    """
    Griffe extension that converts typing_extensions imports
    into typing imports. This allows mkdocstring's modernization
    option to work on typing_extensions hint (assuming they are all
    available in the most recent version of python).

    Expressions that access typing_extensions through its module
    (e.g., `tx.Literal` after `import typing_extensions as tx`)
    are rewritten as if the name had been imported from typing
    (e.g., `Literal`), so that the module prefix does not appear
    in rendered values and signatures.

    Note that hints will now cross-reference with python's `typing`,
    not with `typing_extensions`. There may be issues if objects
    imported from typing_extensions do not exist in `typing`.
    """

    def __init__(self):
        super().__init__()
        # Paths of aliases that pointed to the typing_extensions module
        self._module_aliases = set()

    def on_node(self, *, node, **kwargs):
        # This does not seem to work
        if isinstance(node, Import):
            for alias in node.names:
                if alias.name == "typing_extensions":
                    alias.name = "typing"
        elif isinstance(node, ImportFrom):
            if node.module == "typing_extensions":
                node.module = "typing"

    def on_alias_instance(self, *, alias, **kwargs):
        # This does work
        if alias.target_path == "typing_extensions":
            alias.target_path = "typing"
            self._module_aliases.add(alias.path)
        elif alias.target_path.startswith("typing_extensions."):
            alias.target_path = "typing" + alias.target_path[len("typing_extensions") :]

    def on_instance(self, *, obj, **kwargs):
        # Strip the typing_extensions module prefix from expressions
        # (`tx.Literal` -> `Literal`, resolving to `typing.Literal`)
        if obj.is_attribute or getattr(obj, "is_type_alias", False):
            obj.value = self._fix(obj.value)
            if obj.is_attribute:
                obj.annotation = self._fix(obj.annotation)
        if obj.is_function:
            obj.returns = self._fix(obj.returns)
            for parameter in obj.parameters:
                parameter.annotation = self._fix(parameter.annotation)
                parameter.default = self._fix(parameter.default)
        if obj.is_class:
            obj.bases = [self._fix(base) for base in obj.bases]
            keywords = getattr(obj, "keywords", {})
            for key, value in keywords.items():
                keywords[key] = self._fix(value)
        for decorator in getattr(obj, "decorators", []):
            decorator.value = self._fix(decorator.value)
        for type_parameter in getattr(obj, "type_parameters", []):
            type_parameter.annotation = self._fix(type_parameter.annotation)
            type_parameter.default = self._fix(type_parameter.default)

    def _fix(self, expr):
        if isinstance(expr, ExprAttribute) and self._is_module_alias(expr.first):
            values = expr.values[1:]
            first = ExprName(values[0].name, parent="typing")
            if len(values) == 1:
                return first
            values[1].parent = first
            return ExprAttribute([first, *values[1:]])
        if isinstance(expr, Expr):
            for field in fields(expr):
                # `parent` points back up the tree
                if field.name == "parent":
                    continue
                value = getattr(expr, field.name)
                if isinstance(value, list):
                    value[:] = [self._fix(item) for item in value]
                elif isinstance(value, Expr):
                    setattr(expr, field.name, self._fix(value))
        return expr

    def _is_module_alias(self, name):
        # Whether `name` refers to an alias of the typing_extensions module
        if not isinstance(name, ExprName) or isinstance(name.parent, (str, ExprName)):
            return False
        scope = name.parent
        member = getattr(name, "member", None)
        if scope is not None and member:
            scope = scope.members.get(member, scope)
        while scope is not None:
            if name.name in scope.members:
                member = scope.members[name.name]
                # Older griffe versions do not trigger `on_alias_instance`
                # for imports, so the alias may not have been rewritten
                return member.is_alias and (
                    member.path in self._module_aliases
                    or member.target_path == "typing_extensions"
                )
            scope = scope.parent
        return False
