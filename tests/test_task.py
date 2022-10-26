import pytest

def test_list(client, auth):
	auth.login()
	response = client.get('/tasks/list')
	assert b"Tasks" in response.data

@pytest.mark.parametrize('path', (
	'/tasks/list',
))
def test_login_required_get(client, path):
	response = client.get(path)
	assert response.headers["Location"] == "/auth/login"

@pytest.mark.parametrize('path', (
	'/tasks/create',
	'/tasks/update/1',
	'/tasks/delete/1'
))
def test_login_required_post(client, path):
	response = client.post(path)
	assert response.headers["Location"] == "/auth/login"

def test_task_create(client, auth):
	auth.login()
	assert client.get('/tasks/create').status_code == 200
	response = client.post(
		'/tasks/create', data={'name': 'test2', 'description': 'test description', 'priority': 0, 'till_date': '2022-10-28', 'finished': 1}
	)

	assert response.headers["Location"] == '/tasks/list'
	response = client.get('/tasks/list', follow_redirects=True)
	assert b'Task was successfully created' in response.data

def test_task_update(client, auth):
	auth.login()
	assert client.get('/tasks/update/1').status_code == 200
	response = client.post(
		'/tasks/update/1', data={'name': 'test_updated'}
	)

	assert response.headers["Location"] == '/tasks/list'
	response = client.get('/tasks/list', follow_redirects=True)
	assert b'Task was successfully updated' in response.data

@pytest.mark.parametrize('path', (
	'/tasks/create',
	'/tasks/update/1'
))
def test_create_update_validate(client, auth, path):
	auth.login()
	response = client.post(path, data={'name': ''})
	assert b'Name is required.' in response.data

def test_delete(client, auth):
	auth.login()
	response = client.post('/tasks/delete/1')

	assert response.headers["Location"] == '/tasks/list'
	response = client.get('/shopping_lists/list', follow_redirects=True)
	assert b'Task was successfully deleted' in response.data

def test_delete_not_found(client, auth):
	auth.login()
	response = client.post('/tasks/delete/1')
	assert b'Task id 1 doesn&#39;t exist.' in response.data

