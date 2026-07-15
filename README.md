# griffe-typing-extensions

A `griffe` extension that converts `typing_extensions` imports
into `typing` imports. This allows `mkdocstrings`' modernization
option to work on `typing_extensions` hints (assuming they are all
available in the most recent version of python).

Note that hints will now cross-reference with `typing`,
not with `typing_extensions`. There may be issues if objects 
imported from `typing_extensions` do not exist in `typing`.
