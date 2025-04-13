from flask import Flask, request, jsonify
import requests
from functools import wraps

app = Flask(__name__)

# Mock third-party API configuration
THIRD_PARTY_APIS = {
    'temperature': {
        'url': 'https://api.weatherservice.example/temp',
        'param': 'temp',
        'original_unit': 'kelvin'
    },
    'pressure': {
        'url': 'https://api.weatherservice.example/pressure',
        'param': 'atm',
        'original_unit': 'hpa'
    }
}

def convert_units(value, from_unit, to_unit):
    """Handles all unit conversions with proper rounding"""
    if from_unit == 'kelvin' and to_unit == 'celsius':
        return round(value - 273.15, 2)  # Round to 2 decimal places
    elif from_unit == 'kelvin' and to_unit == 'fahrenheit':
        return round((value - 273.15) * 9/5 + 32, 2)
    elif from_unit == 'hpa' and to_unit == 'atm':
        return round(value / 1013.25, 4)  # Round to 4 decimal places for pressure
    return value

def validate_units(parameter, units):
    """Validates requested units are supported"""
    valid_units = {
        'temperature': ['celsius', 'fahrenheit'],
        'pressure': ['hpa', 'atm']
    }
    if parameter not in valid_units or units.lower() not in valid_units[parameter]:
        raise ValueError(f"Invalid units for {parameter}")

@app.route('/weather/temperature', methods=['POST'])
def get_temperature():
    """Endpoint for temperature data"""
    try:
        data = request.get_json()
        if not data or 'units' not in data or 'city' not in data:
            return jsonify({'error': 'Missing required parameters'}), 400
        
        units = data['units'].lower()
        validate_units('temperature', units)
        
        # Mock API call
        config = THIRD_PARTY_APIS['temperature']
        response = requests.get(
            config['url'],
            params={'location': data['city'].lower(), 'param': config['param']}
        )
        response.raise_for_status()
        
        temp_k = response.json()['value']
        converted_temp = convert_units(temp_k, config['original_unit'], units)
        
        return jsonify({
            'city': data['city'],
            'temperature': round(converted_temp, 2),
            'units': units,
            'original_value': round(temp_k, 2),
            'original_units': 'kelvin'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except requests.RequestException as e:
        return jsonify({'error': f'Weather service error: {str(e)}'}), 502
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/weather/pressure', methods=['POST'])
def get_pressure():
    """Endpoint for pressure data"""
    try:
        data = request.get_json()
        if not data or 'units' not in data or 'city' not in data:
            return jsonify({'error': 'Missing required parameters'}), 400
        
        units = data['units'].lower()
        validate_units('pressure', units)
        
        # Mock API call
        config = THIRD_PARTY_APIS['pressure']
        response = requests.get(
            config['url'],
            params={'location': data['city'].lower(), 'param': config['param']}
        )
        response.raise_for_status()
        
        pressure_hpa = response.json()['value']
        converted_pressure = convert_units(pressure_hpa, config['original_unit'], units)
        
        return jsonify({
            'city': data['city'],
            'pressure': round(converted_pressure, 4),
            'units': units,
            'original_value': pressure_hpa,
            'original_units': 'hpa'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except requests.RequestException as e:
        return jsonify({'error': f'Pressure service error: {str(e)}'}), 502
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True)