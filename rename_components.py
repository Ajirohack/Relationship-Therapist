#!/usr/bin/env python3
"""
Component Renaming Script for Hybrid AI Brain Implementation
Renames MirrorCore -> SystemCore and archivist -> DataProcessor
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple

class ComponentRenamer:
    """Handles systematic renaming of components throughout the project"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.rename_mappings = {
            # Case-sensitive mappings
            'MirrorCore': 'SystemCore',
            'mirrorCore': 'systemCore',
            'mirrorcore': 'systemcore',
            'MIRRORCORE': 'SYSTEMCORE',
            'mirror-core': 'system-core',
            'mirror_core': 'system_core',
            
            # Archivist mappings
            'Archivist': 'DataProcessor',
            'archivist': 'dataProcessor',
            'ARCHIVIST': 'DATAPROCESSOR',
            'archivist_': 'data_processor_',
            'archivist-': 'data-processor-'
        }
        
        # File extensions to process
        self.file_extensions = {
            '.py', '.js', '.jsx', '.ts', '.tsx', '.html', '.css', '.scss',
            '.json', '.md', '.txt', '.yml', '.yaml', '.sh', '.env'
        }
        
        # Directories to skip
        self.skip_dirs = {
            '__pycache__', '.git', 'node_modules', '.venv', 'venv',
            '.pytest_cache', '.mypy_cache', 'dist', 'build'
        }
        
        # Files to skip
        self.skip_files = {
            'rename_components.py',  # This script itself
            '.gitignore', '.DS_Store'
        }
        
        self.changes_made = []
        self.files_processed = 0
        self.total_replacements = 0
    
    def should_process_file(self, file_path: Path) -> bool:
        """Check if file should be processed"""
        # Skip if in excluded directory
        for part in file_path.parts:
            if part in self.skip_dirs:
                return False
        
        # Skip if excluded file
        if file_path.name in self.skip_files:
            return False
        
        # Only process files with target extensions
        return file_path.suffix.lower() in self.file_extensions
    
    def rename_in_content(self, content: str, file_path: Path) -> Tuple[str, int]:
        """Rename components in file content"""
        modified_content = content
        replacements_count = 0
        
        for old_name, new_name in self.rename_mappings.items():
            # Count occurrences before replacement
            count = modified_content.count(old_name)
            if count > 0:
                modified_content = modified_content.replace(old_name, new_name)
                replacements_count += count
                
                if count > 0:
                    self.changes_made.append({
                        'file': str(file_path),
                        'old': old_name,
                        'new': new_name,
                        'count': count
                    })
        
        return modified_content, replacements_count
    
    def rename_file_if_needed(self, file_path: Path) -> Path:
        """Rename file if it contains target names"""
        old_name = file_path.name
        new_name = old_name
        
        for old_term, new_term in self.rename_mappings.items():
            if old_term in old_name:
                new_name = new_name.replace(old_term, new_term)
        
        if new_name != old_name:
            new_path = file_path.parent / new_name
            try:
                file_path.rename(new_path)
                self.changes_made.append({
                    'type': 'file_rename',
                    'old_path': str(file_path),
                    'new_path': str(new_path)
                })
                return new_path
            except Exception as e:
                print(f"Warning: Could not rename {file_path} to {new_path}: {e}")
                return file_path
        
        return file_path
    
    def process_file(self, file_path: Path) -> bool:
        """Process a single file"""
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                original_content = f.read()
            
            # Rename content
            modified_content, replacements = self.rename_in_content(original_content, file_path)
            
            # Write back if changes were made
            if replacements > 0:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(modified_content)
                
                self.total_replacements += replacements
                print(f"✅ Updated {file_path.name}: {replacements} replacements")
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
            return False
    
    def process_directory(self, directory: Path = None) -> None:
        """Process all files in directory recursively"""
        if directory is None:
            directory = self.project_root
        
        print(f"🔍 Processing directory: {directory}")
        
        for item in directory.iterdir():
            if item.is_file():
                if self.should_process_file(item):
                    # Rename file if needed
                    renamed_item = self.rename_file_if_needed(item)
                    
                    # Process file content
                    if self.process_file(renamed_item):
                        self.files_processed += 1
                        
            elif item.is_dir() and item.name not in self.skip_dirs:
                self.process_directory(item)
    
    def create_backup_mappings(self) -> None:
        """Create backup of original mappings for rollback"""
        backup_file = self.project_root / 'rename_backup.json'
        
        backup_data = {
            'timestamp': str(Path().cwd()),
            'mappings': self.rename_mappings,
            'changes': self.changes_made
        }
        
        with open(backup_file, 'w') as f:
            json.dump(backup_data, f, indent=2)
        
        print(f"📝 Backup created: {backup_file}")
    
    def run_renaming(self) -> None:
        """Execute the complete renaming process"""
        print("🚀 Starting Component Renaming Process")
        print("=" * 50)
        print(f"Project root: {self.project_root}")
        print(f"Mappings: {len(self.rename_mappings)} terms to rename")
        print()
        
        # Process all files
        self.process_directory()
        
        # Create backup
        self.create_backup_mappings()
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 RENAMING SUMMARY")
        print("=" * 50)
        print(f"Files processed: {self.files_processed}")
        print(f"Total replacements: {self.total_replacements}")
        print(f"Changes logged: {len(self.changes_made)}")
        
        if self.changes_made:
            print("\n🔄 Changes made:")
            for change in self.changes_made[:10]:  # Show first 10 changes
                if 'type' in change and change['type'] == 'file_rename':
                    print(f"  📁 Renamed: {change['old_path']} → {change['new_path']}")
                else:
                    print(f"  📝 {change['file']}: {change['old']} → {change['new']} ({change['count']}x)")
            
            if len(self.changes_made) > 10:
                print(f"  ... and {len(self.changes_made) - 10} more changes")
        
        print("\n✅ Renaming process completed!")
        print("\n🔄 Next steps:")
        print("1. Test the application to ensure everything works")
        print("2. Update any remaining references manually if needed")
        print("3. Commit the changes to version control")
        print("4. Update documentation with new component names")

def create_rollback_script(project_root: str) -> None:
    """Create a rollback script to undo changes if needed"""
    rollback_content = '''#!/usr/bin/env python3
"""
Rollback Script for Component Renaming
Reverts SystemCore -> MirrorCore and DataProcessor -> archivist
"""

import os
import json
from pathlib import Path

def rollback_changes():
    """Rollback the renaming changes"""
    project_root = Path(__file__).parent
    backup_file = project_root / 'rename_backup.json'
    
    if not backup_file.exists():
        print("❌ No backup file found. Cannot rollback.")
        return
    
    # Load backup data
    with open(backup_file, 'r') as f:
        backup_data = json.load(f)
    
    # Create reverse mappings
    reverse_mappings = {
        'SystemCore': 'MirrorCore',
        'systemCore': 'mirrorCore',
        'systemcore': 'mirrorcore',
        'SYSTEMCORE': 'MIRRORCORE',
        'system-core': 'mirror-core',
        'system_core': 'mirror_core',
        'DataProcessor': 'Archivist',
        'dataProcessor': 'archivist',
        'DATAPROCESSOR': 'ARCHIVIST',
        'data_processor_': 'archivist_',
        'data-processor-': 'archivist-'
    }
    
    # Use the ComponentRenamer with reverse mappings
    renamer = ComponentRenamer(str(project_root))
    renamer.rename_mappings = reverse_mappings
    renamer.run_renaming()
    
    print("\n🔄 Rollback completed!")

if __name__ == "__main__":
    rollback_changes()
'''
    
    rollback_path = Path(project_root) / 'rollback_renaming.py'
    with open(rollback_path, 'w') as f:
        f.write(rollback_content)
    
    # Make executable
    os.chmod(rollback_path, 0o755)
    print(f"📝 Rollback script created: {rollback_path}")

def main():
    """Main execution function"""
    # Get project root (current directory)
    project_root = os.getcwd()
    
    print("🧠 Component Renaming for Hybrid AI Brain")
    print("=" * 50)
    print("This script will rename:")
    print("  • MirrorCore → SystemCore")
    print("  • archivist → DataProcessor")
    print("  • All variations and case combinations")
    print()
    
    # Confirm with user
    response = input("Do you want to proceed? (y/N): ").strip().lower()
    if response not in ['y', 'yes']:
        print("❌ Operation cancelled.")
        return
    
    # Create rollback script first
    create_rollback_script(project_root)
    
    # Execute renaming
    renamer = ComponentRenamer(project_root)
    renamer.run_renaming()
    
    print("\n🎉 Component renaming completed successfully!")
    print("\n📋 What was changed:")
    print("  ✅ All 'MirrorCore' references → 'SystemCore'")
    print("  ✅ All 'archivist' references → 'DataProcessor'")
    print("  ✅ File names updated where applicable")
    print("  ✅ Backup and rollback scripts created")
    
    print("\n🔧 Ready to implement hybrid approach!")

if __name__ == "__main__":
    main()