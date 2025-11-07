# Python coding style

## Comments and docstrings

- Write docstrings for all public modules, functions, classes, and methods.
- Use NumPy style for docstrings (cf. [below](#numpy-docstring-sections)).
- Use sentences like in comments:
  - start with a capital letter,
  - DO NOT end with a full stop if it's a short phrase.

```python
# ✅ Good
# Generate storage path
storage_path = (
    f"{name_part}-{file_hash}{ext_part}"
    if INCLUDE_ORIGINAL_FILENAME
    else f"{file_hash}{ext_part}"
)
# ❌ Bad
# this part generates storage path.
# genration of storage path
# ...
```

### NumPy docstring sections

```python
def add(a: int, b: int) -> int:
    """
    Add two integers.

    Parameters
    ----------
    a : int
        The first integer.
    b : int
        The integers to add.
    Returns
    -------
    int
        The sum of the two integers.
    """
    return a + b
```

List of sections:

- `Short summary`: a sentence summarize the function's purpose
  - one line at the top to
  - start with a capital letter
  - ends without a full stop
  - DO NOT begin with "This function ..."
  - use imperative mood (e.g., "Return", "Compute", "Check")
- `Extended summary` [*optional*]: a longer description for specific details
  - multiple lines
  - separated from the short summary by a blank line
- `Parameters`: a list of parameters
  - each parameter has a name, type, and description
- `Returns`: the return value(s)
  - specify the type and description
- `Yields` [*optional*]: for generator functions
- `Attributes` [*optional*]: for class docstrings, list of attributes
- `Raises` [*optional*]: exceptions that the function may raise
- `References` [*optional*]: citations or external references
  - for academic or technical references (e.g., papers, articles)
- `Examples` [*optional*]: usage examples
  - use triple backticks for code blocks
  - can include multiple examples
- `See Also` [*optional*]: related functions or classes
  - list of related items with brief descriptions
- `Notes` [*optional*]: additional information or clarifications
  - for implementation details or caveats
