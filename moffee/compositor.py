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


# Constants for default values
DEFAULT_ASPECT_RATIO = "16:9"
DEFAULT_SLIDE_WIDTH = 720
DEFAULT_SLIDE_HEIGHT = 405
MIN_ASPECT_RATIO = 1.33
MAX_ASPECT_RATIO = 1.78


@dataclass
class PageOption:
    default_h1: bool = False
    default_h2: bool = True
    default_h3: bool = True
    theme: str = "default"
    layout: str = "content"
    resource_dir: str = "."
    styles: dict = field(default_factory=dict)
    slide_width: int = DEFAULT_SLIDE_WIDTH
    slide_height: int = DEFAULT_SLIDE_HEIGHT
    aspect_ratio: str = DEFAULT_ASPECT_RATIO

    @property
    def computed_slide_size(self) -> Tuple[int, int]:
        """Returns the computed slide size as a tuple (width, height)."""
        width_ratio, height_ratio = map(int, self.aspect_ratio.split(":"))
        calculated_aspect_ratio = width_ratio / height_ratio
        if calculated_aspect_ratio < MIN_ASPECT_RATIO or calculated_aspect_ratio > MAX_ASPECT_RATIO:
            raise ValueError(
                f"Unsupported aspect ratio: {calculated_aspect_ratio}. "
                f"Please use an aspect ratio between {MIN_ASPECT_RATIO} (4:3) and {MAX_ASPECT_RATIO} (16:9)."
            )
        return self.slide_width, self.slide_height

    def __post_init__(self):
        self._validate_aspect_ratio()

    def _validate_aspect_ratio(self):
        """Validates the aspect ratio of the slide dimensions."""
        try:
            ratio_parts = self.aspect_ratio.split(":")
            if len(ratio_parts) != 2:
                raise ValueError("Aspect ratio must be in the format 'width:height'.")
            width_ratio, height_ratio = map(int, ratio_parts)
            calculated_aspect_ratio = width_ratio / height_ratio
            if calculated_aspect_ratio < MIN_ASPECT_RATIO or calculated_aspect_ratio > MAX_ASPECT_RATIO:
                raise ValueError(
                    f"Unsupported aspect ratio: {calculated_aspect_ratio}. "
                    f"Please use an aspect ratio between {MIN_ASPECT_RATIO} (4:3) and {MAX_ASPECT_RATIO} (16:9)."
                )
        except ValueError as e:
            raise ValueError(f"Invalid aspect ratio format: {self.aspect_ratio}. {e}")


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
        """Returns the title of the page, which is the first non-None header."""
        return self.h1 or self.h2 or self.h3

    @property
    def subtitle(self) -> Optional[str]:
        """Returns the subtitle of the page, which is the second non-None header."""
        if self.h1:
            return self.h2 or self.h3
        elif self.h2:
            return self.h3
        return None

    @property
    def chunk(self) -> Chunk:
        """
        Splits raw_md into a chunk tree.
        Chunk tree branches when an in-page divider is met.
        - Adjacent "***"s create a chunk with horizontal direction.
        - Adjacent "___"s create a chunk with vertical direction.
        "___" has higher priority than "***".

        :return: Root of the chunk tree.
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

        # Collect "___"
        vchunks = split_by_div(self.raw_md, "_")
        # Split by "***" if possible
        for i in range(len(vchunks)):
            hchunks = split_by_div(vchunks[i].paragraph, "*")
            if len(hchunks) > 1:  # Found ***
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
        headers = []
        for line in lines:
            header_level = get_header_level(line)
            if 1 <= header_level <= 3:
                headers.append((header_level, line.lstrip("#").strip()))
            else:
                break

        for header_level, header_text in headers:
            if header_level == 1:
                self.h1 = header_text
            elif header_level == 2:
                self.h2 = header_text
            elif header_level == 3:
                self.h3 = header_text

        lines = [l for l in lines if not (1 <= get_header_level(l) <= 3)]
        self.raw_md = "\n".join(lines).strip()


def parse_frontmatter(document: str) -> Tuple[str, PageOption]:
    """
    Parses the YAML front matter in a given markdown document.

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
    option.styles.update(yaml_data)

    return content, option


def parse_deco(line: str, base_option: Optional[PageOption] = None) -> PageOption:
    """
    Parses a deco (custom decorator) line and returns an updated PageOption.
    If base_option is provided, it updates the option with matching keys from the deco.
    Otherwise, it initializes a new PageOption.

    :param line: The line containing the deco.
    :param base_option: Optional PageOption to update with deco values.
    :return: An updated PageOption.
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
    """Helper function to parse string values into appropriate types."""
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
    Composites a markdown document into slide pages.

    Splitting criteria:
    - New h1/h2/h3 header (except when following another header)
    - "---" Divider (___, ***, +++ not counted)

    :param document: Input markdown document as a string.
    :return: List of Page objects representing paginated slides.
    """
    pages: List[Page] = []
    current_page_lines = []
    current_escaped = False  # Track whether in code area
    current_h1 = current_h2 = current_h3 = None
    prev_header_level = 0

    document = rm_comments(document)
    document, options = parse_frontmatter(document)

    lines = document.split("\n")

    def create_page():
        nonlocal current_page_lines, current_h1, current_h2, current_h3, options
        # Only make a new page if there are non-empty lines
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
            raw_md=raw_md.strip(),
            option=local_option,
            h1=current_h1,
            h2=current_h2,
            h3=current_h3,
        )

        pages.append(page)
        current_page_lines = []
        current_h1 = current_h2 = current_h3 = None

    for line in lines:
        # Update current environment stack
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