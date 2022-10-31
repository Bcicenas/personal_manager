import pytest

def test_personal_details(client, auth):
	auth.login()
	response = client.get('/users/personal_details', follow_redirects=True)
	print(response.data)
	assert b'User details' in response.data
	assert b'Username: admin' in response.data
	assert b'Email: admin@email.com' in response.data

@pytest.mark.parametrize(('current_password', 'new_password', 'confirm_new_passord', 'message'), (
	('', 'test', 'test', b'Current Password is required.'),
	('test', '', 'test', b'New Password is required.'),
	('test', 'test', '', b'Confirm New Password is required.'),
	('test', 'test', 'test', b'Current Password is invalid'),
	('A@sdas123_', 'test', 'test1', b'Password mismatch'),
	('A@sdas123_', 'test', 'test', b'Please choose a stronger password.')
))
def test_change_password_validate_input(client, auth, current_password, new_password, confirm_new_passord, message):
	auth.login()
	response = client.post('/users/change_password', 
			data={'current_password': current_password, 'new_password': new_password, 'confirm_new_passord': confirm_new_passord})
	assert message in response.data

def test_change_password(client, auth):
	auth.login()
	response = client.post('/users/change_password', 
			data={'current_password': 'A@sdas123_', 'new_password': 'A@sdas123_5', 'confirm_new_passord': 'A@sdas123_5'})
	response = client.get('/users/personal_details', follow_redirects=True)
	assert b'Password was successfully changed' in response.data

def test_delete_account(client, auth):
	auth.login(password='A@sdas123_5')
	response = client.post('/users/delete_account')

	assert response.headers["Location"] == '/'
	response = client.get('/', follow_redirects=True)
	assert b'Account was successfully deleted' in response.data
