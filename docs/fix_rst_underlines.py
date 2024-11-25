#!/usr/bin/env python3
import os
import re

def fix_rst_file(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Find all title patterns (word followed by underline)
    title_pattern = re.compile(r'([^\n]+)\n([~=-]+)\n')
    
    def fix_underline(match):
        title = match.group(1)
        underline_char = match.group(2)[0]  # Get the first character of underline
        return f'{title}\n{underline_char * len(title)}\n'
    
    fixed_content = title_pattern.sub(fix_underline, content)
    
    if fixed_content != content:
        with open(file_path, 'w') as f:
            f.write(fixed_content)
        return True
    return False

def process_directory(directory):
    fixed_files = 0
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.rst'):
                file_path = os.path.join(root, file)
                if fix_rst_file(file_path):
                    print(f'Fixed: {file_path}')
                    fixed_files += 1
    return fixed_files

if __name__ == '__main__':
    docs_dir = os.path.dirname(os.path.abspath(__file__))
    fixed = process_directory(docs_dir)
    print(f'\nFixed {fixed} files')
