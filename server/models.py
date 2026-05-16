from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.ext.associationproxy import association_proxy
from marshmallow import Schema, fields


metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)


class Customer(db.Model):
    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    def __repr__(self):
        return f'<Customer {self.id}, {self.name}>'


class Item(db.Model):
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    price = db.Column(db.Float)

    def __repr__(self):
        return f'<Item {self.id}, {self.name}, {self.price}>'


# --- Review Model ---
class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer)
    comment = db.Column(db.String)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=True)

    customer = db.relationship('Customer', back_populates='reviews')
    item = db.relationship('Item', back_populates='reviews')

    def __repr__(self):
        return f'<Review {self.id}, Customer {self.customer_id}, Item {self.item_id}, Rating {self.rating}>'


# --- Relationships and Association Proxies ---
Customer.reviews = db.relationship('Review', back_populates='customer', cascade='all, delete-orphan')
Customer.items = association_proxy('reviews', 'item')

Item.reviews = db.relationship('Review', back_populates='item', cascade='all, delete-orphan')



# --- Marshmallow Schemas ---
class ReviewSchema(Schema):
    id = fields.Int()
    rating = fields.Int()
    comment = fields.Str()
    customer = fields.Nested(lambda: CustomerSchema(exclude=("reviews",)), allow_none=True)
    item = fields.Nested(lambda: ItemSchema(exclude=("reviews",)), allow_none=True)

class ItemSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    price = fields.Float()
    reviews = fields.Nested(lambda: ReviewSchema(exclude=("item",)), many=True)

class CustomerSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    reviews = fields.Nested(lambda: ReviewSchema(exclude=("customer",)), many=True)
    # Use fields.Nested to serialize relationships, but exclude items and reviews from nested outputs
    reviews = fields.Nested('ReviewSchema', many=True, exclude=('item', 'customer'))
    reviewed_items = fields.Nested('ItemSchema', many=True)
