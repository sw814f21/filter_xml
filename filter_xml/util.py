import os

from datetime import datetime
from pathlib import Path


def is_file_old(path: str) -> bool:
    """
    Check whether or not a file defined by :param path is modified today
    """
    if not os.path.isfile(path):
        return True

    f_stat = Path(path).stat()
    m_stamp = datetime.fromtimestamp(f_stat.st_mtime)
    now = datetime.now()

    return now.date() != m_stamp.date()