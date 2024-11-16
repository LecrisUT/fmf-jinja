# Recursive

The example in {path}`example/recursive` showcases how `fmf-jinja` can run recursively
in order to support more complex template outputs. The initial template defines
```{literalinclude} ../../example/recursive/main.fmf
:language: yaml
:caption: /main.fmf
```
Which is used to generate a new fmf tree from
```{literalinclude} ../../example/recursive/template_fmf/main.fmf.j2
:language: jinja
:caption: /template_fmf/main.fmf
```
which overwrites the original `main.fmf` file.

The second run starts from the generated files:
```{literalinclude} ../../test/data/output/recursive/main.fmf
:language: yaml
:caption: /main.fmf
```
This overcomes a limitation in `fmf` that glob patterns are not supported that would
otherwise allow cleaner design of the fmf tree without requiring recursive runs.

Putting all together, running `fmf-jinja` on this example we get:
```console
$ fmf-jinja -r example/recusive generate -o output
$ tree output
output/
├── .fmf
│   └── version
├── A_2
│   ├── B_x
│   │   └── file.yaml
│   └── B_y
│       └── file.yaml
├── A_3
│   ├── B_x
│   │   └── file.yaml
│   └── B_y
│       └── file.yaml
└── main.fmf
```
