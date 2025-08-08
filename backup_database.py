#!/usr/bin/env python3
"""
Database Backup and Restore Utility for SERP Strategist
Simple backup/restore functionality for SQLite database
"""

import sqlite3
import os
import shutil
import logging
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_database_path():
    """Get the path to the database file."""
    db_path = os.getenv('DATABASE_URL', 'serp_strategist.db')
    if db_path.startswith('sqlite:///'):
        db_path = db_path.replace('sqlite:///', '')
    return db_path

def create_backup(backup_dir='backups'):
    """Create a backup of the current database."""
    db_path = get_database_path()
    
    if not os.path.exists(db_path):
        logger.error(f"Database file not found: {db_path}")
        return False
    
    # Create backup directory
    backup_path = Path(backup_dir)
    backup_path.mkdir(exist_ok=True)
    
    # Generate backup filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f"serp_strategist_backup_{timestamp}.db"
    backup_full_path = backup_path / backup_filename
    
    try:
        # Copy database file
        shutil.copy2(db_path, backup_full_path)
        
        # Verify backup integrity
        conn = sqlite3.connect(str(backup_full_path))
        cursor = conn.cursor()
        cursor.execute("PRAGMA integrity_check")
        result = cursor.fetchone()[0]
        conn.close()
        
        if result == 'ok':
            logger.info(f"✅ Backup created successfully: {backup_full_path}")
            logger.info(f"📊 Backup size: {backup_full_path.stat().st_size} bytes")
            return str(backup_full_path)
        else:
            logger.error(f"❌ Backup integrity check failed: {result}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Backup failed: {str(e)}")
        return False

def restore_backup(backup_file):
    """Restore database from backup file."""
    db_path = get_database_path()
    backup_path = Path(backup_file)
    
    if not backup_path.exists():
        logger.error(f"Backup file not found: {backup_file}")
        return False
    
    try:
        # Verify backup integrity before restore
        conn = sqlite3.connect(str(backup_path))
        cursor = conn.cursor()
        cursor.execute("PRAGMA integrity_check")
        result = cursor.fetchone()[0]
        conn.close()
        
        if result != 'ok':
            logger.error(f"❌ Backup file is corrupted: {result}")
            return False
        
        # Create backup of current database before restore
        current_backup = create_backup('restore_backups')
        if current_backup:
            logger.info(f"📋 Current database backed up to: {current_backup}")
        
        # Restore from backup
        shutil.copy2(backup_path, db_path)
        
        # Verify restored database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA integrity_check")
        result = cursor.fetchone()[0]
        conn.close()
        
        if result == 'ok':
            logger.info(f"✅ Database restored successfully from: {backup_file}")
            return True
        else:
            logger.error(f"❌ Restored database integrity check failed: {result}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Restore failed: {str(e)}")
        return False

def list_backups(backup_dir='backups'):
    """List available backup files."""
    backup_path = Path(backup_dir)
    
    if not backup_path.exists():
        logger.info("No backup directory found")
        return []
    
    backup_files = list(backup_path.glob('serp_strategist_backup_*.db'))
    backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    
    logger.info(f"📋 Available backups ({len(backup_files)}):")
    for i, backup_file in enumerate(backup_files, 1):
        size = backup_file.stat().st_size
        mtime = datetime.fromtimestamp(backup_file.stat().st_mtime)
        logger.info(f"  {i}. {backup_file.name} ({size} bytes, {mtime.strftime('%Y-%m-%d %H:%M:%S')})")
    
    return backup_files

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Database Backup/Restore Utility')
    parser.add_argument('action', choices=['backup', 'restore', 'list'], help='Action to perform')
    parser.add_argument('--file', help='Backup file path for restore operation')
    parser.add_argument('--dir', default='backups', help='Backup directory (default: backups)')
    
    args = parser.parse_args()
    
    if args.action == 'backup':
        create_backup(args.dir)
    elif args.action == 'restore':
        if not args.file:
            logger.error("❌ --file parameter required for restore operation")
        else:
            restore_backup(args.file)
    elif args.action == 'list':
        list_backups(args.dir)