import pytest

from fmf_jinja.template import generate


@pytest.mark.parametrize("fmf_tree", ["simple", "symlink"], indirect=True)
def test_generate(fmf_tree):
    generate(fmf_tree.tree, fmf_tree.out_path.path)
    assert fmf_tree.out_path == fmf_tree.expected_path
