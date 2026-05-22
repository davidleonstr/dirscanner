import os
import fnmatch

class DirectoryScanner:
    def __init__(self, basePath, patterns=None):
        self.basePath = basePath
        self.patterns = patterns if patterns else []

    def shouldInclude(self, path):
        '''
        Checks if a path matches any of the provided patterns.
        If no patterns are provided, everything is included by default.
        '''
        if not self.patterns:
            return True
        return any(fnmatch.fnmatch(path, p) for p in self.patterns)

    def scan(self):
        '''
        Recursively scans the directory and returns a dictionary
        containing relative paths and their file content.
        '''
        scanResult = {}

        for root, _, files in os.walk(self.basePath):
            # No preventive filtering; all directories are traversed 
            # to check their files against the patterns.
            for fileName in files:
                filePath = os.path.join(root, fileName)
                
                # Normalize relative path (Unix-style) for pattern matching
                relativePath = os.path.relpath(filePath, self.basePath).replace(os.sep, '/')

                if self.shouldInclude(relativePath):
                    try:
                        with open(filePath, 'r', encoding='utf-8') as f:
                            content = f.read()
                    except Exception:
                        # If file is unreadable (binary, permissions), store None
                        content = None
                    
                    scanResult[relativePath] = content

        return scanResult