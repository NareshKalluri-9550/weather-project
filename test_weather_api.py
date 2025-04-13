import pytest
from app import app, convert_units, validate_units
from unittest.mock import patch, MagicMock
import json
import requests

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_validate_units():
    # Test valid units
    validate_units('temperature', 'celsius')
    validate_units('temperature', 'fahrenheit')
    validate_units('temperature', 'kelvin')
    validate_units('pressure', 'hpa')
    validate_units('pressure', 'atm')
    validate_units('pressure', 'mmhg')
    validate_units('pollutant', 'ppm')
    validate_units('pollutant', 'ppb')
    validate_units('pollutant', 'µg/m³')
    
    # Test invalid units
    with pytest.raises(ValueError) as excinfo:
        validate_units('temperature', 'invalid')
    assert "Invalid units for temperature" in str(excinfo.value)
    
    with pytest.raises(ValueError) as excinfo:
        validate_units('pressure', 'invalid')
    assert "Invalid units for pressure" in str(excinfo.value)
    
    with pytest.raises(ValueError) as excinfo:
        validate_units('pollutant', 'invalid')
    assert "Invalid units for pollutant" in str(excinfo.value)
    
    # Test invalid parameter
    with pytest.raises(ValueError) as excinfo:
        validate_units('invalid', 'celsius')
    assert "Invalid parameter" in str(excinfo.value)

def test_temperature_conversion():
    assert convert_units(273.15, 'kelvin', 'celsius', 'temperature') == 0
    assert convert_units(300, 'kelvin', 'fahrenheit', 'temperature') == pytest.approx(80.33, 0.01)
    assert convert_units(300, 'kelvin', 'kelvin', 'temperature') == 300
    
    assert convert_units(0, 'celsius', 'kelvin', 'temperature') == 273.15
    assert convert_units(100, 'celsius', 'fahrenheit', 'temperature') == 212
    assert convert_units(25, 'celsius', 'celsius', 'temperature') == 25
    
    assert convert_units(32, 'fahrenheit', 'celsius', 'temperature') == 0
    assert convert_units(212, 'fahrenheit', 'kelvin', 'temperature') == pytest.approx(373.15, 0.01)
    assert convert_units(50, 'fahrenheit', 'fahrenheit', 'temperature') == 50

def test_pressure_conversion():
    assert convert_units(1013.25, 'hpa', 'atm', 'pressure') == pytest.approx(1, 0.001)
    assert convert_units(1013.25, 'hpa', 'mmhg', 'pressure') == pytest.approx(760, 0.1)
    assert convert_units(1000, 'hpa', 'hpa', 'pressure') == 1000
    
    assert convert_units(1, 'atm', 'hpa', 'pressure') == pytest.approx(1013.25, 0.01)
    assert convert_units(1, 'atm', 'mmhg', 'pressure') == 760
    assert convert_units(1, 'atm', 'atm', 'pressure') == 1
    
    assert convert_units(760, 'mmhg', 'hpa', 'pressure') == pytest.approx(1013.25, 0.1)
    assert convert_units(760, 'mmhg', 'atm', 'pressure') == 1
    assert convert_units(700, 'mmhg', 'mmhg', 'pressure') == 700

def test_pollutant_conversion():
    assert convert_units(1, 'ppm', 'ppb', 'pollutant') == 1000
    assert convert_units(1, 'ppm', 'µg/m³', 'pollutant') == 1000
    assert convert_units(1, 'ppm', 'ppm', 'pollutant') == 1
    
    assert convert_units(1000, 'ppb', 'ppm', 'pollutant') == 1
    assert convert_units(1000, 'ppb', 'µg/m³', 'pollutant') == 1000
    assert convert_units(500, 'ppb', 'ppb', 'pollutant') == 500
    
    assert convert_units(1000, 'µg/m³', 'ppm', 'pollutant') == 1
    assert convert_units(1000, 'µg/m³', 'ppb', 'pollutant') == 1000
    assert convert_units(500, 'µg/m³', 'µg/m³', 'pollutant') == 500

@patch('requests.get')
def test_temperature_endpoint(mock_get, client):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'value': 293.15}  # 20°C in Kelvin
    mock_get.return_value = mock_response
    
    response = client.post(
        '/temperature',
        json={'units': 'celsius'}
    )
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert data['parameter'] == 'temperature'
    assert data['measured_value'] == 20
    assert data['units'] == 'celsius'
    assert data['original_value'] == 293.15
    assert data['original_units'] == 'kelvin'

@patch('requests.get')
def test_pressure_endpoint(mock_get, client):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'value': 1013.25}  # 1 atm in hPa
    mock_get.return_value = mock_response
    
    response = client.post(
        '/pressure',
        json={'units': 'atm'}
    )
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert data['parameter'] == 'pressure'
    assert data['measured_value'] == pytest.approx(1, 0.001)
    assert data['units'] == 'atm'
    assert data['original_value'] == 1013.25
    assert data['original_units'] == 'hpa'

@patch('requests.get')
def test_pollutant_endpoint(mock_get, client):
    # Test successful case
    success_mock = MagicMock()
    success_mock.status_code = 200
    success_mock.json.return_value = {'value': 1}  # 1 ppm
    success_mock.raise_for_status.return_value = None
    
    # Test error case
    error_mock = MagicMock()
    error_mock.status_code = 500
    error_mock.raise_for_status.side_effect = requests.exceptions.HTTPError("500 Server Error")
    
    # First test successful response
    mock_get.return_value = success_mock
    response = client.post(
        '/pollutant',
        json={'units': 'ppb'}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['measured_value'] == 1000
    
    # Then test error response
    mock_get.return_value = error_mock
    response = client.post(
        '/pollutant',
        json={'units': 'ppb'}
    )
    assert response.status_code == 502
    error_data = json.loads(response.data)
    assert 'Pollutant service error' in error_data['error']