import pytest
from app import app, convert_units
from unittest.mock import patch
import json

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_temperature_conversion():
    """Test temperature unit conversions with proper rounding"""
    assert convert_units(300, 'kelvin', 'celsius') == pytest.approx(26.85, abs=1e-2)
    assert convert_units(300, 'kelvin', 'fahrenheit') == pytest.approx(80.33, abs=1e-2)

def test_pressure_conversion():
    """Test pressure unit conversions"""
    assert convert_units(1013, 'hpa', 'atm') == pytest.approx(1.0, 0.001)

@patch('app.requests.get')
def test_get_temperature(mock_get, client):
    """Test temperature endpoint"""
    # Mock response
    mock_get.return_value.json.return_value = {'value': 300}
    mock_get.return_value.status_code = 200
    
    response = client.post(
        '/weather/temperature',
        json={'city': 'London', 'units': 'Celsius'}
    )
    assert response.status_code == 200
    assert response.json['temperature'] == 26.85
    assert response.json['units'] == 'celsius'

@patch('app.requests.get')
def test_get_pressure(mock_get, client):
    """Test pressure endpoint"""
    # Mock response
    mock_get.return_value.json.return_value = {'value': 1013}
    mock_get.return_value.status_code = 200
    
    response = client.post(
        '/weather/pressure',
        json={'city': 'London', 'units': 'atm'}
    )
    assert response.status_code == 200
    assert response.json['pressure'] == pytest.approx(1.0, 0.001)
    assert response.json['units'] == 'atm'

def test_invalid_city(client):
    """Test missing city parameter"""
    response = client.post(
        '/weather/temperature',
        json={'units': 'Celsius'}  # Missing city
    )
    assert response.status_code == 400
    assert 'Missing required parameters' in response.json['error']

def test_invalid_units_for_temperature(client):
    """Test invalid temperature units"""
    response = client.post(
        '/weather/temperature',
        json={'city': 'London', 'units': 'Kelvin'}  # Invalid unit
    )
    assert response.status_code == 400
    assert 'Invalid units for temperature' in response.json['error']

def test_invalid_units_for_pressure(client):
    """Test invalid pressure units"""
    response = client.post(
        '/weather/pressure',
        json={'city': 'London', 'units': 'mmHg'}  # Invalid unit
    )
    assert response.status_code == 400
    assert 'Invalid units for pressure' in response.json['error']

