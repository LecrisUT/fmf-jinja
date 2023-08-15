# FMF-Jinja

[![Documentation Status](https://readthedocs.org/projects/fmf-jinja/badge/?version=latest)](https://fmf-jinja.readthedocs.io/en/latest/?badge=latest)
[![CI](https://github.com/LecrisUT/fmf-jinja/actions/workflows/ci.yaml/badge.svg)](https://github.com/LecrisUT/fmf-jinja/actions/workflows/ci.yaml)
[![codecov](https://codecov.io/github/LecrisUT/fmf-jinja/graph/badge.svg?token=WCTLWU6M2O)](https://codecov.io/github/LecrisUT/fmf-jinja)

<!-- SPHINX-START -->

Templating engine using [jinja files](https://jinja.palletsprojects.com) and
[fmf metadata](https://fmf.readthedocs.io).

## Concept

If you've found this project, chances are you already know about either
the FMF or Jinja project. But for the sake of redundancy:

[Jinja](https://jinja.palletsprojects.com) is a popular templating engine that
enables one to substitute text from JSON/YAML/Python like objects into a template
file/string.

[FMF](https://fmf.readthedocs.io) is an extension to YAML files that incorporates
a file structure format and inheritance of the dictionary variables from the parent
path to the children.

This project combines the two such that you can maintain your metadata in a folder
structure with minimal effort and generate any necessary data folder structure you
desire.

## Minimum example

See [`example/simple`](/example/simple) for a minimal example.
The output can then be generated using the python function `fmf_jinja.template.generate`
or using the cli interface `fmf-jinja`:

```console
$ fmf-jinja --root=example/simple generate --output=out
$ tree ./out
./out
├── rootA
│   ├── file.yaml
│   └── some_file.yaml
└── rootB
    ├── file.yaml
    └── some_file.yaml
$ cat ./out/rootA/template_file.yaml
my_var: A
```

<!-- SPHINX-END -->
