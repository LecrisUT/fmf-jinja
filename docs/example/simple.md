# Simple

The more recommended design is to explicitly specify the Jinja variables with
{term}`vars` and template folder with {term}`templates` keys. This allows to use all
other keys in the [Template schema].

The example in {path}`example/simple` contains a simple template with all supported
functionalities. The fmf tree is defined by:
```{literalinclude} ../../example/simple/main.fmf
:language: yaml
:caption: /main.fmf
:emphasize-lines: 8-16
```
This is identical to the [minimal] example, with additional keys used in `/rootA`. The
changes in `/rootA` are:
- create a symbolic link to a generated file in `/rootB`
- copy/rename `common_file.txt` to `renamed_file.txt`
- exclude `common_file.txt` from being copied

Running `fmf-jinja` on this example we get:
```{code-block} console
:emphasize-lines: 8,10

$ fmf-jinja -r example/simple generate -o output
$ tree output
output/
├── .fmf
│   └── version
├── main.fmf
├── rootA
│   ├── fileB.yaml -> ../rootB/file.yaml
│   ├── file.yaml
│   └── renamed_file.txt
└── rootB
    ├── common_file.txt
    └── file.yaml
```

[Template schema]: ../usage/index.md#template-schema
[minimal]: minimal.md
