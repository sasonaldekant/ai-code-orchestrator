"""
File Writer Module for AI Code Orchestrator v3.0

This module handles writing generated code to project files with:
- Diff preview before writing
- Backup/rollback support
- Git integration (optional)
- Event notifications for GUI
"""

from __future__ import annotations

import os
import shutil
import logging
import difflib
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class WriteMode(Enum):
    """File write modes."""
    CREATE = "create"      # Create new file (fail if exists)
    OVERWRITE = "overwrite"  # Replace entire file
    PATCH = "patch"        # Apply specific changes
    APPEND = "append"      # Add to end of file


class WriteStatus(Enum):
    """Status of file write operation."""
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    PENDING_APPROVAL = "pending_approval"


@dataclass
class FileDiff:
    """Represents a diff between old and new file content."""
    file_path: str
    old_content: str
    new_content: str
    unified_diff: str = ""
    additions: int = 0
    deletions: int = 0
    
    def __post_init__(self):
        if not self.unified_diff:
            self.unified_diff = self._generate_diff()
            self._count_changes()
    
    def _generate_diff(self) -> str:
        """Generate unified diff."""
        old_lines = self.old_content.splitlines(keepends=True)
        new_lines = self.new_content.splitlines(keepends=True)
        
        diff = difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile=f"a/{Path(self.file_path).name}",
            tofile=f"b/{Path(self.file_path).name}",
            lineterm=""
        )
        return "".join(diff)
    
    def _count_changes(self):
        """Count additions and deletions."""
        for line in self.unified_diff.split("\n"):
            if line.startswith("+") and not line.startswith("+++"):
                self.additions += 1
            elif line.startswith("-") and not line.startswith("---"):
                self.deletions += 1


@dataclass
class WriteResult:
    """Result of a file write operation."""
    status: WriteStatus
    file_path: str
    diff: Optional[FileDiff] = None
    backup_path: Optional[str] = None
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def success(self) -> bool:
        return self.status == WriteStatus.SUCCESS


@dataclass
class WriteRequest:
    """Request to write content to a file."""
    file_path: str
    content: str
    mode: WriteMode = WriteMode.OVERWRITE
    create_backup: bool = True
    require_approval: bool = True


class FileWriter:
    """
    Handles writing generated code to project files.
    
    Features:
    - Preview diffs before writing
    - Create backups for rollback
    - Git integration
    - Batch operations
    
    Usage:
        writer = FileWriter(project_root="E:/Projects/MyApp")
        
        # Preview changes
        diff = writer.preview("src/utils.py", new_code)
        
        # Write with backup
        result = writer.write("src/utils.py", new_code)
        
        # Rollback if needed
        writer.rollback(result.backup_path)
    """
    
    def __init__(
        self,
        project_root: str,
        backup_dir: Optional[str] = None,
        auto_approve: bool = False,
        use_git: bool = True
    ):
        """
        Initialize FileWriter.
        
        Args:
            project_root: Root directory of the project
            backup_dir: Directory for backups (default: .orchestrator/backups)
            auto_approve: Skip approval for writes
            use_git: Use git for version control if available
        """
        self.project_root = Path(project_root)
        self.backup_dir = Path(backup_dir) if backup_dir else self.project_root / ".orchestrator" / "backups"
        self.auto_approve = auto_approve
        self.use_git = use_git
        self.pending_writes: List[WriteRequest] = []
        
        # Create backup directory
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
    def preview(self, file_path: str, new_content: str) -> FileDiff:
        """
        Generate a preview diff without writing.
        
        Args:
            file_path: Relative or absolute path to file
            new_content: The new content to write
            
        Returns:
            FileDiff with old/new content and unified diff
        """
        full_path = self._resolve_path(file_path)
        
        # Read existing content
        old_content = ""
        if full_path.exists():
            old_content = full_path.read_text(encoding="utf-8")
        
        return FileDiff(
            file_path=str(full_path),
            old_content=old_content,
            new_content=new_content
        )
    
    def write(
        self,
        file_path: str,
        content: str,
        mode: WriteMode = WriteMode.OVERWRITE,
        create_backup: bool = True
    ) -> WriteResult:
        """
        Write content to a file.
        
        Args:
            file_path: Path to file (relative to project_root or absolute)
            content: Content to write
            mode: How to write (create, overwrite, patch, append)
            create_backup: Whether to create a backup first
            
        Returns:
            WriteResult with status and details
        """
        full_path = self._resolve_path(file_path)
        backup_path = None
        
        try:
            # Create backup if file exists
            if create_backup and full_path.exists():
                backup_path = self._create_backup(full_path)
            
            # Generate diff for logging
            diff = self.preview(file_path, content)
            
            # Ensure parent directory exists
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write based on mode
            if mode == WriteMode.CREATE:
                if full_path.exists():
                    return WriteResult(
                        status=WriteStatus.FAILED,
                        file_path=str(full_path),
                        error="File already exists"
                    )
                full_path.write_text(content, encoding="utf-8")
                
            elif mode == WriteMode.OVERWRITE:
                full_path.write_text(content, encoding="utf-8")
                
            elif mode == WriteMode.APPEND:
                with open(full_path, "a", encoding="utf-8") as f:
                    f.write(content)
                    
            elif mode == WriteMode.PATCH:
                # For patch mode, content should be a diff to apply
                # TODO: Implement patch application
                pass
            
            logger.info(f"Successfully wrote to {full_path}")
            
            return WriteResult(
                status=WriteStatus.SUCCESS,
                file_path=str(full_path),
                diff=diff,
                backup_path=backup_path
            )
            
        except Exception as e:
            logger.error(f"Failed to write {full_path}: {e}")
            return WriteResult(
                status=WriteStatus.FAILED,
                file_path=str(full_path),
                error=str(e),
                backup_path=backup_path
            )
    
    def write_multiple(
        self,
        files: Dict[str, str],
        create_backup: bool = True
    ) -> List[WriteResult]:
        """
        Write multiple files atomically.
        
        Args:
            files: Dictionary of {file_path: content}
            create_backup: Whether to create backups
            
        Returns:
            List of WriteResult for each file
        """
        results = []
        
        for file_path, content in files.items():
            result = self.write(file_path, content, create_backup=create_backup)
            results.append(result)
            
            # If any write fails, rollback all successful ones
            if not result.success:
                logger.warning(f"Write failed for {file_path}, rolling back...")
                for prev_result in results[:-1]:
                    if prev_result.success and prev_result.backup_path:
                        self.rollback(prev_result.backup_path, prev_result.file_path)
                break
        
        return results
    
    def rollback(self, backup_path: str, original_path: Optional[str] = None) -> bool:
        """
        Rollback a file to its backup.
        
        Args:
            backup_path: Path to the backup file
            original_path: Original file path (if not stored in backup)
            
        Returns:
            True if rollback succeeded
        """
        backup = Path(backup_path)
        
        if not backup.exists():
            logger.error(f"Backup not found: {backup_path}")
            return False
        
        try:
            # Determine original path from backup name if not provided
            if not original_path:
                # Backup format: original_name.timestamp.bak
                parts = backup.stem.rsplit(".", 1)
                original_path = parts[0] if len(parts) > 1 else backup.stem
            
            target = Path(original_path)
            shutil.copy2(backup, target)
            logger.info(f"Rolled back {target} from backup")
            return True
            
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return False
    
    def _resolve_path(self, file_path: str) -> Path:
        """Resolve file path relative to project root."""
        path = Path(file_path)
        if path.is_absolute():
            return path
        return self.project_root / path
    
    def _create_backup(self, file_path: Path) -> str:
        """Create a timestamped backup of a file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{file_path.name}.{timestamp}.bak"
        backup_path = self.backup_dir / backup_name
        
        shutil.copy2(file_path, backup_path)
        logger.debug(f"Created backup: {backup_path}")
        
        return str(backup_path)
    
    def get_pending_writes(self) -> List[WriteRequest]:
        """Get list of pending write requests awaiting approval."""
        return self.pending_writes
    
    def queue_write(self, request: WriteRequest):
        """Queue a write request for approval."""
        self.pending_writes.append(request)
    
    def approve_write(self, index: int) -> WriteResult:
        """Approve and execute a pending write."""
        if index >= len(self.pending_writes):
            return WriteResult(
                status=WriteStatus.FAILED,
                file_path="",
                error="Invalid request index"
            )
        
        request = self.pending_writes.pop(index)
        return self.write(
            request.file_path,
            request.content,
            request.mode,
            request.create_backup
        )
    
    def reject_write(self, index: int):
        """Reject a pending write request."""
        if index < len(self.pending_writes):
            self.pending_writes.pop(index)


class GitIntegration:
    """Optional Git integration for FileWriter."""
    
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self._git_available = self._check_git()
    
    def _check_git(self) -> bool:
        """Check if git is available and this is a git repo."""
        git_dir = self.repo_path / ".git"
        return git_dir.exists()
    
    def create_branch(self, branch_name: str) -> bool:
        """Create a new branch for changes."""
        if not self._git_available:
            return False
        
        import subprocess
        try:
            subprocess.run(
                ["git", "checkout", "-b", branch_name],
                cwd=self.repo_path,
                check=True,
                capture_output=True
            )
            return True
        except subprocess.CalledProcessError:
            return False
    
    def commit(self, message: str, files: List[str] = None) -> bool:
        """Commit changes."""
        if not self._git_available:
            return False
        
        import subprocess
        try:
            if files:
                subprocess.run(
                    ["git", "add"] + files,
                    cwd=self.repo_path,
                    check=True,
                    capture_output=True
                )
            else:
                subprocess.run(
                    ["git", "add", "."],
                    cwd=self.repo_path,
                    check=True,
                    capture_output=True
                )
            
            subprocess.run(
                ["git", "commit", "-m", message],
                cwd=self.repo_path,
                check=True,
                capture_output=True
            )
            return True
        except subprocess.CalledProcessError:
            return False
