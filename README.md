# DirScanner

[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

A CLI utility written in Python designed to scan directories, filter files based on glob patterns, and aggregate their content into a structured **JSON** or **XML** format. It can also do the reverse: read a JSON/XML snapshot and **recreate the directory tree**. Useful for generating code contexts, project audits, or structured backups of text-based assets.

## Features

* **Two modes:** `--produce` (scan a directory, default) and `--consume` (rebuild a tree from JSON/XML).
* **JSON or XML output:** choose with `--json` / `--xml`, or let the `-o` file extension decide.
* **Recursive Scanning:** Deep-traversal of directory structures to capture all nested files.
* **Pattern Matching:** Unix-style glob patterns (e.g., `*.py`, `src/*.js`) for inclusion.
* **Exclusion Patterns:** `-xp` / `--exclusion-patterns` (inline) or `-xi` / `--exclusion-input` (from a file) to skip files and whole directories (e.g., `node_modules`, `*.pyc`). Exclusions win over inclusions.
* **Dual Pattern Inputs:** Define inclusion rules via command-line arguments or through an external file (similar to `.gitignore` syntax).
* **Safe Content Handling:** Binary or unreadable files are marked as `null` (JSON) or `binary="true"` (XML) so the scan never fails.
* **Safe Consume:** Refuses to write outside the target directory and refuses to overwrite existing files unless `--force` is given.

## Installation

1. Ensure **Python 3.9** or higher is installed.
2. Clone or download the project source code.
3. **No Dependencies:** only the Python Standard Library is used.

### Installation as library

```bash
pip install git+https://github.com/davidleonstr/dirscanner.git
```

## Usage

```bash
python main.py <path> [options]
# or, as a module
python -m dirscanner <path> [options]
```

`<path>` is the directory to scan in `--produce` mode, or the JSON/XML file to read in `--consume` mode.

### Produce examples

```bash
# JSON to the terminal (default)
python main.py ./folder

# XML to the terminal
python main.py ./folder --xml

# Only some extensions
python main.py ./folder --patterns "*.py" "*.md"

# Exclude directories and file types
python main.py ./folder -xp node_modules .git "*.pyc"

# Exclusions from a file
python main.py ./folder -xi exclude.txt

# Write to a file (format inferred from the extension: .xml -> XML, .json -> JSON)
python main.py ./folder -o snapshot.xml

# Patterns from a file
python main.py ./folder -i include.txt -o output.json

# Inclusions and exclusions, both from files
python main.py ./folder -i include.txt -xi exclude.txt -o output.json
```

Example `include.txt`:

```text
# Source code
src/*.py
# Configuration
config/*.json
```

Example `exclude.txt`:

```text
# Dependencies and VCS
node_modules
.git
# Compiled files
*.pyc
build/
```

### Consume examples

```bash
# Recreate the tree from a snapshot into ./restored
python main.py snapshot.xml --consume -o ./restored

# Overwrite files that already exist
python main.py snapshot.json --consume -o ./restored --force
```

The input format is taken from `--json`/`--xml`, otherwise from the file extension, otherwise auto-detected from the content. Entries without content (binary files) cannot be restored and are skipped with a report on stderr.

## CLI Arguments Reference

| Argument | Short | Description |
| --- | --- | --- |
| `path` | - | **Required**. Directory to scan (`--produce`) or JSON/XML file to read (`--consume`). |
| `--produce` | - | Scan a directory and output JSON/XML. Default mode. |
| `--consume` | - | Read a JSON/XML file and recreate its tree in the `--output` directory. |
| `--json` / `--xml` | - | Select the format (mutually exclusive). Default: inferred from the file extension, else JSON. |
| `--output` | `-o` | Destination file (`--produce`) or target directory (`--consume`, required). |
| `--stdin` | - | Forces the output to print to the terminal (`--produce`). |
| `--patterns` | `-p` | Inclusion patterns (e.g., `*.py *.txt`). |
| `--input` | `-i` | File containing inclusion patterns (one per line). |
| `--exclusion-patterns` | `-xp` | Exclusion patterns (e.g., `node_modules "*.pyc"`). |
| `--exclusion-input` | `-xi` | File containing exclusion patterns (one per line). Combined with `-xp` if both are given. |
| `--force` | - | Overwrite existing files (`--consume`). |

### How exclusion patterns match

A pattern excludes a path if it matches the full relative path, or the name of the file or of **any parent directory**. So `node_modules` skips every `node_modules` folder at any depth (and isn't even traversed), `*.pyc` skips compiled files anywhere, and `src/tests` skips that specific folder. Trailing slashes (`build/`) are ignored. Patterns read from an `-xi` file follow the same rules.

## Output Formats

### JSON

Keys are relative file paths; values are the file content.

```json
{
    "src/main.py": "def hello():\n    print(\"Hola mundo\")\n",
    "assets/icon.png": null
}
```

### XML

```xml
<project>
  <folder name="src">
    <file name="main.py">
def hello():
    print("Hola mundo")
    </file>
  </folder>
  <file name="logo.png" binary="true" />
</project>
```

Content starts on the line after the opening tag and the closing tag is placed on its own indented line; both are stripped when consuming, so text files round-trip exactly. Special characters (`<`, `>`, `&`) are escaped.

> **Note:** Files that cannot be read as UTF-8 text (images, compiled binaries) have no content in either format. Empty folders are not recorded.

---

### License

This project is open-source and available under the MIT License.