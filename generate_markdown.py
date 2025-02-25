from pathlib import Path
import os
import pypandoc
from dataclasses import dataclass
from concurrent.futures import ProcessPoolExecutor


def html_to_markdown(html: str, heading_shift=0) -> str:
    return pypandoc.convert_text(html, 'gfm', format='html', extra_args=[f"--shift-heading-level-by={heading_shift}"])


def markdown_heading(heading: str, heading_shift=0) -> str:
    return "\n" + "#" * (1 + heading_shift) + " " + heading + "\n\n"


@dataclass
class Page:
    route: str
    name: str
    children: list


def render_category(category: dict) -> str:
    result = ""
    result += html_to_markdown(category["details"])
    result += "\n"

    for item in category["items"]:
        result += f"- [{item['name']}]({item['route']}) {item['oneliner']}\n"

    return result


def render_func_parameter_header(parameter: dict) -> str:
    result = f"{parameter['name']}: {', '.join([t for t in parameter['types']])}"
    if parameter['required'] or parameter['named'] or parameter['positional']:
        result += " |"
    if parameter['required']:
        result += " _required_"
    if parameter['named']:
        result += " _named_"
    if parameter['positional']:
        result += " _positional_"
    return result


def render_func_preview(func: dict) -> str:
    result = "```\n"
    result += f"{'.'.join(func['path'] + [func['name']])}(\n"
    for parameter in func["params"]:
        result += "    "
        if parameter["named"]:
            result += parameter['name'] + ": "
        result += ' '.join([n for n in parameter['types']])
        result += "\n"
    result += f") -> {' '.join([r for r in func['returns']])}\n```\n"
    return result 


def render_func(func: dict, heading_shift) -> str:
    result = markdown_heading(func['name'], heading_shift=heading_shift)
    result += render_func_preview(func)

    result += html_to_markdown(func["details"], heading_shift=heading_shift) + "\n"

    result += markdown_heading("Parameters", heading_shift=heading_shift+2)
    for parameter in func["params"]:
        result += markdown_heading(render_func_parameter_header(parameter), heading_shift=heading_shift+2)
        result += html_to_markdown(parameter['details'], heading_shift=heading_shift) + "\n"
        if parameter["example"] is not None:
            result += markdown_heading("Example", heading_shift=heading_shift+3)
            result += html_to_markdown(parameter["example"], heading_shift=heading_shift) + "\n"

    if func["example"] is not None:
        result += markdown_heading("Example", heading_shift=heading_shift+1)
        result += html_to_markdown(func["example"], heading_shift=heading_shift) + "\n"

    if len(func["scope"]) != 0:
        result += markdown_heading("Definitions", heading_shift=heading_shift+1)
        for scope_func in func["scope"]:
            result += render_func(scope_func, heading_shift=heading_shift+2)

    return result


def render_type(type_content: dict, heading_shift=0) -> str:
    result = markdown_heading(type_content['title'], heading_shift=heading_shift)

    result += html_to_markdown(type_content['details'])

    result += "\n"

    if type_content["constructor"] is not None:
        result += render_func(type_content["constructor"], heading_shift=heading_shift+1)

    result += markdown_heading("Definitions", heading_shift=heading_shift+1)
    for method in type_content["scope"]:
        result += render_func(method, heading_shift=heading_shift+2)

    return result


def render_symbols(symbols: dict, heading_shift = 0) -> str:
    result = markdown_heading(symbols['title'], heading_shift=heading_shift+1)
    result += html_to_markdown(symbols['details'], heading_shift=heading_shift)
    result += "\n\n"

    result += "| Symbol | Name | Math Class |\n"
    result += "| ----- | ----- | ----- |\n"
    for symbol in symbols["list"]:
        result += f"| {chr(symbol['codepoint'])} | {symbol['name']} | {symbol['mathClass']} |\n"

    return result


def render_group(group: dict, heading_shift = 0) -> str:
    result = markdown_heading(group['name'], heading_shift=heading_shift)
    result += html_to_markdown(group["details"], heading_shift=heading_shift)

    for func in group["functions"]:
        result += render_func(func, heading_shift=heading_shift+1)

    return result


def render_body(body_type: str, body_content) -> str:
    if body_type == "html":
        return html_to_markdown(body_content)
    elif body_type == "category":
        return render_category(body_content)
    elif body_type == "func":
        return render_func(body_content, 0)
    elif body_type == "type":
        return render_type(body_content)
    elif body_type == "symbols":
        return render_symbols(body_content)
    elif body_type == "group":
        return render_group(body_content)
    else:
        print(f"{body_type} is currently not supported")
        return f"{body_type} is currently not supported"


def make_md_book_page(out_dir: Path, data: dict) -> Page:
    title = data["title"]
    route = data["route"][1:]
    description = data["description"]
    body_content = data["body"]["content"]
    body_kind = data["body"]["kind"]
    print(f"generate page for {route}")

    page = Page(route, title, list())

    if not (out_dir / page.route).exists():
        os.mkdir(out_dir / page.route)

    with open(out_dir / page.route / "README.md", "w") as f:
        f.write(render_body(body_kind, body_content))

    executor = ProcessPoolExecutor(max_workers=3)
    futures = []
    for child in data["children"]:
        futures.append(executor.submit(make_md_book_page, out_dir, child))
    for future in futures:
        page.children.append(future.result())

    return page


def generate_children_entries(indent: int, page: Page) -> str:
    result = "  " * indent + f"- [{page.name}]({Path(page.route)/'README.md'})\n"

    for child in page.children:
        result += generate_children_entries(indent + 1, child)

    return result


def generate_markdown_files(data: dict, out_dir: Path):
    pages = []

    for entry in data:
        pages.append(make_md_book_page(out_dir, entry))

    with open(out_dir / "SUMMARY.md", "w") as f:
        for page in pages:
            f.write(generate_children_entries(0, page))
