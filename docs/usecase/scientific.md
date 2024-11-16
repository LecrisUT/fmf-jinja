# Scientific calculation

The majority of scientific programs have highly specific workflows with custom input
file formats, specific file structure formats and little workflow support for chaining
calculations. This project can help bridge the limitations of the scientific program.

In this example we will take `quantum-espresso` as an example.

## Use-case: Running an array of calculations

A simple example to explore here is running convergence calculations e.g. varying the
$k$-point grid:
```{code-block} jinja
:caption: /template/pw.scf.in.j2

&CONTROL
  calculation = 'scf',
  prefix = 'silicon',
  outdir = './tmp/'
/

&SYSTEM
  ibrav =  2,
  celldm(1) = 10.26,
  nat =  2,
  ntyp = 1,
  ecutwfc = {{ ecutwfc }},
  nbnd = 8
/

&ELECTRONS
/

ATOMIC_SPECIES
  Si 28.086 Si.pz-vbc.UPF

ATOMIC_POSITIONS (alat)
  Si 0.0 0.0 0.0
  Si 0.25 0.25 0.25

K_POINTS (automatic)
  {{ n_k }} {{ n_k }} {{ n_k }} 0 0 0
```
```{code-block} yaml
:caption: main.fmf

templates: /template
vars:
  ecutwfc: 30
/k_2:
  vars+:
    n_k: 2
/k_4:
  vars+:
    n_k: 4
/k_6:
  vars+:
    n_k: 6
```

Since fmf structure has a filestructure, it is easy to loop over all variants and
perform the calculations, e.g. a full workflow can look like:
```console
$ fmf-jinja generate -o qe-run
$ pushd qe-run
$ for path in $(fmf ls); do
> pushd "$(pwd)$path"
> pw.x < pw.scf.in > pw.scf.out
> popd
> done
$ popd
```

## Use-case: Linking calculations

Traditionally most scientific programs assume you run each step of the calculation in
the same directory, but this can easily explode the complexity of the folders making it
hard to track what files come from where. Here we recommend using symlinks to the
necessary files of the previous step.

Here we will give an example of calculating the band structure and here we will show
how you can take full advantage of the Jinja templating engine.

Here we will show how you can take full advantage of the Jinja templating engine. We
start from a base template containing the common general data
```{code-block} jinja
:caption: /template/base.j2

{% block Control %}
&CONTROL
  calculation = '{% block Calculation required%}{% endblock +%}',
  prefix = 'silicon',
  outdir = './tmp/'
/
{% endblock %}

{% block System %}
&SYSTEM
  ibrav =  2,
  celldm(1) = 10.26,
  nat =  2,
  ntyp = 1,
  ecutwfc = {{ ecutwfc|default(30) }},
  nbnd = 8
/
{% endblock %}

{% block Electrons %}
&ELECTRONS
/
{% endblock %}

{% block Atomic %}
ATOMIC_SPECIES
  Si 28.086 Si.pz-vbc.UPF

ATOMIC_POSITIONS (alat)
  Si 0.0 0.0 0.0
  Si 0.25 0.25 0.25
{% endblock %}

{% block KPoints %}
K_POINTS (automatic)
  {{ n_k }} {{ n_k }} {{ n_k }} 0 0 0
{% endblock %}
```
from which we inherit to define the `scf` and the `bands` input files, overriding the
[`block`] as needed.
```{code-block} jinja
:caption: /template/scf/pw.in.j2

{% extends "base.inp.j2" %}
{% block CalcMode %}scf{% endblock %}
```
```{code-block} jinja
:caption: /template/bands/pw.in.j2

{% extends "base.inp.j2" %}
{% block CalcMode %}bands{% endblock %}
{% block KPoints %}
5
  0.0000 0.5000 0.0000 {{ 2 * n_k }}  !L
  0.0000 0.0000 0.0000 {{ 3 * n_k }}  !G
  -0.500 0.0000 -0.500 {{ n_k }}  !X
  -0.375 0.2500 -0.375 {{ 3 * n_k }}  !U
  0.0000 0.0000 0.0000 {{ 2 * n_k }}  !G
{% endblock %}
```

From which we use the following fmf tree:

```{code-block} yaml
:caption: main.fmf

templates:
  exclude:
    - base.j2
vars: {}
/scf:
  templates+:
    path: /template/scf
  vars+:
    n_k: 6
/bands:
  templates+:
    path: /template/bands
  vars+:
    n_k: 10
  links:
    tmp: /scf/tmp
```

:::{caution}
Currently `fmf-jinja` does not support relative paths in the [`extends`] directive,
therefore you will have to make symbolic links to the `base.j2` and add it to the
{term}`exclude <templates[].exclude>` key in order to avoid generating this
intermediate file.
:::

And a simple workflow could look like:
```console
$ fmf-jinja generate -o qe-run
$ pushd qe-run
$ for calc in scf bands; do
> pushd "$calc"
> pw.x < pw.in > pw.out
> popd
> done
$ popd
```

The example here is not ideal because when running the `/bands` calculation the `tmp`
folder is overwritten, however there are other workflows like the Wannier calculation
which can be designed to not overwrite the previous calculation's files. This example
is simply used to illustrate the workflow design using `fmf-jinja.`

[`extends`]: inv:jinja#extends
[`block`]: inv:jinja#blocks
