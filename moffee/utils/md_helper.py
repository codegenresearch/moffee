import os
from urllib.parse import urljoin, urlparse
import re
from typing import Optional


def is_comment(line: str) -> bool:
    """
    Determines if a given line is a Markdown comment.
    Markdown comments are in the format <!-- comment -->

    :param line: The line to check
    :return: True if the line is a comment, False otherwise
    """
    return bool(re.match(r"^\s*<!--.*-->\s*$", line))


def get_header_level(line: str) -> int:
    """
    Determines the header level of a given line.

    :param line: The line to check
    :return: The header level (1-6) if it's a header, 0 otherwise
    """
    match = re.match(r"^(#{1,6})\s", line)
    if match:
        return len(match.group(1))
    return 0


def is_empty(line: str) -> bool:
    """
    Determines if a given line is an empty line in markdown.
    A line is empty if it is blank or a comment.

    :param line: The line to check
    :return: True if the line is empty, False otherwise
    """
    return is_comment(line) or line.strip() == ""


def is_divider(line: str, type: Optional[str] = None) -> bool:
    """
    Determines if a given line is a Markdown divider (horizontal rule).
    Markdown dividers are three or more hyphens, asterisks, underscores, or equal signs,
    without any other characters except spaces.

    :param line: The line to check
    :param type: Which type to match, str. e.g. "*" to match "***" only. Defaults to None, match any of "*", "-", "_", or "=".
    :return: True if the line is a divider, False otherwise
    """
    stripped_line = line.strip()
    if len(stripped_line) < 3:
        return False

    if type is None:
        return bool(re.match(r"^\s*[-*_={3,}\s*$", stripped_line))
    elif type == "-":
        return bool(re.match(r"^\s*-{3,}\s*$", stripped_line))
    elif type == "*":
        return bool(re.match(r"^\s*\*{3,}\s*$", stripped_line))
    elif type == "_":
        return bool(re.match(r"^\s*_{3,}\s*$", stripped_line))
    elif type == "=":
        return bool(re.match(r"^\s*={3,}\s*$", stripped_line))
    elif type == "<":
        return stripped_line == "<->"
    else:
        return False


def contains_image(line: str) -> bool:
    """
    Determines if a given line contains a Markdown image.
    Markdown images are in the format ![alt text](image_url)

    :param line: The line to check
    :return: True if the line contains an image, False otherwise
    """
    return bool(re.search(r"!\[.*?\]\(.*?\)", line))


def contains_deco(line: str) -> bool:
    """
    Determines if a given line contains a deco (custom decorator).
    Decos are in the format @(key1=value1, key2=value2, ...)

    :param line: The line to check
    :return: True if the line contains a deco, False otherwise
    """
    return bool(re.match(r"^\s*@\(.*?\)\s*$", line))


def extract_title(document: str) -> Optional[str]:
    """
    Extracts the first level 1 or 2 heading from the document as the title.

    :param document: The document in markdown
    :return: The title if there is one, otherwise None
    """
    heading_pattern = r"^(#|##)\s+(.*?)(?:\n|$)"
    match = re.search(heading_pattern, document, re.MULTILINE)
    if match:
        return match.group(2).strip()
    return None


def rm_comments(document):
    """
    Remove HTML and single-line comments from the markdown document.

    :param document: The markdown document
    :return: The document with comments removed
    """
    document = re.sub(r"<!--[\s\S]*?-->", "", document)
    document = re.sub(r"^\s*%%.*$", "", document, flags=re.MULTILINE)
    return document.strip()