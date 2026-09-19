import os
from typing import List, Tuple

from .formats import ScanData

def recreateTree(data: ScanData, targetDir: str, force: bool = False) -> Tuple[List[str], List[str]]:
    '''
    Recreates the files described by `data` under `targetDir`.

    Returns (written, skipped). Entries whose content is None (binary or
    unreadable at scan time) cannot be restored and are skipped.

    Every destination is validated before anything is written, so a bad
    entry (path traversal, existing file without `force`) aborts the whole
    operation instead of leaving a half-written tree.
    '''
    targetRoot = os.path.realpath(targetDir)

    plan = []
    skipped = []
    conflicts = []

    for relativePath, content in data.items():
        if content is None:
            skipped.append(relativePath)
            continue

        destination = os.path.realpath(os.path.join(targetRoot, *relativePath.split('/')))

        try:
            inside = os.path.commonpath([targetRoot, destination]) == targetRoot
        except ValueError:  # e.g. different drives on Windows
            inside = False
        if not inside or destination == targetRoot:
            raise ValueError(f'Refusing to write outside the target directory: `{relativePath}`')

        if os.path.exists(destination) and not force:
            conflicts.append(relativePath)

        plan.append((relativePath, destination, content))

    if conflicts:
        shown = ', '.join(conflicts[:5]) + (' ...' if len(conflicts) > 5 else '')
        raise FileExistsError(f'{len(conflicts)} file(s) already exist ({shown}). Use --force to overwrite.')

    os.makedirs(targetRoot, exist_ok=True)

    written = []
    for relativePath, destination, content in plan:
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        with open(destination, 'w', encoding='utf-8') as f:
            f.write(content)
        written.append(relativePath)

    return written, skipped