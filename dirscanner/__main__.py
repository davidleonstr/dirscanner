import argparse
import os
import sys

from dirscanner.core import DirectoryScanner, InputFile, serialize, parse, detectFormat, recreateTree

def inferFormat(path):
    '''Guess the format from a file extension, or None if unknown.'''
    if not path:
        return None
    extension = os.path.splitext(path)[1].lower()
    return extension[1:] if extension in ('.json', '.xml') else None

def buildParser():
    parser = argparse.ArgumentParser(
        description='Scan a directory into JSON/XML (--produce), or recreate a directory from JSON/XML (--consume).'
    )

    parser.add_argument(
        'path',
        help='Directory to scan (--produce) or JSON/XML file to read (--consume)'
    )

    # Mode
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--produce', action='store_true', help='Scan a directory and output JSON/XML (default)')
    mode.add_argument('--consume', action='store_true', help='Read a JSON/XML file and recreate its tree in --output')

    # Format
    fmt = parser.add_mutually_exclusive_group()
    fmt.add_argument('--json', dest='format', action='store_const', const='json', help='Use JSON format')
    fmt.add_argument('--xml', dest='format', action='store_const', const='xml', help='Use XML format')

    # Input/Output arguments
    parser.add_argument('--output', '-o', help='Destination file (--produce) or target directory (--consume)')
    parser.add_argument('--stdin', action='store_true', help='Print the result to the terminal (--produce)')

    # Pattern management arguments
    parser.add_argument('--patterns', '-p', nargs='+', help='Direct inclusion patterns (e.g., *.py)')
    parser.add_argument('--input', '-i', help='File containing inclusion patterns (gitignore style)')
    parser.add_argument('-xp', '--exclusion-patterns', dest='exclusionPatterns', nargs='+',
                        help='Exclusion patterns (e.g., node_modules "*.pyc"); they win over inclusions')
    parser.add_argument('-xi', '--exclusion-input', dest='exclusionInput',
                        help='File containing exclusion patterns (one per line, like --input)')

    parser.add_argument('--force', action='store_true', help='Overwrite existing files (--consume)')

    return parser

def runProduce(args):
    if not os.path.isdir(args.path):
        raise NotADirectoryError(f'`{args.path}` is not a directory')

    # Consolidate all patterns from CLI and input file
    allPatterns = list(args.patterns or [])

    # If input file add the patterns
    if args.input:
        allPatterns.extend(InputFile(args.input).getPatterns())

    # Same for exclusions: CLI patterns plus the exclusion input file
    allExclusions = list(args.exclusionPatterns or [])

    if args.exclusionInput:
        allExclusions.extend(InputFile(args.exclusionInput).getPatterns())

    scanner = DirectoryScanner(args.path, allPatterns, allExclusions)
    data = scanner.scan()

    # Explicit flag > output file extension > JSON
    fmt = args.format or inferFormat(args.output) or 'json'
    result = serialize(data, fmt)

    # Handle output persistence
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(result)

    # Print to terminal if --stdin is set or if no output file is provided
    if args.stdin or not args.output:
        sys.stdout.write(result)

def runConsume(args):
    if not os.path.isfile(args.path):
        raise FileNotFoundError(f'`{args.path}` is not a file')

    with open(args.path, 'r', encoding='utf-8-sig') as f:
        text = f.read()

    fmt = args.format or inferFormat(args.path) or detectFormat(text)
    data = parse(text, fmt)

    written, skipped = recreateTree(data, args.output, force=args.force)

    print(f'Recreated {len(written)} file(s) in `{args.output}`.', file=sys.stderr)
    if skipped:
        print(f'Skipped {len(skipped)} file(s) with no recoverable content (binary/unreadable):', file=sys.stderr)
        for path in skipped:
            print(f'  - {path}', file=sys.stderr)

def main():
    parser = buildParser()
    args = parser.parse_args()

    if args.consume:
        if not args.output:
            parser.error('--consume requires --output (-o) with the target directory')
        if args.patterns or args.input or args.exclusionPatterns or args.exclusionInput or args.stdin:
            parser.error('--patterns, --input, --exclusion-patterns, --exclusion-input and --stdin only apply to --produce')

    try:
        if args.consume:
            runConsume(args)
        else:
            runProduce(args)
    except (OSError, ValueError) as e:
        sys.exit(f'Error: {e}')

# Entry point
if __name__ == '__main__':
    main()