import os
from typing import List

class InputFile:
    def __init__(self, path: str) -> None:
        self.path = path

        # If not exists
        if not os.path.exists(self.path):
            raise FileNotFoundError(f'Error: Input file `{self.path}` not found')
    
    def getPatterns(self) -> List[str]:
        with open(self.path, 'r', encoding='utf-8') as f:
            # Strip whitespace and ignore comments or empty lines
            filePatterns = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        return filePatterns