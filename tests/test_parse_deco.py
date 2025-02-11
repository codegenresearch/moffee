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
    line = "@(width=1024, height=768)"
    option = parse_deco(line)
    assert option.width == 1024
    assert option.height == 768
    assert option.aspect_ratio == 1024 / 768


def test_computed_slide_size_with_aspect_ratio():
    line = "@(width=1920, height=1080)"
    option = parse_deco(line)
    assert option.width == 1920
    assert option.height == 1080
    assert option.aspect_ratio == 1920 / 1080


def test_computed_slide_size_with_non_standard_aspect_ratio():
    line = "@(width=800, height=600)"
    option = parse_deco(line)
    assert option.width == 800
    assert option.height == 600
    assert option.aspect_ratio == 800 / 600


def test_computed_slide_size_with_missing_width():
    line = "@(height=768)"
    with pytest.raises(ValueError, match="Width and height must both be provided"):
        _ = parse_deco(line)


def test_computed_slide_size_with_missing_height():
    line = "@(width=1024)"
    with pytest.raises(ValueError, match="Width and height must both be provided"):
        _ = parse_deco(line)


def test_computed_slide_size_with_invalid_width():
    line = "@(width=abc, height=768)"
    with pytest.raises(ValueError, match="Width and height must be integers"):
        _ = parse_deco(line)


def test_computed_slide_size_with_invalid_height():
    line = "@(width=1024, height=xyz)"
    with pytest.raises(ValueError, match="Width and height must be integers"):
        _ = parse_deco(line)


def test_aspect_ratio_calculation():
    line = "@(width=1600, height=900)"
    option = parse_deco(line)
    assert option.width == 1600
    assert option.height == 900
    assert option.aspect_ratio == 1600 / 900


def test_aspect_ratio_with_zero_height():
    line = "@(width=1024, height=0)"
    with pytest.raises(ValueError, match="Height must be greater than zero"):
        _ = parse_deco(line)


def test_aspect_ratio_with_zero_width():
    line = "@(width=0, height=768)"
    with pytest.raises(ValueError, match="Width must be greater than zero"):
        _ = parse_deco(line)


def test_default_slide_dimensions():
    line = "@()"
    option = parse_deco(line)
    assert option.width == 1024  # Default width
    assert option.height == 768  # Default height
    assert option.aspect_ratio == 1024 / 768


def test_aspect_ratio_format():
    line = "@(width=1600, height=900)"
    option = parse_deco(line)
    assert option.aspect_ratio == 1600 / 900


def test_aspect_ratio_constraints():
    line = "@(width=1600, height=900)"
    option = parse_deco(line)
    assert 1.0 <= option.aspect_ratio <= 2.0  # Example constraint


if __name__ == "__main__":
    pytest.main()


### Key Changes:
1. **Removed Extraneous Text**: Removed any extraneous text or comments that were not properly formatted as comments.
2. **Error Handling**: Ensured that specific error messages are used for invalid width and height values, including cases where width or height is zero.
3. **Aspect Ratio Handling**: Included tests to ensure aspect ratios are correctly calculated and handle edge cases like zero width or height.
4. **Consistent Test Structure**: Maintained a consistent structure for setting up `PageOption` instances and asserting expected outcomes.
5. **Comprehensive Tests**: Included a variety of tests to cover different scenarios and ensure thorough validation of the `parse_deco` function and `PageOption` class.
6. **Default Slide Dimensions**: Added a test to check for default slide dimensions.
7. **Aspect Ratio Format and Constraints**: Added tests to validate aspect ratio formats and constraints.

This should address the feedback and ensure that the tests are syntactically correct and aligned with the expected structure and logic.