import pytest

def test_personal_details(client, auth):
	auth.login()
	response = client.get('/users/personal_details', follow_redirects=True)
	print(response.data)
	assert b'User details' in response.data
	assert b'Username: admin' in response.data
	assert b'Email: admin@email.com' in response.data