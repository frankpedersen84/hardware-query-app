from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Workbook(db.Model):
    __tablename__ = 'workbooks'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    sheets = db.relationship('Sheet', backref='workbook', lazy=True, cascade='all, delete-orphan')

class Sheet(db.Model):
    __tablename__ = 'sheets'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    workbook_id = db.Column(db.Integer, db.ForeignKey('workbooks.id'), nullable=False)
    columns = db.relationship('Column', backref='sheet', lazy=True, cascade='all, delete-orphan')
    rows = db.relationship('Row', backref='sheet', lazy=True, cascade='all, delete-orphan')

class Column(db.Model):
    __tablename__ = 'columns'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    data_type = db.Column(db.String(50), nullable=False)
    sheet_id = db.Column(db.Integer, db.ForeignKey('sheets.id'), nullable=False)
    cells = db.relationship('Cell', backref='column', lazy=True, cascade='all, delete-orphan')

class Row(db.Model):
    __tablename__ = 'rows'
    
    id = db.Column(db.Integer, primary_key=True)
    row_index = db.Column(db.Integer, nullable=False)
    sheet_id = db.Column(db.Integer, db.ForeignKey('sheets.id'), nullable=False)
    cells = db.relationship('Cell', backref='row', lazy=True, cascade='all, delete-orphan')

class Cell(db.Model):
    __tablename__ = 'cells'
    
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(1000))
    row_id = db.Column(db.Integer, db.ForeignKey('rows.id'), nullable=False)
    column_id = db.Column(db.Integer, db.ForeignKey('columns.id'), nullable=False)
