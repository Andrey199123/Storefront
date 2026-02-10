# Database Backup Instructions

## Before Beta Testing

**IMPORTANT:** Always create a backup before letting beta testers use the system!

### What Gets Backed Up

The backup script saves:
- ✅ **Database** (`instance/pantry.db`) - All clients, products, orders, inventory, etc.
- ✅ **Product Images** (`static/images/products/`) - All uploaded product photos

### Create a Backup

```bash
python backup_database.py
```

This will create:
- `backups/pantry_backup_TIMESTAMP.db` - Database backup
- `backups/products_backup_TIMESTAMP/` - Product images backup

### List All Backups

```bash
python backup_database.py list
```

Shows all backups with timestamps and whether images are included.

### Restore from a Backup

```bash
python backup_database.py restore
```

This will:
1. Show you all available backups
2. Let you choose which one to restore
3. Backup your current data before restoring (safety!)
4. Restore both database AND product images

## Quick Backup Before Beta Testing

```bash
# 1. Create a backup
python backup_database.py

# 2. Start your Flask app for beta testing
python main.py
```

## After Beta Testing

If testers messed up the database:

```bash
# 1. Stop the Flask app (Ctrl+C)

# 2. Restore the backup
python backup_database.py restore

# 3. Select the backup from before beta testing (look at the timestamp)

# 4. Restart the app
python main.py
```

## Tips

- Backups are stored in `backups/` directory (not tracked by git)
- Each backup is timestamped so you know when it was created
- The restore command creates a safety backup before restoring
- Keep your pre-beta-testing backup safe!
- Both database AND images are backed up together

## MyPlate Categories

Your system uses these food categories:
- **Fruits** 🍎 (Red)
- **Vegetables** 🥦 (Green)
- **Dairy** 🥛 (Blue)
- **Proteins** 🍗 (Purple)
- **Grains** 🌾 (Yellow)
- **Other** (Gray) - for items that don't fit main categories
