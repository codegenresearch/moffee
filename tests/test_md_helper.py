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


def test_get_header_level():
    assert get_header_level("# Header 1") == 1
    assert get_header_level("### Header 3") == 3
    assert get_header_level("Normal text") == 0
    assert get_header_level("####### Not a valid header") == 0


def test_is_divider():
    assert is_divider("---") is True, "Horizontal rule should be detected as a divider"
    assert is_divider("***") is True, "Asterisk rule should be detected as a divider"
    assert is_divider("___") is True, "Underscore rule should be detected as a divider"
    assert is_divider("  ----  ") is True, "Indented rule should be detected as a divider"
    assert is_divider("--") is False, "Short rule should not be detected as a divider"
    assert is_divider("- - -") is False, "Spaced rule should not be detected as a divider"
    assert is_divider("This is not a divider") is False, "Normal text should not be detected as a divider"
    assert is_divider("***", type="*") is True, "Specific asterisk rule should be detected as a divider"
    assert is_divider("***", type="-") is False, "Asterisk rule should not match hyphen type"
    assert is_divider("* * *", type="*") is False, "Spaced asterisk rule should not match asterisk type"


def test_contains_image():
    assert contains_image("![Alt text](image.jpg)") is True, "Image with alt text should be detected"
    assert contains_image("This is an image: ![Alt text](image.jpg)") is True, "Image within text should be detected"
    assert contains_image("This is not an image") is False, "Normal text should not be detected as an image"
    assert contains_image("![](image.jpg)") is True, "Image with empty alt text should be detected"
    assert contains_image("![]()") is False, "Empty image syntax should not be detected as an image"


def test_contains_deco():
    assert contains_deco("@(layout=split, background=blue)") is True, "Full deco should be detected"
    assert contains_deco("  @(layout=default)  ") is True, "Indented deco should be detected"
    assert contains_deco("This is not a deco") is False, "Normal text should not be detected as a deco"
    assert contains_deco("@(key=value) Some text") is False, "Deco followed by text should not be detected"
    assert contains_deco("@()") is True, "Empty deco should be detected"


def test_extract_title():
    assert extract_title("# Main Title\nSome content") == "Main Title", "Level 1 heading should be extracted as title"
    assert extract_title("## Secondary Title\nSome content") == "Secondary Title", "Level 2 heading should be extracted as title"
    assert extract_title("# Main Title\n## Secondary Title\nSome content") == "Main Title", "First level 1 heading should be extracted"
    assert extract_title("## Secondary Title\n# Main Title\nSome content") == "Secondary Title", "First heading should be extracted regardless of level"
    assert extract_title("Some content without headings") is None, "No headings should result in no title"
    assert extract_title("") is None, "Empty document should result in no title"
    assert extract_title("#  Title with spaces  \nContent") == "Title with spaces", "Leading/trailing spaces should be trimmed"
    multi_para = "Para 1\n\nPara 2\n\n# Actual Title\nContent"
    assert extract_title(multi_para) == "Actual Title", "Title should be extracted from the first heading after paragraphs"


def multi_strip(text):
    return "\n".join([t.strip() for t in text.split("\n") if t.strip() != ""])


def test_remove_html_comments():
    markdown = """\n    # Title\n    <!-- This is a comment -->\n    Normal text.\n    <!--\n    This is a\n    multi-line comment\n    -->\n    More text.\n    """
    expected = """\n    # Title\n    Normal text.\n    More text.\n    """
    assert multi_strip(rm_comments(markdown)) == multi_strip(expected), "HTML comments should be removed"


def test_remove_single_line_comments():
    markdown = """\n    # Title\n    %% This is a comment\n    Normal text.\n    %% Another comment\n    More text.\n    """
    expected = """\n    # Title\n    Normal text.\n    More text.\n    """
    assert multi_strip(rm_comments(markdown)) == multi_strip(expected), "Single line comments should be removed"


def test_remove_all_types_of_comments():
    markdown = """\n    # Title\n    <!-- HTML comment -->\n    Normal text.\n    %% Single line comment\n    <!--\n    Multi-line\n    HTML comment\n    -->\n    More text.\n    Final text.\n    """
    expected = """\n    # Title\n    Normal text.\n    More text.\n    Final text.\n    """
    assert multi_strip(rm_comments(markdown)) == multi_strip(expected), "All types of comments should be removed"


def test_no_comments():
    markdown = """\n    # Title\n    This is a normal Markdown\n    document with no comments.\n    """
    assert multi_strip(rm_comments(markdown)) == multi_strip(markdown), "Document without comments should remain unchanged"