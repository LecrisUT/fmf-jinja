# Usage

```{toctree}
:hidden: true

fmf
jinja
advanced
```

The simplest design shown on the [top page] and [minimal example] is to simply store
all Jinja variables in the fmf file and use the current directory as the templated
folder that will be generated.

For more complex structure see the following breakdown of supported variables

## Template schema

{.glossary}
`templates`
: *Default*: `"/"`

  *Type*: `Path | Template | list[Path | Template]`

  Define the template source(s) under the current node's output path. Can be either a
  list or a single item and the item(s) can be either strings or an object. If the item
  is a string it uses the default object with modified {term}`path <templates[].path>`
  variable.

`templates[].path`
: *Required*

  *Type*: `Path`

  Path to the template file or folder to generate under the current node's output.

  If the path is absolute, it is evaluated from the current fmf root directory,
  otherwise it is evaluated from the current node's fmf path.

  If the path points to a folder, the whole folder is processed recursively except for
  the items in {term}`exclude <templates[].exclude>`. The files are either rendered
  using Jinja if the file extension ends in `.j2` (stripping the final `.j2` extension
  in the output file), or otherwise copied over. Symbolic links are recreated,
  reinterpreting the target's absolute/relative path as described in the previous
  paragraph.

`templates[].exclude`
: *Default*: `[]`

  *Type*: `list[Path]`

  List of paths to exclude from being rendered or copied.

`vars`
: *Special*

  *Type*: `dict[str,Any]`

  Variables used in the Jinja template files.

  If the key is not specified, keys in the fmf object except for {term}`templates` are
  treated as the contents for `vars`.

`links`
: *Default*: `{}`

  *Type*: `dict[Path,Path]`

  Dictionary of symbolic links to generate, the key being path to the symbolic link
  created and the value being the path to the target. The absolute/relative paths are
  treated similarly to the {term}`path <templates[].path>` key.

`copy`
: *Default*: `{}`

  *Type*: `dict[Path,Path]`

  Dictionary of files/folders to copy, the key being the destination file/folder and
  the value being the original file/folder. The absolute/relative paths are treated
  similarly to the {term}`path <templates[].path>` key.

[top page]: ../index.md
[minimal example]: ../example/minimal.md
