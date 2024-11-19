# Fmf metadata

## Basics

If you are new to fmf files, these are basically [yaml] files with a file-structure
hierarchy. I.e. a fmf file like:
```{code-block} yaml
:name: basics/main.fmf
:caption: /main.fmf
:emphasize-lines: 4,5

var1: 42
var2: Default value

/rootA:
/rootB:
  var2: Overwritten
```
is interpreted as if you had 2 fmf/yaml files
```{code-block} yaml
:caption: /rootA/main.fmf

var1: 42
var2: Default value
```
```{code-block} yaml
:caption: /rootB/main.fmf
:emphasize-lines: 2

var1: 42
var2: Overwritten
```
Notice how the keys starting with `/` are treated as paths describing the tree
structure of the fmf tree as if it was a file structure, and how the variables are
inherited and overwritten.

:::{caution}
Crucially for a fmf tree to be valid, you have to define where the root of the tree is
located. This is done by adding a `.fmf/version` text file (with the content `1`) at
the root directory of the fmf tree. If there are any other `.fmf/version` somewhere in
the subdirectory hierarchy, the current tree branch will terminate there and a new tree
starts.
:::

## In the `fmf-jinja` context

From the fmf tree format we are using two aspects:
1. The paths of the fmf tree nodes (only the final leaves) represent the paths of each
   output folders where the templated folder is generated.

   Use `fmf ls` to see the tree structure.

2. The contents of the fmf tree nodes contain the instructions of how to generate the
   current output folder.

   Use `fmf show` to see the contents of the tree.

## Other useful features

The reason why fmf format is used for this project is its various [features]. Here are
some of the most common features that you should consider

### [Inheritance]

The fmf data is inherited from the top of the tree downwards as shown in the
[Basics example], greatly reducing the deduplication of variable and avoiding the need
of yaml-anchors.

If needed, the inheritance can be turned off by adding the following to the tree node's
data:
```yaml
/:
  inherit: false
```

:::{note}
In this case `/` is treated as a special path pointing to the current node where
containing the fmf directives of the current node. Here we are turning off the
inheritance.
:::

### [Merging]

By default, when a key is redefined further down the hierarchy, this key-value is
overwritten by the most recent value, as we saw in the [Basics example]. On top of that
fmf supports merging operations defined by appending an operator (`+`, `-`, `+<`, etc.)
to the key and performing an operation like [`dict.update()`]. For example the
following fmf file
```{code-block} yaml
:caption: /main.fmf
:emphasize-lines: 6-8

vars:
  var1: 42
  var2: Default value

/merged:
  vars+:
    var1+: 378
    var3: New one
```
evaluates to
```{code-block} yaml
:caption: /merged/main.fmf

vars:
  var1: 420
  var2: Default value
  var3: New one
```

:::{note}
The merging operations take into account the yaml type of the original value. For
example `+` operation can be `dict.update()`, `list.append()` or `str.__add__()`.
:::

### [Scatter]

Instead of defining one monolithic `main.fmf` file, you can instead redistribute the
fmf nodes into their equivalent fmf files in the file structure. Specifically, the
following fmf files are equivalent:


```{code-block} yaml
:caption: /main.fmf

/rootA:
  var1: 42
  var2: Default value
```
```{code-block} yaml
:caption: /rootA.fmf

var1: 42
var2: Default value
```
```{code-block} yaml
:caption: /rootA/main.fmf

var1: 42
var2: Default value
```

Note how `main.fmf` behaves like `index.html` on website or `.` in unix paths.

[yaml]: https://en.wikipedia.org/wiki/YAML
[features]: inv:fmf#features
[Inheritance]: inv:fmf:std:label#features:inheritance
[Merging]: inv:fmf:std:label#features:merging
[Scatter]: inv:fmf:std:label#features:scatter
[Basics example]: #basics/main.fmf
[`dict.update()`]: inv:python:py:method#dict.update
