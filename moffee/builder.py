from typing import List, Dict
import os
from jinja2 import Environment, FileSystemLoader
from moffee.compositor import Page, composite, parse_frontmatter
from moffee.markdown import md
from moffee.utils.md_helper import extract_title
from moffee.utils.file_helper import redirect_paths, copy_assets, merge_directories


def read_options(document_path: str) -> Dict:
    """Read frontmatter options from the document path"""
    with open(document_path, "r") as f:
        document = f.read()
    _, options = parse_frontmatter(document)
    return options


def retrieve_structure(pages: List[Page]) -> Dict:
    current_h1 = None
    current_h2 = None
    current_h3 = None
    headings = []
    page_meta = []

    last_h1_idx = -1
    last_h2_idx = -1
    last_h3_idx = -1

    for i, page in enumerate(pages):
        page_meta.append({"h1": page.h1, "h2": page.h2, "h3": page.h3})

        if page.h1 and page.h1 != current_h1:
            current_h1 = page.h1
            current_h2 = None
            current_h3 = None
            last_h1_idx = len(headings)
            headings.append({"level": 1, "content": page.h1, "page_ids": [i]})
        elif page.h2 and page.h2 != current_h2:
            current_h2 = page.h2
            current_h3 = None
            last_h2_idx = len(headings)
            headings.append({"level": 2, "content": page.h2, "page_ids": [i]})
        elif page.h3 and page.h3 != current_h3:
            current_h3 = page.h3
            last_h3_idx = len(headings)
            headings.append({"level": 3, "content": page.h3, "page_ids": [i]})
        else:
            if last_h1_idx != -1:
                headings[last_h1_idx]["page_ids"].append(i)
            if last_h2_idx != -1:
                headings[last_h2_idx]["page_ids"].append(i)
            if last_h3_idx != -1:
                headings[last_h3_idx]["page_ids"].append(i)

    return {"page_meta": page_meta, "headings": headings}


def render_jinja2(document: str, template_dir: str) -> str:
    """Run jinja2 templating to create html"""
    # Setup Jinja 2
    env = Environment(loader=FileSystemLoader(template_dir))
    env.filters["markdown"] = md

    template = env.get_template("index.html")

    # Fill template
    pages = composite(document)
    title = extract_title(document) or "Untitled"
    options = read_options(document)
    slide_struct = retrieve_structure(pages)

    slide_width, slide_height = options.get("computed_slide_size", ("1024px", "768px"))

    data = {
        "title": title,
        "struct": slide_struct,
        "slides": [
            {
                "h1": page.h1,
                "h2": page.h2,
                "h3": page.h3,
                "chunk": page.chunk,
                "layout": page.option.layout,
                "styles": page.option.styles,
            }
            for page in pages
        ],
        "slide_width": slide_width,
        "slide_height": slide_height,
    }

    return template.render(data)


def build(
    document_path: str, output_dir: str, template_dir: str, theme_dir: str = None
):
    """Render document, create output directories and write result html."""
    asset_dir = os.path.join(output_dir, "assets")

    merge_directories(template_dir, output_dir, theme_dir)
    options = read_options(document_path)
    with open(document_path) as f:
        document = f.read()
    output_html = render_jinja2(document, output_dir)
    output_html = redirect_paths(
        output_html, document_path=document_path, resource_dir=options.get("resource_dir", "")
    )
    output_html = copy_assets(output_html, asset_dir).replace(asset_dir, "assets")

    output_file = os.path.join(output_dir, f"index.html")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(output_html)


### Key Changes:
1. **Removed Invalid Comment**: Removed the invalid comment that was causing a syntax error.
2. **Return Type Consistency**: Ensured the return type of `read_options` is `Dict` to match expected types.
3. **Heading Index Management**: Simplified the logic in `retrieve_structure` to manage indices for headings more clearly.
4. **Data Structure for Headings**: Correctly referenced the last indices for each heading level when appending page IDs.
5. **Slide Size Handling**: Retrieved slide dimensions correctly from `options`.
6. **Order of Operations**: Ensured `merge_directories` is called before reading options in the `build` function.
7. **Use of Filters**: Confirmed that the markdown filter is applied in the Jinja2 environment setup.
8. **Code Clarity and Readability**: Improved clarity and readability by using meaningful variable names and maintaining consistent style.