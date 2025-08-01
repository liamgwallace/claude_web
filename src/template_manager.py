"""
Template manager for initializing Claude Code projects with proper configuration.
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class TemplateManager:
    def __init__(self, templates_dir: str = "templates"):
        # Get the absolute path to the project root (parent of src/)
        current_dir = Path(__file__).parent  # src/
        project_root = current_dir.parent    # project root
        self.templates_dir = project_root / templates_dir
        self.claude_template_dir = self.templates_dir / "claude_project"
        
    def initialize_claude_project(self, project_path: str, project_name: str, 
                                description: Optional[str] = None) -> bool:
        """
        Initialize a new project folder with Claude Code configuration files.
        
        Args:
            project_path: Path to the project directory
            project_name: Name of the project
            description: Optional project description
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            project_dir = Path(project_path)
            project_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy template files
            if not self._copy_template_files(project_dir):
                return False
                
            # Replace template variables
            template_vars = {
                "{{PROJECT_NAME}}": project_name,
                "{{PROJECT_DESCRIPTION}}": description or f"A project created with Claude Code",
                "{{CREATION_DATE}}": datetime.now().isoformat()
            }
            
            if not self._replace_template_variables(project_dir, template_vars):
                return False
                
            logger.info(f"Successfully initialized Claude project: {project_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Claude project {project_name}: {e}")
            return False
    
    def _copy_template_files(self, project_dir: Path) -> bool:
        """
        Copy all template files to the project directory.
        """
        try:
            if not self.claude_template_dir.exists():
                logger.error(f"Template directory not found: {self.claude_template_dir}")
                return False
            
            # Copy all files and directories from template
            for item in self.claude_template_dir.rglob("*"):
                if item.is_file():
                    # Calculate relative path from template root
                    rel_path = item.relative_to(self.claude_template_dir)
                    dest_path = project_dir / rel_path
                    
                    # Create parent directories if they don't exist
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Copy file
                    shutil.copy2(item, dest_path)
                    
            return True
            
        except Exception as e:
            logger.error(f"Failed to copy template files: {e}")
            return False
    
    def _replace_template_variables(self, project_dir: Path, variables: Dict[str, str]) -> bool:
        """
        Replace template variables in all copied files.
        """
        try:
            # Files that should have template variable replacement
            template_files = [
                "README.md",
                ".claude/settings.json",
                "CLAUDE.md"
            ]
            
            for file_path in template_files:
                full_path = project_dir / file_path
                if full_path.exists():
                    # Read file content
                    content = full_path.read_text(encoding='utf-8')
                    
                    # Replace variables
                    for var, value in variables.items():
                        content = content.replace(var, value)
                    
                    # Write back
                    full_path.write_text(content, encoding='utf-8')
                    
            return True
            
        except Exception as e:
            logger.error(f"Failed to replace template variables: {e}")
            return False
    
    def add_custom_instructions(self, project_path: str, instructions: str) -> bool:
        """
        Add custom instructions to the project's CLAUDE.md file.
        
        Args:
            project_path: Path to the project directory
            instructions: Custom instructions to add
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            claude_md_path = Path(project_path) / "CLAUDE.md"
            
            if not claude_md_path.exists():
                logger.error(f"CLAUDE.md not found at: {claude_md_path}")
                return False
            
            # Read existing content
            existing_content = claude_md_path.read_text(encoding='utf-8')
            
            # Add custom instructions section
            custom_section = f"\n\n## Custom Instructions\n\n{instructions}\n"
            updated_content = existing_content + custom_section
            
            # Write back
            claude_md_path.write_text(updated_content, encoding='utf-8')
            
            logger.info(f"Added custom instructions to {project_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add custom instructions: {e}")
            return False
    
    def update_project_settings(self, project_path: str, settings: Dict) -> bool:
        """
        Update project settings in .claude/settings.json
        
        Args:
            project_path: Path to the project directory
            settings: Dictionary of settings to update
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            import json
            
            settings_path = Path(project_path) / ".claude" / "settings.json"
            
            if not settings_path.exists():
                logger.error(f"Settings file not found at: {settings_path}")
                return False
            
            # Read existing settings
            existing_settings = json.loads(settings_path.read_text(encoding='utf-8'))
            
            # Update settings (deep merge)
            def deep_update(base_dict, update_dict):
                for key, value in update_dict.items():
                    if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                        deep_update(base_dict[key], value)
                    else:
                        base_dict[key] = value
            
            deep_update(existing_settings, settings)
            
            # Write back
            settings_path.write_text(json.dumps(existing_settings, indent=2), encoding='utf-8')
            
            logger.info(f"Updated project settings for {project_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update project settings: {e}")
            return False