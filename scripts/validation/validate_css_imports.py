
"""
CSS/Style Import Validator.

This script scans your project's UI source directories for CSS, SCSS, LESS, or other style files.
It extracts `@import` statements and verifies that the target files exist.

It supports:
- Relative imports (e.g., `./foo.css`, `../../bar.css`)
- Absolute imports for aliases (currently manual aliases like @dyn-ui/, @dyn-design-tokens/)

Usage:
    python scripts/validation/validate_css_imports.py [path-to-scan]
    
Example:
    python scripts/validation/validate_css_imports.py ui/src
"""

import os
import re
import sys
from pathlib import Path

# --- Configuration ---
DEFAULT_SCAN_PATH = str(Path("ui/src").resolve())
# TODO: Scan package.json or tsconfig.json for dynamic aliases
ALIASES = {
    "@dyn-ui/": "ui/src/dyn-ui/",
    "@dyn-design-tokens/": "ui/src/dyn-design-tokens/",
    "@/": "ui/src/"
}

# Supported file extensions for styles
STYLE_EXTENSIONS = {".css", ".scss", ".less", ".sass"}

# Regex for CSS-like imports
# Matches: @import "foo.css"; or @import 'foo.css'; or @import url("foo.css");
IMPORT_REGEX = re.compile(r"""
    @import\s+                  # Match @import and whitespace
    (?:url\s*\(\s*)?            # Optional url(
    ['"](.*?)['"]               # Capture path inside quotes
    (?:\s*\))?                  # Optional closing )
    \s*;?                       # Optional semicolon
""", re.VERBOSE | re.IGNORECASE)

def resolve_alias(import_path: str, project_root: Path) -> Path:
    """
    Resolve alias-based paths to absolute paths.
    """
    for alias, replacement in ALIASES.items():
        if import_path.startswith(alias):
            # Convert alias replacement to absolute path
            target = project_root / replacement
            # Append the rest of the path
            remaining = import_path[len(alias):]
            return target.resolve() / remaining
            
    # Default: Return None if no alias matched
    return None

def check_file(file_path: Path, project_root: Path) -> list:
    """
    Check imports in a single file. Returns list of errors.
    """
    errors = []
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        return [f"Could not read file: {e}"]

    # Find line numbers for imports
    lines = content.splitlines()
    
    for line_num, line in enumerate(lines, 1):
        # Using a simpler line-by-line check is often safer than regex on whole file for huge files,
        # but regex is robust enough for imports usually at top.
        # However, checking each line allows precise location reporting.
        match = IMPORT_REGEX.search(line)
        if match:
            import_path_str = match.group(1).strip()
            
            # Skip empty or external URLs (http/https)
            if not import_path_str or import_path_str.startswith(("http:", "https:", "//")):
                continue
            
            resolved_path = None
            
            # 1. Check if alias
            resolved_path = resolve_alias(import_path_str, project_root)
            
            # 2. If not alias, treat as relative path
            if not resolved_path:
                # Resolve relative to the current file
                try:
                    resolved_path = (file_path.parent / import_path_str).resolve()
                except Exception as e:
                    errors.append(f"Line {line_num}: Invalid path format '{import_path_str}' ({e})")
                    continue

            # 3. Check existence
            if not resolved_path.exists():
                # Try adding .css if missing (some preprocessors allow omitting extension)
                if not resolved_path.suffix and (resolved_path.with_suffix(".css").exists()):
                    resolved_path = resolved_path.with_suffix(".css")
                elif not resolved_path.suffix and (resolved_path.with_suffix(".scss").exists()):
                    resolved_path = resolved_path.with_suffix(".scss")
                else:
                    errors.append(f"Line {line_num}: Import not found: '{import_path_str}' -> Checked: {resolved_path}")

    return errors

def scan_directory(scan_path: Path, project_root: Path):
    """
    Recursively scan directory for style files and validate them.
    """
    error_count = 0
    file_count = 0
    
    print(f"Scanning {scan_path} for style imports...")
    
    for root, _, files in os.walk(scan_path):
        for file in files:
            file_path = Path(root) / file
            if file_path.suffix.lower() in STYLE_EXTENSIONS:
                file_count += 1
                file_errors = check_file(file_path, project_root)
                
                if file_errors:
                    try:
                        display_path = file_path.relative_to(project_root)
                    except ValueError:
                        display_path = file_path
                    print(f"\n❌ {display_path}")
                    for err in file_errors:
                        print(f"   - {err}")
                        error_count += 1
    
    print("\n" + "="*40)
    print(f"Scanned {file_count} files.")
    if error_count == 0:
        print("✅ No import errors found.")
        return 0
    else:
        print(f"❌ Found {error_count} broken imports.")
        return 1

if __name__ == "__main__":
    scan_target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(DEFAULT_SCAN_PATH)
    
    # Try to find project root (where scripts/ is)
    # Assuming script is run from project root directly
    current_cwd = Path.cwd()
    
    if not scan_target.exists():
        print(f"Error: Path {scan_target} does not exist.")
        sys.exit(1)

    print(f"Validating styles in: {scan_target}")
    
    exit_code = 0
    if scan_target.is_file():
        # Check single file
        errors = check_file(scan_target, current_cwd)
        if errors:
            print(f"\n❌ {scan_target.relative_to(current_cwd)}")
            for err in errors:
                print(f"   - {err}")
            print(f"\nFound {len(errors)} broken imports.")
            exit_code = 1
        else:
            print("✅ File valid.")
            exit_code = 0
    else:
        # Check directory
        exit_code = scan_directory(scan_target, current_cwd)
        
    sys.exit(exit_code)
