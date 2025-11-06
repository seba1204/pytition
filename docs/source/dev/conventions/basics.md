# Basics conventions

## Comments

- Use English for all comments.
- Write comments that explain why the code does something, not what it does.
- You can use `FIXME` or `TODO` tags to indicate areas that need improvement, but provide an issue reference, with the format shown below:

    ```python
    # TODO: [#123] Refactor this function to improve performance.
    ```

## Templates

- Do not put inline CSS or JS in templates. Use static files instead.
- Use Bootstrap 5 classes and components for styling and layout.
- Use Django template inheritance to avoid code duplication.
