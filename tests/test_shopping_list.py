import pytest

def test_list(client, auth):
	auth.login()
	response = client.get('/shopping_lists/list')
	assert b"Shopping Lists" in response.data


@pytest.mark.parametrize('path', (
	'/shopping_lists/list',
	'/shopping_lists/shopping_items/1'
))
def test_login_required_get(client, path):
	response = client.get(path)
	assert response.headers["Location"] == "/auth/login"

@pytest.mark.parametrize('path', (
	'/shopping_lists/create',
	'/shopping_lists/update/1',
	'/shopping_lists/delete/1',
	'/shopping_lists/create_shopping_list_item/1',
	'/shopping_lists/delete_shopping_list_item/1'
))

def test_login_required_post(client, path):
	response = client.post(path)
	assert response.headers["Location"] == "/auth/login"

def test_shopping_list_create(client, auth):
	auth.login()
	assert client.get('/shopping_lists/create').status_code == 200
	response = client.post(
		'/shopping_lists/create', data={'name': 'test'}
	)

	assert response.headers["Location"] == '/shopping_lists/list'
	response = client.get('/shopping_lists/list', follow_redirects=True)
	assert b'Shopping List was successfully created' in response.data

def test_shopping_list_update(client, auth):
	auth.login()
	assert client.get('/shopping_lists/update/1').status_code == 200
	response = client.post(
		'/shopping_lists/update/1', data={'name': 'test_updated'}
	)

	assert response.headers["Location"] == '/shopping_lists/list'
	response = client.get('/shopping_lists/list', follow_redirects=True)
	assert b'Shopping List was successfully updated' in response.data


@pytest.mark.parametrize('path', (
	'/shopping_lists/create',
	'/shopping_lists/update/1'
))
def test_create_update_validate(client, auth, path):
	auth.login()
	response = client.post(path, data={'name': ''})
	assert b'Name is required.' in response.data

def test_create_shopping_item(client, auth):
	auth.login()
	assert client.get('/shopping_lists/shopping_items/1').status_code == 200
	response = client.post(
		'/shopping_lists/create_shopping_list_item/1', data={'name': 'item'}
	)

	assert response.headers["Location"] == '/shopping_lists/shopping_items/1'
	response = client.get('/shopping_lists/shopping_items/1', follow_redirects=True)
	assert b'Shopping Item was successfully created' in response.data

def test_delete_shopping_item(client, auth):
	auth.login()
	response = client.post('/shopping_lists/delete_shopping_list_item/1', data={'shopping_list_id': 1})

	assert response.headers["Location"] == '/shopping_lists/shopping_items/1'
	response = client.get('/shopping_lists/shopping_items/1', follow_redirects=True)
	assert b'Shopping Item was successfully deleted' in response.data

def test_delete_shopping_item_not_found(client, auth):
	auth.login()
	response = client.post('/shopping_lists/delete_shopping_list_item/1')
	assert b"Shopping item id 1 doesn&#39;t exist." in response.data


def test_shopping_list_delete(client, auth):
	auth.login()
	response = client.post('/shopping_lists/delete/1')

	assert response.headers["Location"] == '/shopping_lists/list'
	response = client.get('/shopping_lists/list', follow_redirects=True)
	assert b'Shopping List was successfully deleted' in response.data
