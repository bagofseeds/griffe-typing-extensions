# Authored with Claude
from ast import Import, ImportFrom

from griffe import Extension


class TypingExtensionsToTyping(Extension):
  """
  Griffe extension that converts typing_extensions imports
  into typing imports. This allows mkdocstring's modernization
  option to work on typing_extensions hint (assuming they are all
  available in the most recent version of python).
  
  Note that hints will now cross-reference with python's `typing`,
  not with `typing_extensions`. There may be issues if objects 
  imported from typing_extensions do not exist in `typing`.
  """

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
        elif alias.target_path.startswith("typing_extensions."):
            alias.target_path = "typing" + alias.target_path[len("typing_extensions") :]
