import json
import argparse
import sys

# Directory scanner from core
from dirscanner.core import DirectoryScanner, InputFile

parser = argparse.ArgumentParser(description='Scan a directory and generate a JSON with filtered content.')
    
# Input/Output arguments
parser.add_argument('directory', help='Base directory to scan')
parser.add_argument('--output', '-o', help='Destination JSON file')
parser.add_argument('--stdin', action='store_true', help='Print JSON to terminal')
    
# Pattern management arguments
parser.add_argument('--patterns', '-p', nargs='+', help='Direct inclusion patterns (e.g., *.py)')
parser.add_argument('--input', '-i', help='File containing inclusion patterns (gitignore style)')

args = parser.parse_args()

def main(args):
    # Consolidate all patterns from CLI and input file
    allPatterns = args.patterns if args.patterns else []
    
    # If input file add the patterns
    if args.input:
        inputFile = InputFile(args.input)
        allPatterns.extend(inputFile.getPatterns())

    # Core logic centralized in the object
    scanner = DirectoryScanner(args.directory, allPatterns)
    data = scanner.scan()
        
    jsonOutput = json.dumps(data, indent=4, ensure_ascii=False)

    # Handle output persistence
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(jsonOutput)
        
    # Print to terminal if --stdin is set or if no output file is provided
    if args.stdin or not args.output:
        sys.stdout.write(jsonOutput)

# Entry point
if __name__ == '__main__':
    main(args)