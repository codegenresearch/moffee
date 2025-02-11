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
    line1 = "@(width=1024, height=768)"
    option1 = parse_deco(line1)
    assert option1.styles == {"width": "1024", "height": "768"}
    assert option1.aspect_ratio == 1024 / 768

    line2 = "@(width=800, height=600)"
    option2 = parse_deco(line2)
    assert option2.styles == {"width": "800", "height": "600"}
    assert option2.aspect_ratio == 800 / 600

    line3 = "@(width=1280, height=720)"
    option3 = parse_deco(line3)
    assert option3.styles == {"width": "1280", "height": "720"}
    assert option3.aspect_ratio == 1280 / 720

    line4 = "@(width=1920, height=1080)"
    option4 = parse_deco(line4)
    assert option4.styles == {"width": "1920", "height": "1080"}
    assert option4.aspect_ratio == 1920 / 1080

    line5 = "@(width=1600, height=900)"
    option5 = parse_deco(line5)
    assert option5.styles == {"width": "1600", "height": "900"}
    assert option5.aspect_ratio == 1600 / 900


if __name__ == "__main__":
    pytest.main()


### Key Changes:
1. **Removed Invalid Comment**: Ensured there are no invalid comments that could cause syntax errors.
2. **Computed Slide Size Tests**: Expanded `test_computed_slide_size` to include more scenarios with different `width`, `height`, and `aspect_ratio` values.
3. **Error Handling**: Included specific error messages in `test_invalid_deco` to provide more informative feedback.
4. **Consistency in Assertions**: Ensured assertions are consistent and match the expected structure.
5. **Use of PageOption**: Utilized `PageOption` in various contexts, including default values and computed properties.
6. **Formatting and Spacing**: Ensured consistent formatting and spacing throughout the code.