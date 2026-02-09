"""
Script to add invoice numbers to existing orders
"""
from main import app
from database import db, Order as DBOrder
from datetime import datetime

def generate_invoice_number(order_id, created_at):
    """Generate invoice number in format INV-YYYYMMDD-#####"""
    date_str = created_at.strftime('%Y%m%d')
    order_num = str(order_id).zfill(5)
    return f"INV-{date_str}-{order_num}"

def update_invoice_numbers():
    """Update all orders without invoice numbers"""
    with app.app_context():
        # Get all orders without invoice numbers
        orders = DBOrder.query.filter(
            (DBOrder.invoice_number == None) | (DBOrder.invoice_number == '')
        ).all()
        
        print(f"Found {len(orders)} orders without invoice numbers")
        
        for order in orders:
            invoice_num = generate_invoice_number(order.order_id, order.created_at)
            order.invoice_number = invoice_num
            print(f"Order #{order.order_id} -> {invoice_num}")
        
        db.session.commit()
        print(f"\nSuccessfully updated {len(orders)} orders with invoice numbers")

if __name__ == '__main__':
    update_invoice_numbers()
