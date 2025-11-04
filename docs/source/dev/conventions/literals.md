# Literals

## Error and status messages

Error messages are correctly formed sentences (capital letters, subject, verb, complement, period at the end).

Example:

```python
# ✅ Good
raise ValidationError(_("This field is required."))
# ❌ Bad
raise ValidationError(_("field required"))
```

## Button labels and short action messages

Button labels and short action messages are :

- necessarily short
- without a period at the end
- if possible, an infinitive verb (an action)

Example:

```html
{# ✅ Good #}
<button type="submit">{% trans "Export" %}</button>

{# ❌ Bad #}
<button type="submit">{% trans "Export signatures to CSV file." %}</button>
```

```{note}
The interface must make it clear that when you click on the Export button, it will export the signatures to CSV. This could be done with a help text near the button (tooltip are not visible on mobile, cf. [UX conventions](./ux.md)).
```
