import pytest

from moffee.compositor import parse_deco, PageOption


def test_basic_deco():
    line = "@( layout=split, background=blue )"
    option = parse_deco(line)
    assert option.layout == "split"
    assert option.styles == {"background": "blue"}


def test_empty_deco():
    line = "@()"
    option = parse_deco(line)
    assert option == PageOption()


def test_invalid_deco():
    line = "This is not a deco"
    with pytest.raises(ValueError, match="Invalid deco format"):
        _ = parse_deco(line)


def test_deco_with_base_option():
    line = "@( layout=split, default_h1=true, custom_key=value )"
    base_option = PageOption(
        layout="content", default_h1=False, default_h2=True, default_h3=True
    )
    updated_option = parse_deco(line, base_option)

    assert updated_option.styles == {"custom_key": "value"}
    assert updated_option.layout == "split"
    assert updated_option.default_h1 is True
    assert updated_option.default_h2 is True
    assert updated_option.default_h3 is True


def test_deco_with_type_conversion():
    line = "@( default_h1=true, default_h2=false, layout=centered, custom_int=42, custom_float=3.14 )"
    base_option = PageOption()
    updated_option = parse_deco(line, base_option)

    assert updated_option.styles == {"custom_int": 42, "custom_float": 3.14}
    assert updated_option.default_h1 is True
    assert updated_option.default_h2 is False
    assert updated_option.layout == "centered"


def test_deco_with_spaces():
    line = "@( layout=split, background=blue )"
    option = parse_deco(line)
    assert option.layout == "split"
    assert option.styles == {"background": "blue"}


def test_deco_with_quotes():
    line = "@( layout=\"split\", length='34px' )"
    option = parse_deco(line)
    assert option.layout == "split"
    assert option.styles == {"length": "34px"}


def test_deco_with_hyphen():
    line = "@( background-color='red' )"
    option = parse_deco(line)
    assert option.styles == {"background-color": "red"}


def test_computed_slide_size():
    line = "@( width=800, height=600 )"
    option = parse_deco(line)
    assert option.width == 800
    assert option.height == 600
    assert option.aspect_ratio == 800 / 600


def test_computed_slide_size_no_height():
    line = "@( width=800 )"
    option = parse_deco(line)
    assert option.width == 800
    assert option.height is None
    assert option.aspect_ratio is None


def test_computed_slide_size_no_width():
    line = "@( height=600 )"
    option = parse_deco(line)
    assert option.width is None
    assert option.height == 600
    assert option.aspect_ratio is None


def test_computed_slide_size_default_aspect_ratio():
    line = "@( width=800, height=600 )"
    option = parse_deco(line)
    assert option.width == 800
    assert option.height == 600
    assert option.aspect_ratio == 800 / 600


def test_computed_slide_size_with_aspect_ratio_override():
    line = "@( width=800, height=600, aspect_ratio=1.5 )"
    option = parse_deco(line)
    assert option.width == 800
    assert option.height == 600
    assert option.aspect_ratio == 1.5


def test_computed_slide_size_with_only_aspect_ratio():
    line = "@( aspect_ratio=1.78 )"
    option = parse_deco(line)
    assert option.width is None
    assert option.height is None
    assert option.aspect_ratio == 1.78


def test_aspect_ratio_consistency():
    line = "@( width=1920, height=1080 )"
    option = parse_deco(line)
    assert option.aspect_ratio == 1920 / 1080

    line = "@( width=1280, height=720 )"
    option = parse_deco(line)
    assert option.aspect_ratio == 1280 / 720


if __name__ == "__main__":
    pytest.main()