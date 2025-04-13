Weather Data API - Simple Documentation

What This API Does:
-------------------
This is a simple weather data service that provides:
- Temperature readings
- Atmospheric pressure data
- Air pollutant levels
All with automatic unit conversion.

How to Use It:
--------------
We have three simple endpoints:

1. Get Temperature:
   - Send POST request to /temperature
   - Include JSON body: {"units": "celsius"} (or "fahrenheit"/"kelvin")

2. Get Pressure:
   - Send POST request to /pressure
   - Include JSON body: {"units": "hpa"} (or "atm"/"mmhg")

3. Get Pollutant Levels:
   - Send POST request to /pollutant
   - Include JSON body: {"units": "ppm"} (or "ppb"/"µg/m³")

Example Response:
----------------
You'll get back data like this:
{
  "parameter": "temperature",
  "measured_value": 25.5,
  "units": "celsius",
  "original_value": 298.65,
  "original_units": "kelvin"
}

Getting Started:
---------------
1. Install Python 3.7+ if you don't have it
2. Create a project folder and navigate to it
3. Set up a virtual environment:
   python -m venv venv
   source venv/bin/activate (Linux/Mac)
   venv\Scripts\activate (Windows)
4. Install requirements:
   pip install flask requests

Running the API:
---------------
Just type:
python app.py

The API will start at http://localhost:5000

Testing:
--------
We've included tests to make sure everything works:
- Run: pytest test_weather_api.py
- Tests check all conversions and error cases

Example API Calls:
------------------
Try these with curl or Postman:

1. Get temperature in Fahrenheit:
curl -X POST -H "Content-Type: application/json" -d '{"units":"fahrenheit"}' http://localhost:5000/temperature

2. Get pressure in mmHg:
curl -X POST -H "Content-Type: application/json" -d '{"units":"mmhg"}' http://localhost:5000/pressure

Need Help?
----------
If something doesn't work:
1. Check you've activated your virtual environment
2. Make sure all packages are installed
3. Try running the tests to identify issues
4. Port 5000 should be available
