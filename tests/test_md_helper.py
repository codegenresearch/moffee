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
    """Test if the function correctly identifies Markdown comments."""
    assert is_comment("<!-- This is a comment -->") is True
    assert is_comment("This is not a comment") is False


def test_is_empty():
    """Test if the function correctly identifies empty lines in Markdown."""
    assert is_empty("<!-- This is a comment -->") is True
    assert is_empty("This is not a comment") is False
    assert is_empty(" \n") is True


def test_get_header_level():
    """Test if the function correctly determines the header level of a given line."""
    assert get_header_level("# Header 1") == 1
    assert get_header_level("### Header 3") == 3
    assert get_header_level("Normal text") == 0
    assert get_header_level("####### Not a valid header") == 0


def test_is_divider():
    """Test if the function correctly identifies Markdown dividers."""
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
    assert is_divider("  ===  ", type="=") is True
    assert is_divider("  <->  ") is True
    assert is_divider("<->", type="<") is True
    assert is_divider("<->", type="=") is False


def test_contains_image():
    """Test if the function correctly identifies lines containing Markdown images."""
    assert contains_image("![Alt text](image.jpg)") is True
    assert contains_image("This is an image: ![Alt text](image.jpg)") is True
    assert contains_image("This is not an image") is False
    assert contains_image("![](image.jpg)") is True  # empty alt text
    assert contains_image("![]()") is True  # empty alt text and URL


def test_contains_deco():
    """Test if the function correctly identifies lines containing Markdown decorators."""
    assert contains_deco("@(layout=split, background=blue)") is True
    assert contains_deco("  @(layout=default)  ") is True
    assert contains_deco("This is not a deco") is False
    assert contains_deco("@(key=value) Some text") is False
    assert contains_deco("@()") is True  # empty deco


def test_extract_title():
    """Test if the function correctly extracts the title from a Markdown document."""
    assert extract_title("# Main Title\nSome content") == "Main Title"
    assert extract_title("## Secondary Title\nSome content") == "Secondary Title"
    assert extract_title("# Main Title\n## Secondary Title\nSome content") == "Main Title"
    assert extract_title("## Secondary Title\n# Main Title\nSome content") == "Secondary Title"
    assert extract_title("Some content without headings") is None
    assert extract_title("") is None
    assert extract_title("#  Title with spaces  \nContent") == "Title with spaces"
    multi_para = "Para 1\n\nPara 2\n\n# Actual Title\nContent"
    assert extract_title(multi_para) == "Actual Title"


def multi_strip(text):
    """Helper function to strip and remove empty lines from a text."""
    return "\n".join([t.strip() for t in text.split("\n") if t.strip() != ""])


def test_remove_html_comments():
    """Test if the function correctly removes HTML comments from Markdown."""
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
    """Test if the function correctly removes single-line comments from Markdown."""
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
    """Test if the function correctly removes all types of comments from Markdown."""
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
    """Test if the function correctly handles Markdown with no comments."""
    markdown = """
# Title
This is a normal Markdown
document with no comments.
"""
    assert multi_strip(rm_comments(markdown)) == multi_strip(markdown)