import pytest

from moffee.compositor import parse_deco, PageOption


def test_basic_deco():
    line = "@(layout=split, background=blue, width=800, height=600)"
    option = parse_deco(line)
    assert option.layout == "split"
    assert option.styles == {"background": "blue", "width": "800", "height": "600"}


def test_empty_deco():
    line = "@()"
    option = parse_deco(line)
    assert option == PageOption()


def test_invalid_deco():
    line = "This is not a deco"
    with pytest.raises(ValueError) as excinfo:
        _ = parse_deco(line)
    assert str(excinfo.value) == "Invalid deco format"


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
    assert option.styles == {"width": "1024", "height": "768"}
    assert option.aspect_ratio == 1024 / 768


if __name__ == "__main__":
    pytest.main()


### Key Changes:
1. **Simplified Assertions**: Focused on essential properties in each test.
2. **Default Values**: Used `PageOption()` without parameters in `test_empty_deco`.
3. **Removed Unused Properties**: Ensured only relevant properties are asserted.
4. **Consistent Input Strings**: Simplified input strings where possible.
5. **Additional Test Case**: Added `test_computed_slide_size` to cover computed properties.
6. **Formatting and Spacing**: Improved consistency in formatting.
7. **Error Handling**: Added a specific error message in `test_invalid_deco`.