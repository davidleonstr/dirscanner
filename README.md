# DirScanner

[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

A CLI utility written in Python designed to scan directories, filter files based on glob patterns, and aggregate their content into a structured JSON format. This tool is optimized for generating code contexts, performing project audits, or creating structured backups of text-based assets.

## Features

* **Recursive Scanning:** Deep-traversal of directory structures to capture all nested files.
* **Pattern Matching:** Full support for Unix-style glob patterns (e.g., `*.py`, `src/*.js`) for precise file inclusion.
* **Dual Pattern Inputs:** Define inclusion rules via command-line arguments or through external configuration files (similar to `.gitignore` syntax).
* **Safe Content Handling:** Automatically handles file encoding; binary files or those with restricted permissions are marked as `null` to ensure process continuity.
* **Flexible Output:** Supports direct file writing or piping results to standard output (`stdout`) for integration with other CLI tools.

## Installation

1. Ensure **Python 3.9** or higher is installed on your system.
2. Clone or download the project source code.
3. **No Dependencies:** This project relies exclusively on the Python Standard Library. No external packages are required.

## Installation as library

```bash
pip install git+https://github.com/davidleonstr/dirscanner.git
```

## Usage as library

The basic command structure as main:

```bash
python -m dirscanner <directory> [options]
```

## Usage

The basic command structure is:

```bash
python main.py <directory> [options]
```

### Examples

**1. Standard Scan (Output to Terminal):**

```bash
python main.py ./folder
```

**2. Filter by Specific Extensions:**

```bash
python main.py ./folder --patterns "*.py" "*.md"
```

**3. Export to JSON File:**

```bash
python main.py ./folder -o snapshot.json
```

**4. Advanced Filtering via Input File:**
If you have a file named `include.txt` with the following content:

```text
# Source code
src/*.py
# Configuration
config/*.json
```

Run:

```bash
python main.py ./folder -i include.txt -o output.json
```

## CLI Arguments Reference

| Argument | Short | Description |
| --- | --- | --- |
| `directory` | - | **Required**. The root directory path to scan. |
| `--output` | `-o` | Path to the destination JSON file. |
| `--stdin` | - | Forces the JSON output to print to the terminal. |
| `--patterns` | `-p` | List of inclusion patterns (e.g., `*.py *.txt`). |
| `--input` | `-i` | Path to a file containing patterns (one per line). |

## Output Format

The tool generates a JSON object where keys represent the relative file paths and values contain the file content:

```json
{
    "src/main.py": "import json\n...",
    "docs/README.md": "# Project Documentation...",
    "assets/icon.png": null
}
```

> **Note:** Files that cannot be read as UTF-8 text (such as images or compiled binaries) will have their value set to `null` within the JSON object.

---

### License

This project is open-source and available under the MIT License.