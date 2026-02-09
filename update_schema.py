import sqlite3

conn = sqlite3.connect('instance/pantry.db')
cursor = conn.cursor()

# Add new columns to clients table
try:
    cursor.execute('ALTER TABLE clients ADD COLUMN medical_conditions TEXT DEFAULT ""')
    print('Added medical_conditions to clients')
except Exception as e:
    print(f'medical_conditions: {e}')

try:
    cursor.execute('ALTER TABLE clients ADD COLUMN special_instructions TEXT DEFAULT ""')
    print('Added special_instructions to clients')
except Exception as e:
    print(f'special_instructions: {e}')

try:
    cursor.execute('ALTER TABLE clients ADD COLUMN delivery_address TEXT DEFAULT ""')
    print('Added delivery_address to clients')
except Exception as e:
    print(f'delivery_address: {e}')

try:
    cursor.execute('ALTER TABLE clients ADD COLUMN delivery_notes TEXT DEFAULT ""')
    print('Added delivery_notes to clients')
except Exception as e:
    print(f'delivery_notes: {e}')

# Add new columns to orders table
try:
    cursor.execute('ALTER TABLE orders ADD COLUMN invoice_number TEXT')
    print('Added invoice_number to orders')
except Exception as e:
    print(f'invoice_number: {e}')

try:
    cursor.execute('ALTER TABLE orders ADD COLUMN delivery_address TEXT')
    print('Added delivery_address to orders')
except Exception as e:
    print(f'delivery_address: {e}')

try:
    cursor.execute('ALTER TABLE orders ADD COLUMN delivery_status TEXT')
    print('Added delivery_status to orders')
except Exception as e:
    print(f'delivery_status: {e}')

try:
    cursor.execute('ALTER TABLE orders ADD COLUMN delivery_driver TEXT')
    print('Added delivery_driver to orders')
except Exception as e:
    print(f'delivery_driver: {e}')

try:
    cursor.execute('ALTER TABLE orders ADD COLUMN delivery_notes TEXT')
    print('Added delivery_notes to orders')
except Exception as e:
    print(f'delivery_notes: {e}')

conn.commit()
conn.close()
print('Database updated successfully')
