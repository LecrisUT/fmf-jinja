# FMF-Jinja

[![CI Status][ci-badge]][ci-link]
[![Codecov Status][codecov-badge]][codecov-link]

[![Documentation Status][rtd-badge]][rtd-link]

<!-- SPHINX-START -->

[Jinja templating engine][jinja] using [fmf metadata][fmf].

## Concept

The scope of this project is to take a templated folder and generate *multiple* output
folders with relation to one another. Consider the following fmf file example in
[`example/minimal`]:

```yaml
var1: 42
var2: Default value

/rootA:
/rootB:
  var2: Overwritten
```

This is interpreted by fmf as:

```console
$ fmf show --path example/minimal
/rootA
var1: 42
var2: Default value

/rootB
var1: 42
var2: Overwritten
```

These variables (`var1`, `var2`) are then used as variables inside a jinja template
creating templated folders under `rootA` and `rootB` with their respective values. Try
it out by running

```console
$ fmf-jinja -r example/minimal generate -o /path/to/some/output/folder
```

<!-- SPHINX-END -->

To appreciate the full capabilities see the [fmf features] and [jinja template guide].
Also check the [online documentation] for more examples and detailed usage guide.

[ci-badge]: https://github.com/LecrisUT/fmf-jinja/actions/workflows/ci.yaml/badge.svg?branch=main&event=push
[ci-link]: https://github.com/LecrisUT/fmf-jinja/actions?query=branch%3Amain+event%3Apush
[codecov-badge]: https://codecov.io/gh/LecrisUT/fmf-jinja/graph/badge.svg?token=WCTLWU6M2O
[codecov-link]: https://codecov.io/gh/LecrisUT/fmf-jinja
[fmf]: https://fmf.readthedocs.io
[fmf features]: https://fmf.readthedocs.io/en/stable/features.html
[jinja]: https://jinja.palletsprojects.com
[jinja template guide]: https://jinja.palletsprojects.com/en/stable/templates/
[online documentation]: https://fmf-jinja.readthedocs.io/
[rtd-badge]: https://readthedocs.org/projects/fmf-jinja/badge/?version=latest
[rtd-link]: https://fmf-jinja.readthedocs.io/en/latest/?badge=latest
[`example/minimal`]: example/minimal
