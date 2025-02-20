import json
from pathlib import Path
from typing import Dict, List, Union
import ast

def parse_file_list(file_list_str: str) -> List[str]:
    """
    Parse a string representation of a file list into a proper list of file paths.
    """
    escaped_str = file_list_str.replace('\\', '\\\\')
    
    try:
        return json.loads(escaped_str)
    except json.JSONDecodeError:
        try:
            return ast.literal_eval(escaped_str)
        except (SyntaxError, ValueError):
            paths = escaped_str.replace('[', '').replace(']', '').split(',')
            return [p.strip().strip('"\'') for p in paths if p.strip()]

def read_files_from_paths(parent_dir: Union[str, Path], file_paths: Union[str, List[str]]) -> Dict[str, str]:
    """
    Read files and return their complete contents.
    """
    parent_path = Path(parent_dir).resolve()
    
    if isinstance(file_paths, str):
        paths_list = parse_file_list(file_paths)
    else:
        paths_list = file_paths

    file_contents: Dict[str, str] = {}

    for path in paths_list:
        normalized_path = str(Path(path))
        full_path = parent_path / normalized_path
        
        print(f"\n{'='*80}")
        print(f"File: {normalized_path}")
        print('='*80)
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
                file_contents[normalized_path] = content
                print(content)
        except FileNotFoundError:
            print(f"WARNING: File not found: {full_path}")
        except Exception as e:
            print(f"ERROR reading file {full_path}: {str(e)}")

    return file_contents

"""
if __name__ == "__main__":
    raw_input = """ """[
    "client\\js\\commandPalette.js",
    "client\\js\\editor.js",
    "client\\js\\fileExplorer.js",
    "client\\js\\menuBar.js",
    "client\\js\\terminal.js",
    "server\\server.js"
]"""

"""    
    parent_dir = "C:\\Lagrange\\code-editor"
    print(f"Reading files from: {parent_dir}\n")
    files = read_files_from_paths(parent_dir, raw_input)

"""