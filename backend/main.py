from fastapi import FastAPI, HTTPException
from flatlib.chart import Chart
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Astro Chart API",
    description="Flatlib tabanlı gerçek astrolojik doğum haritası API'si",
    version="1.0.0"
)

# CORS ayarları (frontend ile rahat entegrasyon)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/chart")
async def generate_chart(date: str, time: str, lat: float, lon: float, house_system: str = 'Placidus'):
    """
    Doğum haritası API:
    - date: YYYY-MM-DD
    - time: HH:MM
    - lat, lon: float koordinatlar
    - house_system: Placidus, WholeSign, vs.
    """
    try:
        dt = Datetime(date, time, '+00:00')
        pos = GeoPos(str(lat), str(lon))
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
        return {'planets': data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
