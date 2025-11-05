# Under the hood

In order to better comply with the conventions of a [12-factor app](https://www.12factor.net/), Pytition is able to load configuration variables without modifying any source files or `*.py` files. The following diagrams explain how this works.

```{note}
You can still edit the variables directly in the `config/settings/**.py` files, but this is not recommended as the file may be overwritten on the next update.
```

## Settings structure

<div class="svg-frame">
  <object class="themed-diagram zoomable-svg"
      type="image/svg+xml"
      data-src-light="../../../_static/img/diagrams/light/settings_structure.svg"
      data-src-dark="../../../_static/img/diagrams/dark/settings_structure.svg"
      data="../../../_static/img/diagrams/light/settings_structure.svg">
    </object>
</div>

## Load order

<div class="svg-frame">
  <object class="themed-diagram zoomable-svg"
      type="image/svg+xml"
      data-src-light="../../../_static/img/diagrams/light/load-order.svg"
      data-src-dark="../../../_static/img/diagrams/dark/load-order.svg"
      data="../../../_static/img/diagrams/light/load-order.svg">
    </object>
</div>
