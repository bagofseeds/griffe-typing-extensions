# griffe-typing-extensions

A `griffe` extension that converts `typing_extensions` imports
into `typing` imports. This allows `mkdocstrings`' modernization
option to work on `typing_extensions` hints (assuming they are all
available in the most recent version of python).

Names accessed through the module (e.g., `tx.Literal` after
`import typing_extensions as tx`) are rewritten as if they had been
imported from `typing` (e.g., `Literal`), so that the module prefix
does not show up in rendered values and signatures.

Note that hints will now cross-reference with `typing`,
not with `typing_extensions`. There may be issues if objects 
imported from `typing_extensions` do not exist in `typing`.
