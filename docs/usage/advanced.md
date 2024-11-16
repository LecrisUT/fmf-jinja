# Advanced usage

Here are some more advanced design patterns that you can take advantage of.

## Recursive

By default, the fmf files are copied over in the output, and if there are new `.fmf`
files created, the generation is re-run. This allows to create arbitrarily complex
template structures. The simplest example here is creating 2D array of outputs:

```{code-block} yaml
:caption: /main.fmf

vars:
  var1: [2, 3]
  var2:  [x, y]
templates:
  path: /template
```
```{code-block} jinja
:caption: /template/main.fmf.j2

{% for A in var1 -%}
/A_{{ A }}:
  varA: {{ A }}
{% for B in var2 -%}
/A_{{ A }}/B_{{ B }}:
  varB: {{ B }}
{% endfor -%}
{% endfor -%}
```
Which expands to an intermediate fmf tree of
```{code-block} yaml
:caption: /main.fmf

/A_2:
  varA: 2
/A_2/B_x:
  varB: x
/A_2/B_y:
  varB: y
/A_3:
  varA: 3
/A_3/B_x:
  varB: x
/A_3/B_y:
  varB: y
```
```console
$ fmf show
/A_2/B_x
varA: 2
varB: x

/A_2/B_y
varA: 2
varB: y

/A_3/B_x
varA: 3
varB: x

/A_3/B_y
varA: 3
varB: y
```

:::{note}
If a templated file like `main.fmf.j2` clashes with an original `main.fmf` file in the
original fmf tree, the generated file overwrites the
:::

The recursive feature can be turned off with the `--no-recursive` flag.

### `fmf-jinja` bomb

If you want an equivalent [fork bomb] while running `fmf-jinja`, here you are:
```console
$ fmf init
$ touch main.fmf
$ ln -s main.fmf main.fmf.j2
$ fmf-jinja generate -o whatever
```

[fork bomb]: https://en.wikipedia.org/wiki/Fork_bomb
