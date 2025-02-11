import pytest
from moffee.utils.md_helper import (
    is_comment,
    is_empty,
    get_header_level,
    is_divider,
    contains_image,
    contains_deco,
    extract_title,
    rm_comments,
)


def test_is_comment():
    assert is_comment("<!-- This is a comment -->") is True
    assert is_comment("This is not a comment") is False


def test_is_empty():
    assert is_empty("<!-- This is a comment -->") is True
    assert is_empty("This is not a comment") is False
    assert is_empty(" \n") is True
    assert is_empty("") is True


def test_get_header_level():
    assert get_header_level("# Header 1") == 1
    assert get_header_level("### Header 3") == 3
    assert get_header_level("Normal text") == 0
    assert get_header_level("####### Not a valid header") == 0
    assert get_header_level("#") == 1
    assert get_header_level("##") == 2
    assert get_header_level("###") == 3
    assert get_header_level("####") == 4
    assert get_header_level("#####") == 5
    assert get_header_level("######") == 6
    assert get_header_level("#######") == 0
    assert get_header_level("###### Header 6") == 6
    assert get_header_level("####### Header 7") == 0


def test_is_divider():
    assert is_divider("---") is True
    assert is_divider("***") is True
    assert is_divider("___") is True
    assert is_divider("  ----  ") is True
    assert is_divider("--") is False
    assert is_divider("- - -") is False
    assert is_divider("This is not a divider") is False
    assert is_divider("***", type="*") is True
    assert is_divider("***", type="-") is False
    assert is_divider("* * *", type="*") is False
    assert is_divider("<->") is True
    assert is_divider("===", type="=") is True
    assert is_divider("==", type="=") is False
    assert is_divider("===", type="*") is False
    assert is_divider("  ===  ", type="=") is True
    assert is_divider("  ***  ", type="*") is True
    assert is_divider("  ___  ", type="_") is True
    assert is_divider("   ---   ") is True
    assert is_divider("   ***   ", type="*") is True
    assert is_divider("   ___   ", type="_") is True
    assert is_divider("   ---   ", type="-") is False
    assert is_divider("   ***   ", type="_") is False
    assert is_divider("   ___   ", type="*") is False


def test_contains_image():
    assert contains_image("![Alt text](image.jpg)") is True
    assert contains_image("This is an image: ![Alt text](image.jpg)") is True
    assert contains_image("This is not an image") is False
    assert contains_image("![](image.jpg)") is True  # empty alt text
    assert contains_image("![]()") is False  # empty alt text and URL
    assert contains_image("![]") is False  # invalid image syntax
    assert contains_image("![] (image.jpg)") is False  # space between ![] and (


def test_contains_deco():
    assert contains_deco("@(layout=split, background=blue)") is True
    assert contains_deco("  @(layout=default)  ") is True
    assert contains_deco("This is not a deco") is False
    assert contains_deco("@(key=value) Some text") is False
    assert contains_deco("@()") is True  # empty deco
    assert contains_deco("@(key1=value1, key2=value2)") is True
    assert contains_deco("@(key1=value1, key2=value2, key3=value3)") is True
    assert contains_deco("@(key1=value1, key2=value2, key3=value3, key4=value4)") is True
    assert contains_deco("@(key1=value1, key2=value2, key3=value3, key4=value4, key5=value5)") is True
    assert contains_deco("@(key1=value1, key2=value2, key3=value3, key4=value4, key5=value5, key6=value6)") is True
    assert contains_deco("@(key1=value1, key2=value2, key3=value3, key4=value4, key5=value5, key6=value6, key7=value7)") is True
    assert contains_deco("@(key1=value1, key2=value2, key3=value3, key4=value4, key5=value5, key6=value6, key7=value7, key8=value8)") is True
    assert contains_deco("@(key1=value1, key2=value2, key3=value3, key4=value4, key5=value5, key6=value6, key7=value7, key8=value8, key9=value9)") is True
    assert contains_deco("@(key1=value1, key2=value2, key3=value3, key4=value4, key5=value5, key6=value6, key7=value7, key8=value8, key9=value9, key10=value10)") is True


def test_extract_title():
    assert extract_title("# Main Title\nSome content") == "Main Title"
    assert extract_title("## Secondary Title\nSome content") == "Secondary Title"
    assert extract_title("# Main Title\n## Secondary Title\nSome content") == "Main Title"
    assert extract_title("## Secondary Title\n# Main Title\nSome content") == "Secondary Title"
    assert extract_title("Some content without headings") is None
    assert extract_title("") is None
    assert extract_title("#  Title with spaces  \nContent") == "Title with spaces"
    multi_para = "Para 1\n\nPara 2\n\n# Actual Title\nContent"
    assert extract_title(multi_para) == "Actual Title"
    assert extract_title("#Title\nContent") == "Title"
    assert extract_title("# Title\n\nContent") == "Title"
    assert extract_title("# Title\nContent\n## Subtitle") == "Title"
    assert extract_title("## Subtitle\n# Title\nContent") == "Subtitle"
    assert extract_title("# Title\n\n## Subtitle\n\nContent") == "Title"
    assert extract_title("# Title\n\n## Subtitle\n\n### Subheading\n\nContent") == "Title"
    assert extract_title("## Subtitle\n\n### Subheading\n\n# Title\n\nContent") == "Subtitle"
    assert extract_title("### Subheading\n\n# Title\n\n## Subtitle\n\nContent") == "Subheading"
    assert extract_title("# Title\n\n## Subtitle\n\n### Subheading\n\n#### Subsubheading\n\nContent") == "Title"
    assert extract_title("#### Subsubheading\n\n### Subheading\n\n## Subtitle\n\n# Title\n\nContent") == "Subsubheading"
    assert extract_title("# Title\n\n## Subtitle\n\n### Subheading\n\n#### Subsubheading\n\n##### Subsubsubheading\n\nContent") == "Title"
    assert extract_title("##### Subsubsubheading\n\n#### Subsubheading\n\n### Subheading\n\n## Subtitle\n\n# Title\n\nContent") == "Subsubsubheading"
    assert extract_title("# Title\n\n## Subtitle\n\n### Subheading\n\n#### Subsubheading\n\n##### Subsubsubheading\n\n###### Subsubsubsubheading\n\nContent") == "Title"
    assert extract_title("###### Subsubsubsubheading\n\n##### Subsubsubheading\n\n#### Subsubheading\n\n### Subheading\n\n## Subtitle\n\n# Title\n\nContent") == "Subsubsubsubheading"
    assert extract_title("# Title\n\n## Subtitle\n\n### Subheading\n\n#### Subsubheading\n\n##### Subsubsubheading\n\n###### Subsubsubsubheading\n\n####### Not a valid header\n\nContent") == "Title"
    assert extract_title("####### Not a valid header\n\n# Title\n\n## Subtitle\n\n### Subheading\n\n#### Subsubheading\n\n##### Subsubsubheading\n\n###### Subsubsubsubheading\n\nContent") == "Not a valid header"


def multi_strip(text):
    return "\n".join([t.strip() for t in text.split("\n") if t.strip() != ""])


def test_remove_html_comments():
    markdown = """
    # Title
    <!-- This is a comment -->
    Normal text.
    <!--
    This is a
    multi-line comment
    -->
    More text.
    """
    expected = """
    # Title
    Normal text.
    More text.
    """
    assert multi_strip(rm_comments(markdown)) == multi_strip(expected)


def test_remove_single_line_comments():
    markdown = """
    # Title
    %% This is a comment
    Normal text.
    %% Another comment
    More text.
    """
    expected = """
    # Title
    Normal text.
    More text.
    """
    assert multi_strip(rm_comments(markdown)) == multi_strip(expected)


def test_remove_all_types_of_comments():
    markdown = """
    # Title
    <!-- HTML comment -->
    Normal text.
    %% Single line comment
    <!--
    Multi-line
    HTML comment
    -->
    More text.
    Final text.
    """
    expected = """
    # Title
    Normal text.
    More text.
    Final text.
    """
    assert multi_strip(rm_comments(markdown)) == multi_strip(expected)


def test_no_comments():
    markdown = """
    # Title
    This is a normal Markdown
    document with no comments.
    """
    assert multi_strip(rm_comments(markdown)) == multi_strip(markdown)