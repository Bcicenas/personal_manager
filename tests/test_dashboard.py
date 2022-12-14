import pytest

def test_index(client, auth):
	response = client.get('/', follow_redirects=True)
	assert b"Login" in response.data
	assert b"Register" in response.data
	assert b"Simple web application to manage your tasks, shoppings lists and more" in response.data

	auth.login()
	response = client.get('/', follow_redirects=True)
	assert b'Dashboard' in response.data
	assert b'Shopping Lists' in response.data
	assert b'test_primary' in response.data
	assert b'item1' in response.data
	assert b'task1' in response.data
	