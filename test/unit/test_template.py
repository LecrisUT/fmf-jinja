import pytest

from fmf_jinja.template import TemplateContext


@pytest.mark.parametrize("fmf_tree", ["simple", "symlink"], indirect=True)
def test_generate(fmf_tree):
    ctx = TemplateContext(fmf_tree.tree)
    ctx.generate(fmf_tree.out_path.path)
    assert fmf_tree.out_path == fmf_tree.expected_path
