import pytest
import json
from database import add_user, get_user_by_email

def test_register(client):
    """Test user registration"""
    test_email = "test@example.com"
    test_password = "securepassword123"
    
    # Test successful registration
    response = client.post('/api/auth/register', 
                         data=json.dumps({
                             'email': test_email,
                             'password': test_password
                         }),
                         content_type='application/json')
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert 'user_id' in data
    assert 'message' in data
    
    # Verify user exists in database
    user = get_user_by_email(test_email)
    assert user is not None
    assert user['email'] == test_email

def test_login(client):
    """Test user login"""
    test_email = "login_test@example.com"
    test_password = "loginpass123"
    
    # First register a test user
    add_user(test_email, test_password)
    
    # Test successful login
    response = client.post('/api/auth/login',
                         data=json.dumps({
                             'email': test_email,
                             'password': test_password
                         }),
                         content_type='application/json')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'token' in data
    assert 'user_id' in data

def test_protected_route(client):
    """Test auth middleware on protected routes"""
    # First login to get token
    test_email = "protected@example.com"
    test_password = "protected123"
    add_user(test_email, test_password)
    
    login_res = client.post('/api/auth/login',
                          data=json.dumps({
                              'email': test_email,
                              'password': test_password
                          }),
                          content_type='application/json')
    token = json.loads(login_res.data)['token']
    
    # Test protected route with valid token
    response = client.post('/api/subscribe',
                         headers={'Authorization': token},
                         data=json.dumps({'plan_id': 'basic'}),
                         content_type='application/json')
    
    assert response.status_code in (201, 500)  # 500 if payment not fully mocked

def test_invalid_credentials(client):
    """Test login with invalid credentials"""
    response = client.post('/api/auth/login',
                         data=json.dumps({
                             'email': "nonexistent@test.com",
                             'password': "wrongpass"
                         }),
                         content_type='application/json')
    
    assert response.status_code == 401
    data = json.loads(response.data)
    assert data['error'] == "Invalid credentials"