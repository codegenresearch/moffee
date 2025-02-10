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
    assert is_divider("===", type="_") is False
    assert is_divider("===", type="<") is False
    assert is_divider("===", type=">") is False


def test_contains_image():
    assert contains_image("![Alt text](image.jpg)") is True
    assert contains_image("This is an image: ![Alt text](image.jpg)") is True
    assert contains_image("This is not an image") is False
    assert contains_image("![](image.jpg)") is True  # Empty alt text
    assert contains_image("![]()") is False  # Empty URL
    assert contains_image("![]") is False  # Missing URL
    assert contains_image("![]]") is False  # Malformed URL
    assert contains_image("![](") is False  # Malformed URL
    assert contains_image("![]([])") is False  # Nested brackets in URL
    assert contains_image("![]([]]") is False  # Nested brackets in URL
    assert contains_image("![]([)]") is False  # Nested brackets in URL


def test_contains_deco():
    assert contains_deco("@(layout=split, background=blue)") is True
    assert contains_deco("  @(layout=default)  ") is True
    assert contains_deco("This is not a deco") is False
    assert contains_deco("@(key=value) Some text") is False
    assert contains_deco("@()") is True  # Empty deco
    assert contains_deco("@(key1=value1, key2=value2)") is True
    assert contains_deco("@(key1=value1, key2=value2, key3=value3)") is True
    assert contains_deco("@(key1=value1, key2=value2, key3=value3, key4=value4)") is True
    assert contains_deco("@(key1=value1, key2=value2, key3=value3, key4=value4, key5=value5)") is True
    assert contains_deco("@(key1=value1, key2=value2, key3=value3, key4=value4, key5=value5, key6=value6)") is True
    assert contains_deco("@(key1=value1, key2=value2, key3=value3, key4=value4, key5=value5, key6=value6, key7=value7)") is True
    assert contains_deco("@(key1=value1, key2=value2, key3=value3, key4=value4, key5=value5, key6=value6, key7=value7, key8=value8)") is True
    assert contains_deco("@(key1=value1, key2=value2, key3=value3, key4=value4, key5=value5, key6=value6, key7=value7, key8=value8, key9=value9)") is True
    assert contains_deco("@(key1=value1, key2=value2, key3=value3, key4=value4, key5=value5, key6=value6, key7=value7, key8=value8, key9=value9, key10=value10)") is True
    assert contains_deco("@(key1=value1, key2=value2, key3=value3, key4=value4, key5=value5, key6=value6, key7=value7, key8=value8, key9=value9, key10=value10, key11=value11)") is True
    assert contains_deco("@(key1=value1, key2=value2, key3=value3, key4=value4, key5=value5, key6=value6, key7=value7, key8=value8, key9=value9, key10=value10, key11=value11, key12=value12)") is True
    assert contains_deco("@(key1=value1, key2=value2, key3=value3, key4=value4, key5=value5, key6=value6, key7=value7, key8=value8, key9=value9, key10=value10, key11=value11, key12=value12, key13=value13)") is True
    assert contains_deco("@(key1=value1, key2=value2, key3=value3, key4=value4, key5=value5, key6=value6, key7=value7, key8=value8, key9=value9, key10=value10, key11=value11, key12=value12, key13=value13, key14=value14)") is True
    assert contains_deco("@(key1=value1, key2=value2, key3=value3, key4=value4, key5=value5, key6=value6, key7=value7, key8=value8, key9=value9, key10=value10, key11=value11, key12=value12, key13=value13, key14=value14, key15=value15)") is True
    assert contains_deco("@(key1=value1, key2=value2, key3=value3, key4=value4, key5=value5, key6=value6, key7=value7, key8=value8, key9=value9, key10=value10, key11=value11, key12=value12, key13=value13, key14=value14, key15=value15, key16=value16)") is True
    assert contains_deco("@(key1=value1, key2=value2, key3=value3, key4=value4, key5=value5, key6=value6, key7=value7, key8=value8, key9=value9, key10=value10, key11=value11, key12=value12, key13=value13, key14=value14, key15=value15, key16=value16, key17=value17)") is True
    assert contains_deco("@(key1=value1, key2=value2, key3=value3, key4=value4, key5=value5, key6=value6, key7=value7, key8=value8, key9=value9, key10=value10, key11=value11, key12=value12, key13=value13, key14=value14, key15=value15, key16=value16, key17=value17, key18=value18)") is True
    assert contains_deco("@(key1=value1, key2=value2, key3=value3, key4=value4, key5=value5, key6=value6, key7=value7, key8=value8, key9=value9, key10=value10, key11=value11, key12=value12, key13=value13, key14=value14, key15=value15, key16=value16, key17=value17, key18=value18, key19=value19)") is True
    assert contains_deco("@(key1=value1, key2=value2, key3=value3, key4=value4, key5=value5, key6=value6, key7=value7, key8=value8, key9=value9, key10=value10, key11=value11, key12=value12, key13=value13, key14=value14, key15=value15, key16=value16, key17=value17, key18=value18, key19=value19, key20=value20)") is True


def test_extract_title():
    assert extract_title("# Main Title\nSome content") == "Main Title"
    assert extract_title("## Secondary Title\nSome content") == "Secondary Title"
    assert (
        extract_title("# Main Title\n## Secondary Title\nSome content") == "Main Title"
    )
    assert (
        extract_title("## Secondary Title\n# Main Title\nSome content")
        == "Secondary Title"
    )
    assert extract_title("Some content without headings") is None
    assert extract_title("") is None
    assert extract_title("#  Title with spaces  \nContent") == "Title with spaces"
    multi_para = "Para 1\n\nPara 2\n\n# Actual Title\nContent"
    assert extract_title(multi_para) == "Actual Title"


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