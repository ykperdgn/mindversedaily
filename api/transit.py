import json
import swisseph as swe

def handler(request):
    # Beklenen: natal ve transit bilgileri JSON body'de
    try:
        body = request.get_json(force=True)
        natal = body['natal']
        transit = body['transit']
    except Exception as e:
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Eksik veya hatalı veri', 'detail': str(e)})
        }

    # Julian Day hesapla
    jd_natal = swe.julday(natal['year'], natal['month'], natal['day'], natal['hour'] + natal['minute']/60)
    jd_transit = swe.julday(transit['year'], transit['month'], transit['day'], transit['hour'] + transit['minute']/60)

    # Gezegenler
    planets = [swe.SUN, swe.MOON, swe.MERCURY, swe.VENUS, swe.MARS, swe.JUPITER, swe.SATURN]
    planet_names = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn']
    natal_positions = {}
    transit_positions = {}

    for idx, pl in enumerate(planets):
        natal_pos = swe.calc_ut(jd_natal, pl)[0]
        transit_pos = swe.calc_ut(jd_transit, pl)[0]
        natal_positions[planet_names[idx]] = natal_pos
        transit_positions[planet_names[idx]] = transit_pos

    # Basit açı farkı örneği
    aspects = {}
    for name in planet_names:
        diff = abs(transit_positions[name] - natal_positions[name])
        diff = diff if diff <= 180 else 360 - diff
        aspects[name] = diff

    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({
            'natal': natal_positions,
            'transit': transit_positions,
            'aspects': aspects
        })
    }
