from flask import Flask, request, jsonify
import requests
from enum import Enum

app = Flask(__name__)

# Configuration for third-party APIs
THIRD_PARTY_APIS = {
    'temperature': {
        'url': 'https://api.weatherservice.example/temp',
        'default_unit': 'kelvin',
        'param_name': 'temp'
    },
    'pressure': {
        'url': 'https://api.weatherservice.example/pressure',
        'default_unit': 'hpa',
        'param_name': 'pressure'
    },
    'pollutant': {
        'url': 'https://api.weatherservice.example/pollutant',
        'default_unit': 'ppm',
        'param_name': 'aqi'
    }
}

class ValidUnits(Enum):
    TEMPERATURE = ['celsius', 'fahrenheit', 'kelvin']
    PRESSURE = ['hpa', 'atm', 'mmhg']
    POLLUTANT = ['ppm', 'ppb', 'µg/m³']

def convert_units(value, from_unit, to_unit, parameter):
    """Handle all unit conversions with proper rounding"""
    try:
        if parameter == 'temperature':
            if from_unit == 'kelvin' and to_unit == 'celsius':
                return round(value - 273.15, 2)
            elif from_unit == 'kelvin' and to_unit == 'fahrenheit':
                return round((value - 273.15) * 9/5 + 32, 2)
            elif from_unit == 'celsius' and to_unit == 'kelvin':
                return round(value + 273.15, 2)
            elif from_unit == 'celsius' and to_unit == 'fahrenheit':
                return round((value * 9/5) + 32, 2)
            elif from_unit == 'fahrenheit' and to_unit == 'celsius':
                return round((value - 32) * 5/9, 2)
            elif from_unit == 'fahrenheit' and to_unit == 'kelvin':
                return round((value - 32) * 5/9 + 273.15, 2)
            return value
        
        elif parameter == 'pressure':
            if from_unit == 'hpa' and to_unit == 'atm':
                return round(value / 1013.25, 4)
            elif from_unit == 'hpa' and to_unit == 'mmhg':
                return round(value * 0.750062, 2)
            elif from_unit == 'atm' and to_unit == 'hpa':
                return round(value * 1013.25, 2)
            elif from_unit == 'atm' and to_unit == 'mmhg':
                return round(value * 760, 2)
            elif from_unit == 'mmhg' and to_unit == 'hpa':
                return round(value / 0.750062, 2)
            elif from_unit == 'mmhg' and to_unit == 'atm':
                return round(value / 760, 4)
            return value
        
        elif parameter == 'pollutant':
            if from_unit == 'ppm' and to_unit == 'ppb':
                return round(value * 1000, 2)
            elif from_unit == 'ppm' and to_unit == 'µg/m³':
                return round(value * 1000, 2)  # Simplified conversion
            elif from_unit == 'ppb' and to_unit == 'ppm':
                return round(value / 1000, 4)
            elif from_unit == 'ppb' and to_unit == 'µg/m³':
                return round(value, 2)
            elif from_unit == 'µg/m³' and to_unit == 'ppm':
                return round(value / 1000, 4)
            elif from_unit == 'µg/m³' and to_unit == 'ppb':
                return round(value, 2)
            return value
        
    except Exception as e:
        raise ValueError(f"Conversion error: {str(e)}")

def validate_units(parameter, units):
    """Validate requested units are supported"""
    valid_units = {
        'temperature': ['celsius', 'fahrenheit', 'kelvin'],
        'pressure': ['hpa', 'atm', 'mmhg'],
        'pollutant': ['ppm', 'ppb', 'µg/m³']
    }
    if parameter not in valid_units:
        raise ValueError(f"Invalid parameter. Must be one of: {list(valid_units.keys())}")
    if units.lower() not in valid_units[parameter]:
        raise ValueError(f"Invalid units for {parameter}. Must be one of: {valid_units[parameter]}")

@app.route('/temperature', methods=['POST'])
def get_temperature():
    """Temperature endpoint"""
    try:
        data = request.get_json()
        if not data or 'units' not in data:
            return jsonify({'error': 'Missing required parameter: units'}), 400
        
        units = data['units'].lower()
        validate_units('temperature', units)
        
        # Mock API call to third-party service
        config = THIRD_PARTY_APIS['temperature']
        response = requests.get(
            config['url'],
            params={'param': config['param_name']}
        )
        response.raise_for_status()
        
        # Get value in default unit from mock response
        original_value = response.json()['value']
        
        # Convert to requested units
        converted_value = convert_units(
            original_value,
            config['default_unit'],
            units,
            'temperature'
        )
        
        return jsonify({
            'parameter': 'temperature',
            'measured_value': converted_value,
            'units': units,
            'original_value': original_value,
            'original_units': config['default_unit']
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except requests.RequestException as e:
        return jsonify({'error': f'Temperature service error: {str(e)}'}), 502
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/pressure', methods=['POST'])
def get_pressure():
    """Pressure endpoint"""
    try:
        data = request.get_json()
        if not data or 'units' not in data:
            return jsonify({'error': 'Missing required parameter: units'}), 400
        
        units = data['units'].lower()
        validate_units('pressure', units)
        
        # Mock API call to third-party service
        config = THIRD_PARTY_APIS['pressure']
        response = requests.get(
            config['url'],
            params={'param': config['param_name']}
        )
        response.raise_for_status()
        
        # Get value in default unit from mock response
        original_value = response.json()['value']
        
        # Convert to requested units
        converted_value = convert_units(
            original_value,
            config['default_unit'],
            units,
            'pressure'
        )
        
        return jsonify({
            'parameter': 'pressure',
            'measured_value': converted_value,
            'units': units,
            'original_value': original_value,
            'original_units': config['default_unit']
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except requests.RequestException as e:
        return jsonify({'error': f'Pressure service error: {str(e)}'}), 502
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/pollutant', methods=['POST'])
def get_pollutant():
    """Pollutant endpoint"""
    try:
        data = request.get_json()
        if not data or 'units' not in data:
            return jsonify({'error': 'Missing required parameter: units'}), 400
        
        units = data['units'].lower()
        validate_units('pollutant', units)
        
        # Mock API call to third-party service
        config = THIRD_PARTY_APIS['pollutant']
        response = requests.get(
            config['url'],
            params={'param': config['param_name']}
        )
        # This will raise HTTPError for 4XX/5XX status codes
        response.raise_for_status()
        
        # Get value in default unit from mock response
        original_value = response.json()['value']
        
        # Convert to requested units
        converted_value = convert_units(
            original_value,
            config['default_unit'],
            units,
            'pollutant'
        )
        
        return jsonify({
            'parameter': 'pollutant',
            'measured_value': converted_value,
            'units': units,
            'original_value': original_value,
            'original_units': config['default_unit']
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Pollutant service error: {str(e)}'}), 502
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True)