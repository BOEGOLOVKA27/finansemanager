# app/models/transaction.py
from app import db
from datetime import datetime

class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)  # ← ДОБАВЛЕНО
    operation_type = db.Column(db.Enum('INCOME', 'EXPENSE', name='operation_types'), nullable=False) 
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    user = db.relationship('User', back_populates='transactions')
    category = db.relationship('Category', back_populates='transactions')
    
    def to_dict(self):
        return {
            'id': self.id,
            'amount': float(self.amount),
            'description': self.description,
            'date': self.date.isoformat() if self.date else None,
            'date_display': self.date.strftime('%d.%m.%Y') if self.date else None,
            'operation_type': self.operation_type,
            'category_id': self.category_id,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'category_name': self.category.name if self.category else None
        }
        
    def __repr__(self):
        return f'<Transaction {self.amount} ({self.operation_type})>'

