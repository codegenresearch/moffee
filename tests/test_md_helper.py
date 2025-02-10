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
    # Clearer divider definitions
    assert is_divider("---") is True, "Single dash divider"
    assert is_divider("***") is True, "Single asterisk divider"
    assert is_divider("___") is True, "Single underscore divider"
    assert is_divider("  ----  ") is True, "Single dash divider with spaces"
    assert is_divider("--") is False, "Two dashes"
    assert is_divider("- - -") is False, "Dashes with spaces"
    assert is_divider("This is not a divider") is False, "Normal text"
    assert is_divider("***", type="*") is True, "Specific asterisk divider"
    assert is_divider("***", type="-") is False, "Specific dash divider"
    assert is_divider("* * *", type="*") is False, "Asterisks with spaces"
    assert is_divider("<->") is True, "Arrow divider"
    assert is_divider("===", type="=") is True, "Specific equals divider"
    assert is_divider("==", type="=") is False, "Two equals"
    assert is_divider("===", type="*") is False, "Equals with asterisk type"
    assert is_divider("===", type="_") is False, "Equals with underscore type"
    assert is_divider("===", type="<") is False, "Equals with arrow type"
    assert is_divider("===", type=">") is False, "Equals with invalid type"


def test_contains_image():
    assert contains_image("![Alt text](image.jpg)") is True, "Image with alt text"
    assert contains_image("This is an image: ![Alt text](image.jpg)") is True, "Image in sentence"
    assert contains_image("This is not an image") is False, "No image"
    assert contains_image("![](image.jpg)") is True, "Image with empty alt text"
    assert contains_image("![]()") is True, "Image with empty alt text and URL"
    assert contains_image("![]") is False, "Incomplete image tag"
    assert contains_image("![]]") is False, "Incorrectly closed image tag"
    assert contains_image("![](") is False, "Incorrectly opened image tag"
    assert contains_image("![]([])") is False, "Nested brackets in image tag"
    assert contains_image("![]([]]") is False, "Nested brackets with incorrect close in image tag"
    assert contains_image("![]([)]") is False, "Nested brackets with incorrect order in image tag"


def test_contains_deco():
    # Enhanced parsing for custom decorators
    assert contains_deco("@(layout=split, background=blue)") is True, "Decorator with multiple key-value pairs"
    assert contains_deco("  @(layout=default)  ") is True, "Decorator with spaces"
    assert contains_deco("This is not a deco") is False, "Normal text"
    assert contains_deco("@(key=value) Some text") is False, "Decorator followed by text"
    assert contains_deco("@()") is True, "Empty decorator"
    assert contains_deco("@(key1=value1, key2=value2)") is True, "Decorator with two key-value pairs"
    assert contains_deco("@(key1=value1, key2=value2, key3=value3)") is True, "Decorator with three key-value pairs"
    assert contains_deco("@(key1=value1, key2=value2, key3=value3, key4=value4)") is True, "Decorator with four key-value pairs"
    assert contains_deco("@(key1=value1, key2=value2, key3=value3, key4=value4, key5=value5)") is True, "Decorator with five key-value pairs"
    assert contains_deco("@(key1=value1, key2=value2, key3=value3, key4=value4, key5=value5, key6=value6)") is True, "Decorator with six key-value pairs"
    assert contains_deco("@(key1=value1, key2=value2, key3=value3, key4=value4, key5=value5, key6=value6, key7=value7)") is True, "Decorator with seven key-value pairs"
    assert contains_deco("@(key1=value1, key2=value2, key3=value3, key4=value4, key5=value5, key6=value6, key7=value7, key8=value8)") is True, "Decorator with eight key-value pairs"
    assert contains_deco("@(key1=value1, key2=value2, key3=value3, key4=value4, key5=value5, key6=value6, key7=value7, key8=value8, key9=value9)") is True, "Decorator with nine key-value pairs"
    assert contains_deco("@(key1=value1, key2=value2, key3=value3, key4=value4, key5=value5, key6=value6, key7=value7, key8=value8, key9=value9, key10=value10)") is True, "Decorator with ten key-value pairs"
    assert contains_deco("@(key1=value1, key2=value2, key3=value3, key4=value4, key5=value5, key6=value6, key7=value7, key8=value8, key9=value9, key10=value10, key11=value11)") is True, "Decorator with eleven key-value pairs"
    assert contains_deco("@(key1=value1, key2=value2, key3=value3, key4=value4, key5=value5, key6=value6, key7=value7, key8=value8, key9=value9, key10=value10, key11=value11, key12=value12)") is True, "Decorator with twelve key-value pairs"
    assert contains_deco("@(key1=value1, key2=value2, key3=value3, key4=value4, key5=value5, key6=value6, key7=value7, key8=value8, key9=value9, key10=value10, key11=value11, key12=value12, key13=value13)") is True, "Decorator with thirteen key-value pairs"
    assert contains_deco("@(key1=value1, key2=value2, key3=value3, key4=value4, key5=value5, key6=value6, key7=value7, key8=value8, key9=value9, key10=value10, key11=value11, key12=value12, key13=value13, key14=value14)") is True, "Decorator with fourteen key-value pairs"
    assert contains_deco("@(key1=value1, key2=value2, key3=value3, key4=value4, key5=value5, key6=value6, key7=value7, key8=value8, key9=value9, key10=value10, key11=value11, key12=value12, key13=value13, key14=value14, key15=value15)") is True, "Decorator with fifteen key-value pairs"
    assert contains_deco("@(key1=value1, key2=value2, key3=value3, key4=value4, key5=value5, key6=value6, key7=value7, key8=value8, key9=value9, key10=value10, key11=value11, key12=value12, key13=value13, key14=value14, key15=value15, key16=value16)") is True, "Decorator with sixteen key-value pairs"
    assert contains_deco("@(key1=value1, key2=value2, key3=value3, key4=value4, key5=value5, key6=value6, key7=value7, key8=value8, key9=value9, key10=value10, key11=value11, key12=value12, key13=value13, key14=value14, key15=value15, key16=value16, key17=value17)") is True, "Decorator with seventeen key-value pairs"
    assert contains_deco("@(key1=value1, key2=value2, key3=value3, key4=value4, key5=value5, key6=value6, key7=value7, key8=value8, key9=value9, key10=value10, key11=value11, key12=value12, key13=value13, key14=value14, key15=value15, key16=value16, key17=value17, key18=value18)") is True, "Decorator with eighteen key-value pairs"
    assert contains_deco("@(key1=value1, key2=value2, key3=value3, key4=value4, key5=value5, key6=value6, key7=value7, key8=value8, key9=value9, key10=value10, key11=value11, key12=value12, key13=value13, key14=value14, key15=value15, key16=value16, key17=value17, key18=value18, key19=value19)") is True, "Decorator with nineteen key-value pairs"
    assert contains_deco("@(key1=value1, key2=value2, key3=value3, key4=value4, key5=value5, key6=value6, key7=value7, key8=value8, key9=value9, key10=value10, key11=value11, key12=value12, key13=value13, key14=value14, key15=value15, key16=value16, key17=value17, key18=value18, key19=value19, key20=value20)") is True, "Decorator with twenty key-value pairs"


def test_extract_title():
    assert extract_title("# Main Title\nSome content") == "Main Title", "Single level 1 header"
    assert extract_title("## Secondary Title\nSome content") == "Secondary Title", "Single level 2 header"
    assert (
        extract_title("# Main Title\n## Secondary Title\nSome content") == "Main Title"
    ), "Level 1 header before level 2"
    assert (
        extract_title("## Secondary Title\n# Main Title\nSome content")
        == "Secondary Title"
    ), "Level 2 header before level 1"
    assert extract_title("Some content without headings") is None, "No headers"
    assert extract_title("") is None, "Empty string"
    assert extract_title("#  Title with spaces  \nContent") == "Title with spaces", "Header with leading/trailing spaces"
    multi_para = "Para 1\n\nPara 2\n\n# Actual Title\nContent"
    assert extract_title(multi_para) == "Actual Title", "Title after multiple paragraphs"


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
    assert multi_strip(rm_comments(markdown)) == multi_strip(expected), "HTML comments removed"


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
    assert multi_strip(rm_comments(markdown)) == multi_strip(expected), "Single line comments removed"


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
    assert multi_strip(rm_comments(markdown)) == multi_strip(expected), "All types of comments removed"


def test_no_comments():
    markdown = """
    # Title
    This is a normal Markdown
    document with no comments.
    """
    assert multi_strip(rm_comments(markdown)) == multi_strip(markdown), "No comments to remove"