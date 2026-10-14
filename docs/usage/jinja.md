<!--
SPDX-FileCopyrightText: 2026 Cristian Le

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Jinja templates

Jinja is a standard templating engine, and we cannot adequately cover its basics here.
Refer to Jinja's [Template Designer Guide] instead.

## In the `fmf-jinja` context

The jinja files are handled as follows:

1. Files ending with a `.j2` extensions are treated as jinja template files with the
   generated file having the same path and filename except for the final `.j2`
   extension that is stripped.
1. The variables used in the jinja template are determined by the {confval}`vars` variable
   of the current fmf node.
1. `{{ }}` syntax in the path files are **not** expanded. Use the [recursive feature]
   instead.

## Additional jinja extensions

Currently `fmf-jinja` does not provide additional filters and functions, but some are
being planned.

## Extending jinja environment

Currently, there is no mechanism to extend the {py:class}`jinja2.Environment` used.

[recursive feature]: advanced.md#recursive
[template designer guide]: inv:jinja#templates
