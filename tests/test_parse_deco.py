import pytest
from moffee.compositor import parse_deco, PageOption


def test_basic_deco():
    line = "@(layout=split, background=blue)"
    option = parse_deco(line)
    assert option.layout == "split"
    assert option.styles == {"background": "blue"}
    assert option.aspect_ratio is None
    assert option.slide_dimensions is None


def test_empty_deco():
    line = "@()"
    option = parse_deco(line)
    assert option == PageOption(aspect_ratio=None, slide_dimensions=None)


def test_invalid_deco():
    line = "This is not a deco"
    with pytest.raises(ValueError):
        _ = parse_deco(line)


def test_deco_with_base_option():
    line = "@(layout=split, default_h1=true, custom_key=value)"
    base_option = PageOption(
        layout="content", default_h1=False, default_h2=True, default_h3=True,
        aspect_ratio="16:9", slide_dimensions=(1920, 1080)
    )
    updated_option = parse_deco(line, base_option)

    assert updated_option.styles == {"custom_key": "value"}
    assert updated_option.layout == "split"
    assert updated_option.default_h1 is True
    assert updated_option.default_h2 is True
    assert updated_option.default_h3 is True
    assert updated_option.aspect_ratio == "16:9"
    assert updated_option.slide_dimensions == (1920, 1080)


def test_deco_with_type_conversion():
    line = "@(default_h1=true, default_h2=false, layout=centered, custom_int=42, custom_float=3.14)"
    base_option = PageOption(aspect_ratio="4:3", slide_dimensions=(1280, 960))
    updated_option = parse_deco(line, base_option)

    assert updated_option.styles == {"custom_int": 42, "custom_float": 3.14}
    assert updated_option.default_h1 is True
    assert updated_option.default_h2 is False
    assert updated_option.layout == "centered"
    assert updated_option.aspect_ratio == "4:3"
    assert updated_option.slide_dimensions == (1280, 960)


def test_deco_with_spaces():
    line = "@(  layout = split,   background = blue  )"
    option = parse_deco(line)
    assert option.layout == "split"
    assert option.styles == {"background": "blue"}
    assert option.aspect_ratio is None
    assert option.slide_dimensions is None


def test_deco_with_quotes():
    line = "@(layout = \"split\",length='34px')"
    option = parse_deco(line)
    assert option.layout == "split"
    assert option.styles == {"length": "34px"}
    assert option.aspect_ratio is None
    assert option.slide_dimensions is None


def test_deco_with_hyphen():
    line = "@(background-color='red')"
    option = parse_deco(line)
    assert option.styles == {"background-color": "red"}
    assert option.aspect_ratio is None
    assert option.slide_dimensions is None


if __name__ == "__main__":
    pytest.main()