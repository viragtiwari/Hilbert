import os
import re
from pathlib import Path
from typing import Dict, List, Set
import json

class FileMap:
    def __init__(self, path: str, symbols: List[str]):
        self.path = path
        self.symbols = symbols

    def __str__(self) -> str:
        output = [f"\n{self.path}:"]
        for symbol in self.symbols:
            output.append(f"    {symbol.strip()}")
        return "\n".join(output)

class LanguageParser:
    def __init__(self):
        # Define patterns for different languages
        self.patterns = {
            'python': {
                'symbols': [
                    r'class\s+(\w+)(?:\(.*\))?:',
                    r'def\s+(\w+)\s*\([^)]*\):'
                ]
            },
            'javascript': {
                'symbols': [
                    r'(?:export\s+)?class\s+(\w+)',
                    r'(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\([^)]*\)',
                    r'(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\([^)]*\)\s*=>',
                    r'(?:async\s+)?(\w+)\s*\([^)]*\)\s*{',
                    r'(?:export\s+)?interface\s+(\w+)',
                    r'(?:export\s+)?type\s+(\w+)'
                ]
            },
            'java': {
                'symbols': [
                    r'(?:public|private|protected)?\s*(?:static)?\s*class\s+(\w+)',
                    r'(?:public|private|protected)?\s*interface\s+(\w+)',
                    r'(?:public|private|protected)?\s*(?:static)?\s*\w+\s+(\w+)\s*\([^)]*\)',
                    r'(?:public|private|protected)?\s*enum\s+(\w+)'
                ]
            },
            'cpp': {
                'symbols': [
                    r'class\s+(\w+)',
                    r'struct\s+(\w+)',
                    r'(?:\w+\s+)?(\w+)\s*\([^)]*\)\s*(?:const)?\s*(?:noexcept)?\s*(?:override)?\s*(?:final)?\s*(?:=\s*\w+)?\s*(?:{\|;)',
                    r'namespace\s+(\w+)',
                    r'enum(?:\s+class)?\s+(\w+)'
                ]
            },
            'go': {
                'symbols': [
                    r'type\s+(\w+)\s+struct',
                    r'type\s+(\w+)\s+interface',
                    r'func\s+(\w+)\s*\([^)]*\)',
                    r'func\s*\([^)]*\)\s*(\w+)\s*\([^)]*\)'
                ]
            },
            'rust': {
                'symbols': [
                    r'struct\s+(\w+)',
                    r'enum\s+(\w+)',
                    r'trait\s+(\w+)',
                    r'fn\s+(\w+)\s*(?:<[^>]*>)?\s*\([^)]*\)',
                    r'impl(?:\s*<[^>]*>)?\s+(\w+)'
                ]
            },
            'ruby': {
                'symbols': [
                    r'class\s+(\w+)',
                    r'module\s+(\w+)',
                    r'def\s+(\w+)',
                    r'attr_(?:reader|writer|accessor)\s+:(\w+)'
                ]
            }
        }
        
        # File extensions for each language
        self.extensions = {
            'python': ['.py'],
            'javascript': ['.js', '.jsx', '.ts', '.tsx'],
            'java': ['.java'],
            'cpp': ['.cpp', '.hpp', '.h', '.cc'],
            'go': ['.go'],
            'rust': ['.rs'],
            'ruby': ['.rb']
        }

    def get_language(self, file_path: str) -> str:
        suffix = Path(file_path).suffix.lower()
        for lang, exts in self.extensions.items():
            if suffix in exts:
                return lang
        return None

    def parse_file(self, file_path: str) -> List[str]:
        try:
            language = self.get_language(file_path)
            if not language:
                return []

            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Handle multi-line comments
            if language in ['python', 'ruby']:
                content = re.sub(r'"""[\s\S]*?"""', '', content)
                content = re.sub(r"'''[\s\S]*?'''", '', content)
            elif language in ['javascript', 'java', 'cpp', 'rust']:
                content = re.sub(r'/\*[\s\S]*?\*/', '', content)
            
            lines = content.split('\n')
            symbols = []
            
            for line in lines:
                line = line.strip()
                if not line or line.startswith(('//', '#', '--')):
                    continue
                
                for pattern in self.patterns[language]['symbols']:
                    match = re.search(pattern, line)
                    if match:
                        symbols.append(line)
                        break
            
            return symbols

        except Exception as e:
            print(f"Warning: Could not parse {file_path}: {e}")
            return []

class RepoMapper:
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path).resolve()
        self.parser = LanguageParser()

    def _should_ignore(self, path: str) -> bool:
        ignore_patterns = {
            'node_modules', '__pycache__', 'venv', '.git',
            'build', 'dist', '.idea', '.vscode', 'coverage',
            'target', 'bin', 'obj', '.settings',
            'test', 'tests', '__tests__'
        }
        
        path_parts = Path(path).parts
        return any(part in ignore_patterns for part in path_parts)

    def generate_map(self) -> Dict[str, FileMap]:
        repo_map = {}

        for root, _, files in os.walk(self.repo_path):
            if self._should_ignore(root):
                continue

            for file in files:
                file_path = Path(root) / file
                if self._should_ignore(file_path):
                    continue
                
                rel_path = file_path.relative_to(self.repo_path)
                symbols = self.parser.parse_file(str(file_path))
                if symbols:
                    repo_map[str(rel_path)] = FileMap(str(rel_path), symbols)

        return repo_map

def map_repository(repo_path: str) -> None:
    """
    Generate and save a repository map as JSON in the .lagrange directory.
    
    Args:
        repo_path (str): Path to the repository to be mapped
    """
    repo_path = Path(repo_path).resolve()
    codemap_dir = repo_path / '.lagrange'
    codemap_dir.mkdir(exist_ok=True)
    
    mapper = RepoMapper(str(repo_path))
    repo_map = mapper.generate_map()
    
    serializable_map = {}
    for file_path, file_map in repo_map.items():
        serializable_map[file_path] = {
            'path': file_map.path,
            'symbols': file_map.symbols
        }
    
    output_path = codemap_dir / 'repo_map.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(serializable_map, f, indent=2)
    
    for file_map in repo_map.values():
        print(file_map)




