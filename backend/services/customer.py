from flask import Blueprint, jsonify, request
from utils import *
from db import connection
from datetime import datetime

customer_service = Blueprint('customer_service', __name__, url_prefix='/customer')

@customer_service.route('/min_max_rent', methods=['GET'])
def min_max_rent():
    try:
        query = (f"SELECT p.pincode, "
                f"MIN(u.price) AS Min_Rent, "
                f"MAX(u.price) AS Max_Rent, "
                f"ROUND(AVG(u.price)) AS Avg_Rent, "
                f"MIN(u.area) AS Min_Area, "
                f"MAX(u.area) AS Max_Area, "
                f"ROUND(AVG(u.area)) AS Avg_Area "
                f"FROM property p "
                f"NATURAL JOIN unit u "
                f"GROUP BY p.pincode;")
        rows = run_query(connection, query)

        results = []
        for row in rows:
            results.append({
                    'pincode': row[0],
                    'min_rent': row[1],
                    'max_rent': row[2],
                    'avg_rent': row[3],
                    'min_area': row[4],
                    'max_area': row[5],
                    'avg_area': row[6]
                })
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@customer_service.route('/submit_application', methods=['POST'])
def submit_application():
    try:
        headers = request.headers
        token = headers['Authorization']
        user_id = get_user_id(connection, token)
        if check_agent_role(connection, user_id):
            return jsonify({'error': "User is an Agent"}), 403

        data = request.json
        unit_id = data.get('unit_id')
        created_at = datetime.now().strftime('%Y-%m-%d')
        success = True

        query = (f"INSERT INTO applications (unit_id, user_id, created_at, status) "
                f"VALUES ({unit_id}, {user_id}, '{created_at}', 'pending');")
        if not run_update_query(connection, query):
            success = False
            return jsonify({'success': success}), 409
        result = {'success': success}
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@customer_service.route('/list_properties', methods=['GET'])
def list_properties():
    try:
        data = request.args
        bedrooms = data.get('bedrooms',-1)
        bathrooms = data.get('bathrooms',-1)
        pricemin = data.get('pricemin',-1)
        pricemax = data.get('pricemax',-1)
        areamin = data.get('areamin',-1)
        areamax = data.get('areamax',-1)
        pincode = data.get('pincode',-1)
        propertyName = data.get('propertyName',-1)
        companyName = data.get('companyName',-1)
        query = ("select distinct p.property_id, p.name, c.name, p.address, p.pincode from property p JOIN company c ON p.company_id = c.company_id JOIN unit u ON u.property_id = p.property_id LIMIT 50")
        whereParts = []
        if bedrooms != -1:
            whereParts.append(f"u.bedrooms={bedrooms}")
        if bathrooms != -1:
            whereParts.append(f"u.bathrooms={bathrooms}")
        if areamin != -1:
            whereParts.append(f"u.area>={areamin}")
        if areamax != -1:
            whereParts.append(f"u.area>={areamax}")
        if pricemin != -1:
            whereParts.append(f"u.price>={pricemin}")
        if pricemax != -1:
            whereParts.append(f"u.price<={pricemax}")
        if pincode != -1:
            whereParts.append(f"p.pincode={pincode}")
        if propertyName != -1:
            whereParts.append(f"p.name LIKE '%{propertyName}%'")
        if companyName != -1:
            whereParts.append(f"c.name LIKE '%{companyName}%'")
        if len(whereParts)>0:
            query += " WHERE "
            query += " and ".join(whereParts)
        query += ';'
        rows = run_query(connection, query)

        query2 = ("select * from propertyphoto;")
        rows2 = run_query(connection, query2)

        results = []
        for row in rows:
            results.append({
                    'property_id': row[0],
                    'property_name': row[1],
                    'company_name': row[2],
                    'address': row[3],
                    'pincode': row[4],
                    'photos':[row2[1] for row2 in rows2 if row2[0]==row[0]]
                })
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@customer_service.route('/my_applications', methods=['GET'])
def my_applications():
    try:
        token = request.headers['Authorization']
        user_id = get_user_id(connection, token)
        query = (f"SELECT u.apartment_no, p.name, u.price, a.status "
                f"FROM applications a "
                f"JOIN unit u ON u.unit_id = a.unit_id "
                f"JOIN property p ON p.property_id = u.property_id "
                f"WHERE a.user_id = {user_id}; ")
        rows = run_query(connection, query)

        results = []
        for row in rows:
            results.append({
                    'apartment_no': row[0],
                    'property_name': row[1],
                    'price': row[2],
                    'status': row[3]
                })
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500