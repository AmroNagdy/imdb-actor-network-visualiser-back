import gzip
import requests

from typing import *

def get(split_row: List[str], headings_to_index: Dict[str, int], heading: str, type_conversion_lambda=None) -> Any:
    entry = split_row[headings_to_index[heading]]

    if entry == '\\N':
        return None
    elif type_conversion_lambda is not None:
        return type_conversion_lambda(entry)
    else:
        return entry

def split(row: str) -> List[str]:
    return row.decode('utf-8').split('\t')

def get_headings_to_index(heading_row: str) -> Dict[str, int]:
    return { heading: index for (index, heading) in enumerate(split(heading_row)) }

def get_headings_and_data(url: str) -> Tuple[Dict[str, int], List[str]]:
    response = requests.get(url, stream=True)
    content = gzip.decompress(response.content)
    headings_and_data = content.splitlines()
    headings_to_index = get_headings_to_index(headings_and_data[0])

    return headings_to_index, headings_and_data[1:]
