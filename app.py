import os
import re
import uuid
from datetime import datetime
from decimal import ROUND_UP, Decimal, InvalidOperation

from flask import Flask, jsonify, request

app = Flask(__name__)
points_db = {}

def validate_receipt(data):
    errors = []
    required_fields = ['retailer', 'purchaseDate', 'purchaseTime', 'items', 'total']
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing field: {field}")
    if errors:
        return errors

    if not isinstance(data['retailer'], str):
        errors.append("retailer must be a string")

    try:
        datetime.strptime(data['purchaseDate'], "%Y-%m-%d")
    except ValueError:
        errors.append("Invalid purchaseDate format (expected YYYY-MM-DD)")

    if not re.match(r'^([01]\d|2[0-3]):[0-5]\d$', data['purchaseTime']):
        errors.append("Invalid purchaseTime format (expected HH:MM)")

    items = data.get('items', [])
    if not isinstance(items, list) or len(items) < 1:
        errors.append("items must be a non-empty list")
    else:
        for idx, item in enumerate(items):
            if 'shortDescription' not in item or 'price' not in item:
                errors.append(f"Item {idx} missing required fields")
                continue
            desc = item['shortDescription'].strip()
            if len(desc) == 0:
                errors.append(f"Item {idx} description is empty after trimming")
            try:
                price = Decimal(item['price'])
                if price <= 0:
                    errors.append(f"Item {idx} price must be positive")
            except InvalidOperation:
                errors.append(f"Item {idx} has invalid price format")

    try:
        total = Decimal(data['total'])
        if total <= 0:
            errors.append("total must be positive")
    except InvalidOperation:
        errors.append("Invalid total format")

    return errors

def calculate_points(data):
    points = 0
    retailer = data['retailer']
    points += sum(1 for c in retailer if c.isalnum())

    total = Decimal(data['total'])
    if total == total.to_integral_value():
        points += 50

    if total % Decimal('0.25') == 0:
        points += 25

    item_count = len(data['items'])
    points += (item_count // 2) * 5

    for item in data['items']:
        desc = item['shortDescription'].strip()
        if len(desc) % 3 == 0:
            price = Decimal(item['price'])
            points += (price * Decimal('0.2')).quantize(Decimal('1'), rounding=ROUND_UP)

    purchase_date = datetime.strptime(data['purchaseDate'], "%Y-%m-%d")
    if purchase_date.day % 2 != 0:
        points += 6

    purchase_time = datetime.strptime(data['purchaseTime'], "%H:%M").time()
    if datetime.strptime("14:00", "%H:%M").time() <= purchase_time < datetime.strptime("16:00", "%H:%M").time():
        points += 10

    return points

@app.route('/receipts/process', methods=['POST'])
def process_receipt():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400
    
    errors = validate_receipt(data)
    if errors:
        return jsonify({"errors": errors}), 400
    
    receipt_id = str(uuid.uuid4())
    points = calculate_points(data)
    points_db[receipt_id] = points
    return jsonify({"id": receipt_id}), 200

@app.route('/receipts/<string:id>/points', methods=['GET'])
def get_points(id):
    points = points_db.get(id)
    if points is None:
        return jsonify({"error": "Receipt not found"}), 404
    return jsonify({"points": points}), 200

if __name__ == '__main__':
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5000))
    app.run(host=host, port=port, debug=os.environ.get('FLASK_DEBUG', 'False') == 'True')