from personal_manager import create_app

def test_config():
	# assert not create_app('testing').testing
	assert create_app('testing').testing
