# Minimal

In the minimal example {term}`vars` is not defined and all keys in the fmf file are
used as Jinja variables. By default, the fmf root (`/`) is used as a template folder
unless {term}`templates` key is specified.

The example in {path}`example/minimal` contains a minimal template format for
`fmf-jinja`. Inside we have a fmf tree defined by:
```{literalinclude} ../../example/minimal/main.fmf
:language: yaml
:caption: /main.fmf
```
The template folder contains a file `common_file.txt` that is simply copied over and
a template file `file.yaml.j2` which generates a `file.yaml`.
```{literalinclude} ../../example/minimal/file.yaml.j2
:language: jinja
:caption: /file.yaml.j2
```

Running `fmf-jinja` on this example we get:
```console
$ fmf-jinja -r example/minimal generate -o output
$ tree -a output
output/
├── .fmf
│   └── version
├── main.fmf
├── rootA
│   ├── common_file.txt
│   └── file.yaml
└── rootB
    ├── common_file.txt
    └── file.yaml
$ tail output/root*/file.yaml
==> output/rootA/file.yaml <==
var0: random data
var1: 42
var2: Default value

==> output/rootB/file.yaml <==
var0: random data
var1: 42
var2: Overwritten
```
