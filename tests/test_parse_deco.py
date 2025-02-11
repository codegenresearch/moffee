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
    page_option1 = PageOption(width=1024, height=768)
    assert page_option1.styles == {"width": "1024", "height": "768"}
    assert page_option1.computed_slide_size == (1024, 768)

    page_option2 = PageOption(width=800, height=600)
    assert page_option2.styles == {"width": "800", "height": "600"}
    assert page_option2.computed_slide_size == (800, 600)

    page_option3 = PageOption(width=1280, height=720)
    assert page_option3.styles == {"width": "1280", "height": "720"}
    assert page_option3.computed_slide_size == (1280, 720)

    page_option4 = PageOption(width=1920, height=1080)
    assert page_option4.styles == {"width": "1920", "height": "1080"}
    assert page_option4.computed_slide_size == (1920, 1080)

    page_option5 = PageOption(width=1600, height=900)
    assert page_option5.styles == {"width": "1600", "height": "900"}
    assert page_option5.computed_slide_size == (1600, 900)


def test_aspect_ratio_handling():
    page_option = PageOption(width=1600, height=900)
    assert page_option.aspect_ratio == 1600 / 900

    with pytest.raises(ValueError, match="Width and height must be positive numbers"):
        _ = PageOption(width=0, height=900)

    with pytest.raises(ValueError, match="Width and height must be positive numbers"):
        _ = PageOption(width=1600, height=0)


if __name__ == "__main__":
    pytest.main()


### Key Changes:
1. **Removed Unterminated String Literal**: Ensured there are no unterminated string literals in comments.
2. **Error Handling**: Used the `match` parameter in `pytest.raises` to validate error messages.
3. **Computed Slide Size Tests**: Used `computed_slide_size` as a property to check the expected output.
4. **Consistency in Variable Naming**: Used `page_option` as a variable name in the computed slide size tests.
5. **Aspect Ratio Handling**: Included detailed tests for aspect ratio handling.
6. **Formatting and Spacing**: Ensured consistent formatting and spacing throughout the code.