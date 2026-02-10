#!/usr/bin/env python3
"""
Database Backup Script for Poverello Food Pantry System
Creates a timestamped backup of the database AND product images before beta testing
"""

import shutil
import os
from datetime import datetime

def backup_database():
    """Create a backup of the pantry.db database AND product images"""
    
    # Source database file
    source_db = 'instance/pantry.db'
    
    # Source images directory
    source_images = 'static/images/products'
    
    # Check if database exists
    if not os.path.exists(source_db):
        print(f"❌ Error: Database file '{source_db}' not found!")
        return False
    
    # Create backups directory if it doesn't exist
    backup_dir = 'backups'
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        print(f"✅ Created backups directory: {backup_dir}/")
    
    # Create timestamped backup filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f'{backup_dir}/pantry_backup_{timestamp}.db'
    backup_images_dir = f'{backup_dir}/products_backup_{timestamp}'
    
    # Copy the database
    try:
        shutil.copy2(source_db, backup_file)
        db_size = os.path.getsize(backup_file) / 1024  # Size in KB
        print(f"✅ Database backup created successfully!")
        print(f"   File: {backup_file}")
        print(f"   Size: {db_size:.2f} KB")
    except Exception as e:
        print(f"❌ Error creating database backup: {e}")
        return False
    
    # Copy product images if they exist
    if os.path.exists(source_images):
        try:
            shutil.copytree(source_images, backup_images_dir)
            
            # Count files and calculate total size
            image_count = len([f for f in os.listdir(backup_images_dir) if os.path.isfile(os.path.join(backup_images_dir, f))])
            total_size = sum(os.path.getsize(os.path.join(backup_images_dir, f)) 
                           for f in os.listdir(backup_images_dir) 
                           if os.path.isfile(os.path.join(backup_images_dir, f))) / 1024  # KB
            
            print(f"✅ Product images backup created successfully!")
            print(f"   Directory: {backup_images_dir}/")
            print(f"   Images: {image_count} files")
            print(f"   Size: {total_size:.2f} KB")
        except Exception as e:
            print(f"⚠️  Warning: Could not backup product images: {e}")
            print(f"   Database backup was successful, but images were not backed up.")
    else:
        print(f"ℹ️  No product images directory found at {source_images}")
    
    return True

def restore_database(backup_file):
    """Restore database and product images from a backup"""
    
    if not os.path.exists(backup_file):
        print(f"❌ Error: Backup file '{backup_file}' not found!")
        return False
    
    source_db = 'instance/pantry.db'
    source_images = 'static/images/products'
    
    # Extract timestamp from backup filename
    # Format: pantry_backup_20260209_143022.db
    timestamp = backup_file.replace('backups/pantry_backup_', '').replace('.db', '')
    backup_images_dir = f'backups/products_backup_{timestamp}'
    
    # Create a backup of current database before restoring
    if os.path.exists(source_db):
        temp_backup = f'{source_db}.before_restore'
        shutil.copy2(source_db, temp_backup)
        print(f"⚠️  Current database backed up to: {temp_backup}")
    
    # Restore the database
    try:
        shutil.copy2(backup_file, source_db)
        print(f"✅ Database restored successfully from: {backup_file}")
    except Exception as e:
        print(f"❌ Error restoring database: {e}")
        return False
    
    # Restore product images if backup exists
    if os.path.exists(backup_images_dir):
        try:
            # Backup current images before restoring
            if os.path.exists(source_images):
                temp_images_backup = f'{source_images}_before_restore'
                if os.path.exists(temp_images_backup):
                    shutil.rmtree(temp_images_backup)
                shutil.copytree(source_images, temp_images_backup)
                print(f"⚠️  Current product images backed up to: {temp_images_backup}/")
                
                # Remove current images
                shutil.rmtree(source_images)
            
            # Restore images from backup
            shutil.copytree(backup_images_dir, source_images)
            
            image_count = len([f for f in os.listdir(source_images) if os.path.isfile(os.path.join(source_images, f))])
            print(f"✅ Product images restored successfully!")
            print(f"   Restored {image_count} image files")
        except Exception as e:
            print(f"⚠️  Warning: Could not restore product images: {e}")
            print(f"   Database was restored, but images were not.")
    else:
        print(f"ℹ️  No product images backup found for this timestamp")
    
    return True

def list_backups():
    """List all available backups"""
    
    backup_dir = 'backups'
    
    if not os.path.exists(backup_dir):
        print("No backups directory found.")
        return []
    
    backups = [f for f in os.listdir(backup_dir) if f.startswith('pantry_backup_') and f.endswith('.db')]
    
    if not backups:
        print("No backup files found.")
        return []
    
    print("\n📦 Available Backups:")
    print("-" * 70)
    
    backups.sort(reverse=True)  # Most recent first
    
    for i, backup in enumerate(backups, 1):
        filepath = os.path.join(backup_dir, backup)
        size = os.path.getsize(filepath) / 1024  # KB
        modified = datetime.fromtimestamp(os.path.getmtime(filepath))
        
        # Check if corresponding images backup exists
        timestamp = backup.replace('pantry_backup_', '').replace('.db', '')
        images_dir = f'backups/products_backup_{timestamp}'
        has_images = "✓ Images" if os.path.exists(images_dir) else "✗ No images"
        
        print(f"{i}. {backup}")
        print(f"   DB Size: {size:.2f} KB | Date: {modified.strftime('%Y-%m-%d %H:%M:%S')} | {has_images}")
    
    print("-" * 70)
    return backups

if __name__ == "__main__":
    import sys
    
    print("=" * 60)
    print("🗄️  Poverello Database Backup Tool")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'backup':
            backup_database()
        
        elif command == 'restore':
            backups = list_backups()
            if backups:
                print("\nEnter the number of the backup to restore (or 'q' to quit):")
                choice = input("> ").strip()
                
                if choice.lower() != 'q':
                    try:
                        index = int(choice) - 1
                        if 0 <= index < len(backups):
                            backup_file = os.path.join('backups', backups[index])
                            confirm = input(f"\n⚠️  Are you sure you want to restore from {backups[index]}? (yes/no): ")
                            if confirm.lower() == 'yes':
                                restore_database(backup_file)
                            else:
                                print("Restore cancelled.")
                        else:
                            print("Invalid selection.")
                    except ValueError:
                        print("Invalid input.")
        
        elif command == 'list':
            list_backups()
        
        else:
            print(f"Unknown command: {command}")
            print("\nUsage:")
            print("  python backup_database.py backup   - Create a new backup")
            print("  python backup_database.py restore  - Restore from a backup")
            print("  python backup_database.py list     - List all backups")
    
    else:
        # No arguments - create a backup by default
        print("\n📝 Creating backup...")
        backup_database()
        print("\n💡 Tip: Run 'python backup_database.py list' to see all backups")
        print("💡 Tip: Run 'python backup_database.py restore' to restore a backup")
