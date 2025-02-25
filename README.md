# Typst MdBook Docs

This tool generates Typst documentation in Markdown and builds an MdBook from it.

## Generate the Docs

To generate the documentation, you must have the Rust toolchain, including Cargo, installed.

Additionally, you need Python installed with the packages listed in [`requirements.txt`](./requirements.txt).  
You can install them by running:

```bash
pip install -r requirements.txt
```

### Get the Source Data

To obtain the source data used for generating the documentation, you need to clone the Typst repository and run:

```bash
cargo run --package typst-docs --assets-dir <asset-output-dir> --out-file <output-json-file>
```

> Make sure to specify a valid asset directory and output file.

### Run the Python Script

```bash
python3 main.py <asset-dir> <json-file> <build-dir>
```

After execution, you will find the Markdown files and assets in the output directory.  
They are ready to be viewed with any Markdown viewer.

### Build Using MdBook

To build a complete documentation set with search, summaries, and themes, this script generates additional files for MdBook.

If you do not have MdBook installed, you can follow the installation guide [here](https://rust-lang.github.io/mdBook/guide/installation.html).

Once MdBook is installed, navigate to your build directory and run:

```bash
mdbook serve
```

> The URL for the page should be displayed in your console.
