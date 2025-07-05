import json
from flatlib.chart import Chart
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos

def handler(request):
    # Query params: date (YYYY-MM-DD), time (HH:MM), lat, lon, house_system optional
    params = request.args or {}
    date = params.get('date')
    time = params.get('time')
    lat = params.get('lat')
    lon = params.get('lon')
    house_system = params.get('house_system', 'Placidus')
    # Validate
    if not all([date, time, lat, lon]):
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Eksik parametre: date, time, lat ve lon gereklidir.'})
        }
    try:
        dt = Datetime(date, time, '+00:00')  # UTC timezone
        pos = GeoPos(lat, lon)
        chart = Chart(dt, pos, hsys=house_system)
        planets = ['SUN', 'MOON', 'MERCURY', 'VENUS', 'MARS', 'JUPITER',
                   'SATURN', 'URANUS', 'NEPTUNE', 'PLUTO', 'ASC', 'MC']
        data = []
        for obj in planets:
            point = chart.get(obj)
            data.append({
                'name': obj,
                'sign': point.sign,
                'lon': float(point.lon),
                'house': point.house
            })
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'planets': data})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }
