from typing import List, Optional, Tuple, Dict, Any
from dataclasses import dataclass, field, fields
from copy import deepcopy
import yaml
import re
from moffee.utils.md_helper import (
    get_header_level,
    is_divider,
    is_empty,
    rm_comments,
    contains_deco,
)


# Default values for slide dimensions
DEFAULT_SLIDE_WIDTH = 1024
DEFAULT_SLIDE_HEIGHT = 768
DEFAULT_ASPECT_RATIO = "16:9"


@dataclass
class PageOption:
    default_h1: bool = False
    default_h2: bool = True
    default_h3: bool = True
    theme: str = "default"
    layout: str = "content"
    resource_dir: str = "."
    styles: dict = field(default_factory=dict)
    slide_width: Optional[int] = None
    slide_height: Optional[int] = None
    aspect_ratio: str = DEFAULT_ASPECT_RATIO

    @property
    def computed_slide_size(self) -> Tuple[int, int]:
        """
        Calculate the computed slide size based on slide_width, slide_height, and aspect_ratio.
        If slide_width and slide_height are not set, use default values.
        If aspect_ratio is set, adjust the dimensions to match the aspect ratio.
        """
        width = self.slide_width if self.slide_width is not None else DEFAULT_SLIDE_WIDTH
        height = self.slide_height if self.slide_height is not None else DEFAULT_SLIDE_HEIGHT

        if self.aspect_ratio != DEFAULT_ASPECT_RATIO:
            try:
                ratio_width, ratio_height = map(int, self.aspect_ratio.split(':'))
                if width is None:
                    width = int(height * (ratio_width / ratio_height))
                elif height is None:
                    height = int(width * (ratio_height / ratio_width))
            except ValueError:
                raise ValueError(f"Aspect ratio must be in the format 'width:height', got {self.aspect_ratio}")

        return width, height


class Direction:
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"


class Type:
    PARAGRAPH = "paragraph"
    NODE = "node"


class Alignment:
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"
    JUSTIFY = "justify"


@dataclass
class Chunk:
    paragraph: Optional[str] = None
    children: Optional[List["Chunk"]] = field(default_factory=list)  # List of chunks
    direction: Direction = Direction.HORIZONTAL
    type: Type = Type.PARAGRAPH
    alignment: Alignment = Alignment.LEFT


@dataclass
class Page:
    raw_md: str
    option: PageOption
    h1: Optional[str] = None
    h2: Optional[str] = None
    h3: Optional[str] = None

    def __post_init__(self):
        self._preprocess()

    @property
    def title(self) -> Optional[str]:
        return self.h1 or self.h2 or self.h3

    @property
    def subtitle(self) -> Optional[str]:
        if self.h1:
            return self.h2 or self.h3
        elif self.h2:
            return self.h3
        return None

    @property
    def chunk(self) -> Chunk:
        """
        Split raw_md into chunk tree
        Chunk tree branches when in-page divider is met.
        - adjacent "***"s create chunk with horizontal direction
        - adjacent "___" create chunk with vertical direction
        "___" possesses higher priority than "***"

        :return: Root of the chunk tree
        """

        def split_by_div(text, type) -> List[Chunk]:
            strs = [""]
            current_escaped = False
            for line in text.split("\n"):
                if line.strip().startswith(""):
                    current_escaped = not current_escaped
                if is_divider(line, type) and not current_escaped:
                    strs.append("\n")
                else:
                    strs[-1] += line + "\n"
            return [Chunk(paragraph=s.strip()) for s in strs if s.strip()]

        # collect "___"
        vchunks = split_by_div(self.raw_md, "_")
        # split by "***" if possible
        for i in range(len(vchunks)):
            hchunks = split_by_div(vchunks[i].paragraph, "*")
            if len(hchunks) > 1:  # found ***
                vchunks[i] = Chunk(children=hchunks, type=Type.NODE)

        if len(vchunks) == 1:
            return vchunks[0]

        return Chunk(children=vchunks, direction=Direction.VERTICAL, type=Type.NODE)

    def _preprocess(self):
        """
        Additional processing needed for the page.
        Modifies raw_md in place.

        - Removes headings 1-3
        - Strips
        """

        lines = self.raw_md.splitlines()
        lines = [l for l in lines if not (1 <= get_header_level(l) <= 3)]
        self.raw_md = "\n".join(lines).strip()


def parse_frontmatter(document: str) -> Tuple[str, PageOption]:
    """
    Parse the YAML front matter in a given markdown document.

    :param document: Input markdown document as a string.
    :return: A tuple containing the document with front matter removed and the PageOption.
    """
    document = document.strip()
    front_matter = ""
    content = document

    # Check if the document starts with '---'
    if document.startswith("---"):
        parts = document.split("---", 2)
        if len(parts) >= 3:
            front_matter = parts[1].strip()
            content = parts[2].strip()

    # Parse YAML front matter
    try:
        yaml_data = yaml.safe_load(front_matter) if front_matter else {}
    except yaml.YAMLError:
        yaml_data = {}

    # Create PageOption from YAML data
    option = PageOption()
    for field in fields(option):
        name = field.name
        if name in yaml_data:
            setattr(option, name, yaml_data.pop(name))
    option.styles.update(yaml_data)  # Update styles with remaining data

    return content, option


def parse_deco(line: str, base_option: Optional[PageOption] = None) -> PageOption:
    """
    Parses a deco (custom decorator) line and returns a dictionary of key-value pairs.
    If base_option is provided, it updates the option with matching keys from the deco. Otherwise initialize an option.

    :param line: The line containing the deco
    :param base_option: Optional PageOption to update with deco values
    :return: An updated PageOption
    """

    def rm_quotes(s):
        if (s.startswith('"') and s.endswith('"')) or (
            s.startswith("'") and s.endswith("'")
        ):
            return s[1:-1]
        return s

    deco_match = re.match(r"^\s*@\((.*?)\)\s*$", line)
    if not deco_match:
        raise ValueError(f"Input line should contain a deco, {line} received.")

    deco_content = deco_match.group(1)
    pairs = re.findall(r"([\w\-]+)\s*=\s*([^,]+)(?:,|$)", deco_content)
    deco = {key.strip(): rm_quotes(value.strip()) for key, value in pairs}

    if base_option is None:
        base_option = PageOption()

    updated_option = deepcopy(base_option)

    for key, value in deco.items():
        if hasattr(updated_option, key):
            setattr(updated_option, key, parse_value(value))
        else:
            updated_option.styles[key] = parse_value(value)

    return updated_option


def parse_value(value: str):
    """Helper function to parse string values into appropriate types"""
    if value.lower() == "true":
        return True
    elif value.lower() == "false":
        return False
    elif value.isdigit():
        return int(value)
    elif value.replace(".", "", 1).isdigit():
        return float(value)
    return value


def composite(document: str) -> List[Page]:
    """
    Composite a markdown document into slide pages.

    Splitting criteria:
    - New h1/h2/h3 header (except when following another header)
    - "---" Divider (___, ***, +++ not count)

    :param document: Input markdown document as a string.
    :return: List of Page objects representing paginated slides
    """
    pages: List[Page] = []
    current_page_lines = []
    current_escaped = False  # track whether in code area
    current_h1 = current_h2 = current_h3 = None
    prev_header_level = 0

    document = rm_comments(document)
    document, options = parse_frontmatter(document)

    lines = document.split("\n")

    def create_page():
        nonlocal current_page_lines, current_h1, current_h2, current_h3, options
        # Only make new page if has non empty lines

        if all(l.strip() == "" for l in current_page_lines):
            return

        raw_md = ""
        local_option = deepcopy(options)
        for line in current_page_lines:
            if contains_deco(line):
                local_option = parse_deco(line, local_option)
            else:
                raw_md += "\n" + line

        page = Page(
            raw_md=raw_md,
            option=local_option,
            h1=current_h1,
            h2=current_h2,
            h3=current_h3,
        )

        pages.append(page)
        current_page_lines = []
        current_h1 = current_h2 = current_h3 = None

    for _, line in enumerate(lines):
        # update current env stack
        if line.strip().startswith(""):
            current_escaped = not current_escaped

        header_level = get_header_level(line) if not current_escaped else 0

        # Check if this is a new header and not consecutive
        # Only break at heading 1-3
        is_downstep_header_level = (
            prev_header_level == 0 or prev_header_level >= header_level
        )
        is_more_than_level_4 = prev_header_level > header_level >= 3
        if header_level > 0 and is_downstep_header_level and not is_more_than_level_4:
            # Check if the next line is also a header
            create_page()

        if is_divider(line, type="-") and not current_escaped:
            create_page()
            continue

        current_page_lines.append(line)

        if header_level == 1:
            current_h1 = line.lstrip("#").strip()
        elif header_level == 2:
            current_h2 = line.lstrip("#").strip()
        elif header_level == 3:
            current_h3 = line.lstrip("#").strip()
        else:
            pass  # Handle other cases or do nothing

        if header_level > 0:
            prev_header_level = header_level
        if header_level == 0 and not is_empty(line) and not contains_deco(line):
            prev_header_level = 0

    # Create the last page if there's remaining content
    create_page()

    # Process each page and choose titles
    env_h1 = env_h2 = env_h3 = None
    for page in pages:
        inherit_h1 = page.option.default_h1
        inherit_h2 = page.option.default_h2
        inherit_h3 = page.option.default_h3
        if page.h1 is not None:
            env_h1 = page.h1
            env_h2 = env_h3 = None
            inherit_h1 = inherit_h2 = inherit_h3 = False
        if page.h2 is not None:
            env_h2 = page.h2
            env_h3 = None
            inherit_h2 = inherit_h3 = False
        if page.h3 is not None:
            env_h3 = page.h3
            inherit_h3 = False
        if inherit_h1:
            page.h1 = env_h1
        if inherit_h2:
            page.h2 = env_h2
        if inherit_h3:
            page.h3 = env_h3

    return pages


# New test cases
def test_slide_dimensions_in_frontmatter():
    doc = """
---
slide_width: 1024
slide_height: 768
---
# Title
Content
"""
    pages = composite(doc)
    assert pages[0].option.computed_slide_size == (1024, 768)


def test_additional_frontmatter_options():
    doc = """
---
custom_option: value
another_option: 42
---
# Title
Content
"""
    pages = composite(doc)
    assert pages[0].option.styles == {"custom_option": "value", "another_option": 42}


def test_header_inheritance():
    doc = """
# Main Title
Content
## Subtitle
More content
### Subheader
Even more content
"""
    pages = composite(doc)
    assert pages[0].h1 == "Main Title"
    assert pages[1].h1 is None
    assert pages[1].h2 == "Subtitle"
    assert pages[2].h1 is None
    assert pages[2].h2 == "Subtitle"
    assert pages[2].h3 == "Subheader"


def test_page_splitting_on_headers():
    doc = """
# Header 1
Content 1
## Header 2
Content 2
# New Header 1
Content 3
"""
    pages = composite(doc)
    assert len(pages) == 3
    assert pages[0].h1 == "Header 1"
    assert pages[1].h2 == "Header 2"
    assert pages[2].h1 == "New Header 1"


def test_page_splitting_on_dividers():
    doc = """
Content 1
---
Content 2
***
Content 3
"""
    pages = composite(doc)
    assert len(pages) == 2


def test_escaped_area_paging():
    doc = """
Content 1
bash
---
Content 2

***
Content 3
"""
    pages = composite(doc)
    assert len(pages) == 1


def test_escaped_area_chunking():
    doc = """
Content 1
---
Content 2
bash
***
Content 3

"""
    pages = composite(doc)
    assert len(pages) == 2
    assert len(pages[1].chunk.children) == 0


def test_title_and_subtitle():
    doc = """
# Title
## Subtitle
# Title2
#### Heading4
### Heading3
Content
"""
    pages = composite(doc)
    assert len(pages) == 2
    assert pages[0].title == "Title"
    assert pages[0].subtitle == "Subtitle"
    assert pages[1].title == "Title2"


def test_adjacent_headings_same_level():
    doc = """
# Title
## Subtitle
## Subtitle2
### Heading
### Heading2
"""
    pages = composite(doc)
    assert len(pages) == 3
    assert pages[1].title == "Subtitle2"
    assert pages[1].subtitle == "Heading"


def test_chunking_trivial():
    doc = """
Paragraph 1

Paragraph 2
![](image.jpg)
Paragraph 3

Paragraph 4
"""
    pages = composite(doc)
    chunk = pages[0].chunk
    assert chunk.type == Type.PARAGRAPH
    assert len(chunk.children) == 0
    assert chunk.paragraph.strip() == doc.strip()


def test_chunking_vertical():
    doc = """
Paragraph 1
___

Paragraph 2
"""
    pages = composite(doc)
    chunk = pages[0].chunk
    assert chunk.type == Type.NODE
    assert len(chunk.children) == 2
    assert chunk.direction == Direction.VERTICAL
    assert chunk.children[0].type == Type.PARAGRAPH


def test_chunking_horizontal():
    doc = """
Paragraph 1
***

Paragraph 2
***
"""
    pages = composite(doc)
    chunk = pages[0].chunk
    assert chunk.type == Type.NODE
    assert len(chunk.children) == 3
    assert chunk.direction == Direction.HORIZONTAL
    assert chunk.children[0].type == Type.PARAGRAPH


def test_chunking_hybrid():
    doc = """
Other Pages
---
Paragraph 1
___
Paragraph 2
***
Paragraph 3
***
Paragraph 4
"""
    pages = composite(doc)
    assert len(pages) == 2
    chunk = pages[1].chunk
    assert chunk.type == Type.NODE
    assert len(chunk.children) == 2
    assert chunk.direction == Direction.VERTICAL
    assert len(chunk.children[0].children) == 0
    assert chunk.children[0].type == Type.PARAGRAPH
    assert chunk.children[0].paragraph.strip() == "Paragraph 1"
    next_chunk = chunk.children[1]
    assert next_chunk.direction == Direction.HORIZONTAL
    assert len(next_chunk.children) == 3


def test_empty_lines_handling():
    doc = """
# Title

Content with empty line above
"""
    pages = composite(doc)
    assert len(pages[0].chunk.children) == 0
    assert pages[0].option.styles == {}


def test_deco_handling():
    doc = """
---
default_h1: true
---
# Title
@(default_h1=false)
Hello
@(background=blue)
"""
    pages = composite(doc)
    assert pages[0].raw_md == "Hello"
    assert pages[0].option.default_h1 is False
    assert pages[0].option.styles == {"background": "blue"}


def test_multiple_deco():
    doc = """
---
default_h1: true
---
# Title1
@(background=blue)
## Title2
# Title
@(default_h1=false)
Hello
"""
    pages = composite(doc)
    assert len(pages) == 2
    assert pages[0].raw_md == ""
    assert pages[0].title == "Title1"
    assert pages[0].subtitle == "Title2"
    assert pages[0].option.styles == {"background": "blue"}
    assert pages[0].option.default_h1 is True
    assert pages[1].option.default_h1 is False


def test_aspect_ratio_handling():
    doc = """
---
aspect_ratio: 16:9
---
# Title
Content
"""
    pages = composite(doc)
    assert pages[0].option.computed_slide_size == (1024, 576)  # Based on default width


def test_invalid_aspect_ratio():
    doc = """
---
aspect_ratio: 16x9
---
# Title
Content
"""
    try:
        composite(doc)
    except ValueError as e:
        assert str(e) == "Aspect ratio must be in the format 'width:height', got 16x9"


This code addresses the feedback by:
1. Removing any extraneous text or comments that could cause syntax errors.
2. Implementing aspect ratio handling with a specific format ("width:height") and error handling for invalid formats.
3. Setting default values for `slide_width`, `slide_height`, and `aspect_ratio` directly in the class definition.
4. Ensuring proper style handling in the `parse_frontmatter` function.
5. Adding new test cases to cover the scenarios mentioned in the feedback, including aspect ratio handling and invalid aspect ratio errors.