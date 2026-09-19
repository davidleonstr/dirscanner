import os
import fnmatch

class DirectoryScanner:
    def __init__(self, basePath, patterns=None, exclusionPatterns=None):
        self.basePath = basePath
        self.patterns = patterns if patterns else []
        self.exclusionPatterns = [
            self.normalizePattern(p) for p in (exclusionPatterns or []) if p.strip()
        ]

    @staticmethod
    def normalizePattern(pattern):
        '''Lets users write `build/` or `./build` for a directory named `build`.'''
        pattern = pattern.strip()
        if pattern.startswith('./'):
            pattern = pattern[2:]
        return pattern.rstrip('/') or pattern

    def shouldInclude(self, path):
        '''
        Checks if a path matches any of the provided patterns.
        If no patterns are provided, everything is included by default.
        '''
        if not self.patterns:
            return True
        return any(fnmatch.fnmatch(path, p) for p in self.patterns)

    def isExcluded(self, path):
        '''
        Checks if a relative path (Unix-style) is excluded. A pattern matches if it
        fits the full path, or the name of the path or of any parent directory, so
        `node_modules` excludes everything inside any `node_modules` folder and
        `*.pyc` excludes compiled files at any depth. Exclusions take priority
        over inclusion patterns.
        '''
        if not self.exclusionPatterns:
            return False

        parts = path.split('/')
        for i in range(1, len(parts) + 1):
            partial = '/'.join(parts[:i])
            name = parts[i - 1]
            for pattern in self.exclusionPatterns:
                if fnmatch.fnmatch(partial, pattern) or fnmatch.fnmatch(name, pattern):
                    return True
        return False

    def _relative(self, path):
        return os.path.relpath(path, self.basePath).replace(os.sep, '/')

    def scan(self):
        '''
        Recursively scans the directory and returns a dictionary
        containing relative paths and their file content.
        '''
        scanResult = {}

        for root, dirs, files in os.walk(self.basePath):
            # Prune excluded directories so they are never traversed.
            dirs[:] = sorted(d for d in dirs if not self.isExcluded(self._relative(os.path.join(root, d))))

            for fileName in sorted(files):
                filePath = os.path.join(root, fileName)

                # Normalize relative path (Unix-style) for pattern matching
                relativePath = self._relative(filePath)

                if self.isExcluded(relativePath):
                    continue

                if self.shouldInclude(relativePath):
                    try:
                        with open(filePath, 'r', encoding='utf-8') as f:
                            content = f.read()
                    except Exception:
                        # If file is unreadable (binary, permissions), store None
                        content = None

                    scanResult[relativePath] = content

        return scanResult