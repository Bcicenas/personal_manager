from setuptools import find_packages, setup

setup(
	name='personal_manager',
	version='1.0.0',
	packages=find_packages(),
	include_package_data=True,
	install_requires=[
		'flask',
		'Flask-SQLAlchemy',
		'password_strength',
		'dateutils',
		'Flask-Mail',
		'Flask-WTF',
		'flask-paginate',
		'Flask-Babel',
		'email_validator'
	],
)
