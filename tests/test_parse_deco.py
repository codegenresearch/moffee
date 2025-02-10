import pytest
from moffee.compositor import parse_deco, PageOption


def test_basic_deco():
    line = "@(layout=split, background=blue)"
    option = parse_deco(line)
    assert option.layout == "split"
    assert option.styles == {"background": "blue"}


def test_empty_deco():
    line = "@()"
    option = parse_deco(line)
    assert option == PageOption()


def test_invalid_deco():
    line = "This is not a deco"
    with pytest.raises(ValueError):
        _ = parse_deco(line)


def test_deco_with_base_option():
    line = "@(layout=split, default_h1=true, custom_key=value)"
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
    line = "@(default_h1=true, default_h2=false, layout=centered, custom_int=42, custom_float=3.14)"
    base_option = PageOption()
    updated_option = parse_deco(line, base_option)

    assert updated_option.styles == {"custom_int": 42, "custom_float": 3.14}
    assert updated_option.default_h1 is True
    assert updated_option.default_h2 is False
    assert updated_option.layout == "centered"


def test_deco_with_spaces():
    line = "@(  layout = split,   background = blue  )"
    option = parse_deco(line)
    assert option.layout == "split"
    assert option.styles == {"background": "blue"}


def test_deco_with_quotes():
    line = "@(layout = \"split\",length='34px')"
    option = parse_deco(line)
    assert option.layout == "split"
    assert option.styles == {"length": "34px"}


def test_deco_with_hyphen():
    line = "@(background-color='red')"
    option = parse_deco(line)
    assert option.styles == {"background-color": "red"}


def test_computed_slide_size():
    # Test width and height
    line = "@(width=1920, height=1080)"
    page_option = parse_deco(line)
    assert page_option.width == 1920
    assert page_option.height == 1080
    assert page_option.aspect_ratio == 1920 / 1080

    # Test width and aspect ratio
    line = "@(width=1920, aspect_ratio=1.7777777777777777)"
    page_option = parse_deco(line)
    assert page_option.width == 1920
    assert page_option.height == 1080
    assert page_option.aspect_ratio == 1920 / 1080

    # Test height and aspect ratio
    line = "@(height=1080, aspect_ratio=1.7777777777777777)"
    page_option = parse_deco(line)
    assert page_option.width == 1920
    assert page_option.height == 1080
    assert page_option.aspect_ratio == 1920 / 1080

    # Test simultaneous width, height, and aspect ratio
    line = "@(width=1920, height=1080, aspect_ratio=1.7777777777777777)"
    page_option = parse_deco(line)
    assert page_option.width == 1920
    assert page_option.height == 1080
    assert page_option.aspect_ratio == 1920 / 1080

    # Test invalid simultaneous width, height, and aspect ratio
    invalid_line = "@(width=1920, height=1080, aspect_ratio=1.77)"
    with pytest.raises(ValueError, match="Aspect ratio does not match width and height"):
        _ = parse_deco(invalid_line)


def test_validate_aspect_ratio():
    # Test valid aspect ratio
    line = "@(width=1920, height=1080)"
    page_option = parse_deco(line)
    assert page_option.aspect_ratio == 1920 / 1080

    # Test invalid height
    invalid_line = "@(width=1920, height=0)"
    with pytest.raises(ValueError, match="Height cannot be zero"):
        _ = parse_deco(invalid_line)


def test_invalid_aspect_ratio():
    # Test aspect ratio as string
    invalid_line = "@(width=1920, aspect_ratio='16:9')"
    with pytest.raises(ValueError, match="Aspect ratio must be a float"):
        _ = parse_deco(invalid_line)

    invalid_line = "@(height=1080, aspect_ratio='16:9')"
    with pytest.raises(ValueError, match="Aspect ratio must be a float"):
        _ = parse_deco(invalid_line)


def test_aspect_ratio_from_width_height():
    # Test aspect ratio calculation from width and height
    line = "@(width=1920, height=1080)"
    page_option = parse_deco(line)
    assert page_option.aspect_ratio == 1920 / 1080

    line = "@(width=1280, height=720)"
    page_option = parse_deco(line)
    assert page_option.aspect_ratio == 1280 / 720


if __name__ == "__main__":
    pytest.main()