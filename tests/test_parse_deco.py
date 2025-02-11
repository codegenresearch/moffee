import pytest
from moffee.compositor import parse_deco, PageOption


def test_basic_deco():
    line = "@(layout=split, background=blue, width=1024, height=768)"
    option = parse_deco(line)
    assert option.layout == "split"
    assert option.styles == {"background": "blue"}
    assert option.width == 1024
    assert option.height == 768
    assert option.aspect_ratio == 1024 / 768


def test_empty_deco():
    line = "@()"
    option = parse_deco(line)
    assert option == PageOption(width=1024, height=768, aspect_ratio=1024 / 768)


def test_invalid_deco():
    line = "This is not a deco"
    with pytest.raises(ValueError):
        _ = parse_deco(line)


def test_deco_with_base_option():
    line = "@(layout=split, default_h1=true, custom_key=value, width=1280, height=800)"
    base_option = PageOption(
        layout="content", default_h1=False, default_h2=True, default_h3=True, width=1024, height=768
    )
    updated_option = parse_deco(line, base_option)

    assert updated_option.styles == {"custom_key": "value"}
    assert updated_option.layout == "split"
    assert updated_option.default_h1 is True
    assert updated_option.default_h2 is True
    assert updated_option.default_h3 is True
    assert updated_option.width == 1280
    assert updated_option.height == 800
    assert updated_option.aspect_ratio == 1280 / 800


def test_deco_with_type_conversion():
    line = "@(default_h1=true, default_h2=false, layout=centered, custom_int=42, custom_float=3.14, width=800, height=600)"
    base_option = PageOption()
    updated_option = parse_deco(line, base_option)

    assert updated_option.styles == {"custom_int": 42, "custom_float": 3.14}
    assert updated_option.default_h1 is True
    assert updated_option.default_h2 is False
    assert updated_option.layout == "centered"
    assert updated_option.width == 800
    assert updated_option.height == 600
    assert updated_option.aspect_ratio == 800 / 600


def test_deco_with_spaces():
    line = "@(  layout = split,   background = blue, width = 1024, height = 768  )"
    option = parse_deco(line)
    assert option.layout == "split"
    assert option.styles == {"background": "blue"}
    assert option.width == 1024
    assert option.height == 768
    assert option.aspect_ratio == 1024 / 768


def test_deco_with_quotes():
    line = "@(layout = \"split\",length='34px', width='1024px', height='768px')"
    option = parse_deco(line)
    assert option.layout == "split"
    assert option.styles == {"length": "34px"}
    assert option.width == 1024
    assert option.height == 768
    assert option.aspect_ratio == 1024 / 768


def test_deco_with_hyphen():
    line = "@(background-color='red', width=1024, height=768)"
    option = parse_deco(line)
    assert option.styles == {"background-color": "red"}
    assert option.width == 1024
    assert option.height == 768
    assert option.aspect_ratio == 1024 / 768


def test_validate_aspect_ratio():
    line = "@(width=1024, height=768)"
    option = parse_deco(line)
    assert option.aspect_ratio == 1024 / 768

    line = "@(width=800, height=600)"
    option = parse_deco(line)
    assert option.aspect_ratio == 800 / 600


if __name__ == "__main__":
    pytest.main()