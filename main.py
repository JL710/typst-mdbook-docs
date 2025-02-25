import json
from pathlib import Path
import os
import shutil
import argparse

from generate_markdown import generate_markdown_files


def create_empty_mdbook(path: Path):
    if not path.exists():
        os.mkdir(path)

    with open(path / "book.toml", "w") as f:
        f.write("""
[book]
language = "en"
multilingual = false
src = "src"
title = "Typst MdBook Docs"

[build]
create-missing = false
        """)
    if not (path / "src").exists():
        os.mkdir(path / "src")


def main(data: dict, asset_dir: Path, out_dir: Path):
    create_empty_mdbook(out_dir)

    shutil.copytree(asset_dir, out_dir / "src/assets", dirs_exist_ok=True)

    generate_markdown_files(data, out_dir / "src")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generates a MdBook of the typst docs based on the output of the typst-docs package in the typst repository."
    )
    parser.add_argument("asset_source_dir", type=str)
    parser.add_argument("json_source_file", type=str)
    parser.add_argument("output_directory")

    args = parser.parse_args()

    asset_dir = args.asset_source_dir
    json_file = args.json_source_file
    output_dir = args.output_directory

    with open(json_file, "r") as f:
        data = json.load(f)
    main(data, Path(asset_dir), Path(output_dir))
