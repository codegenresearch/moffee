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
    with pytest.raises(ValueError, match="Invalid deco format"):
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
    line = "@(aspect_ratio='16:9')"
    option = parse_deco(line)
    assert option.aspect_ratio == "16:9"
    assert option.slide_dimensions == (1920, 1080)

    line = "@(aspect_ratio='4:3')"
    option = parse_deco(line)
    assert option.aspect_ratio == "4:3"
    assert option.slide_dimensions == (1280, 960)

    line = "@(aspect_ratio='16:10')"
    option = parse_deco(line)
    assert option.aspect_ratio == "16:10"
    assert option.slide_dimensions == (1920, 1200)

    line = "@(aspect_ratio='1:1')"
    option = parse_deco(line)
    assert option.aspect_ratio == "1:1"
    assert option.slide_dimensions == (1080, 1080)

    line = "@(slide_width=1920, slide_height=1080)"
    option = parse_deco(line)
    assert option.slide_dimensions == (1920, 1080)

    line = "@(slide_width=1280, slide_height=960)"
    option = parse_deco(line)
    assert option.slide_dimensions == (1280, 960)

    line = "@(slide_width=1920, slide_height=1200)"
    option = parse_deco(line)
    assert option.slide_dimensions == (1920, 1200)

    line = "@(slide_width=1080, slide_height=1080)"
    option = parse_deco(line)
    assert option.slide_dimensions == (1080, 1080)


if __name__ == "__main__":
    pytest.main()


### Key Changes:
1. **Error Message in `test_invalid_deco`**: Updated the error message to match the expected "Invalid deco format".
2. **Computed Slide Size Tests**: Added more test cases to cover various scenarios involving `slide_width`, `slide_height`, and `aspect_ratio`.
3. **Base Option Initialization**: Ensured that `base_option` includes all relevant attributes like `default_h2` and `default_h3` to match the gold code.