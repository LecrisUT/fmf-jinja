# tmt tests

`.fmf` files are primarily used as [tmt] test files. Currently, tmt does not integrate
with this project, but here are some workflows that can be generated from this.

## Matrix plans

Consider the case of running a matrix of tests in various python environments and
running different sets of tests. Using the [recursive feature] we can design this as
follows:
```{code-block} jinja
:caption: /template_tmt/main.fmf.j2

prepare:
  - how: shell
    script: |
      source venv/bin/activate
      pip install -e .
execute:
  how: tmt
{% for p_ver in python_versions %}
/python_{{ p_ver }}:
  prepare+<:
    - how: install
      package: python-{{ p_ver }}
    - how: shell
      script: |
        python{{ p_ver }} -m venv venv
{% for tier in tier_filters %}
/python_{{ p_ver }}/tier_{{ tier }}:
  discover:
    how: fmf
    filter: 'tier: {{ tier }}'
{% endfor %}
{% endfor %}
```
```{code-block} yaml
:caption: /main.fmf

templates: /template_tmt
vars:
  python_versions: [ "3.9", "3.13" ]
  tier_filters: [ 0, 1 ]
```

This produces the tmt tree:
```console
$ fmf-jinja generate -o output --no-recursive
$ tmt -r output plans ls
/python_3.13/tier_0
/python_3.13/tier_1
/python_3.9/tier_0
/python_3.9/tier_1
$ tmt -r output plans show /python_3.9/tier_0
/python_3.9/tier_0
    discover
         how fmf
      filter tier: 0
     prepare
         how install
     package python-3.9
     prepare
         how shell
      script python3.9 -m venv venv
     prepare
         how shell
      script source venv/bin/activate
             pip install -e .
     enabled true
```

[tmt]: inv:tmt#index
[recursive feature]: ../usage/advanced.md#recursive
