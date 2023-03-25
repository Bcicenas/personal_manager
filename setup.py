from setuptools import find_packages, setup

setup(
	name='personal_manager',
	version='1.0.0',
	packages=find_packages(),
	include_package_data=True,
	install_requires=[
		'flask==2.2.3',
		'Flask-SQLAlchemy==3.0.3',
		'mysqlclient==2.1.1',
		'password_strength==0.0.3.post2',
		'dateutils==0.6.12',
		'Flask-Mail==0.9.1',
		'Flask-WTF==1.1.1',
		'flask-paginate==2022.1.8',
		'Flask-Babel==3.0.1',
		'email_validator==1.3.1',
		'python-dotenv==1.0.0',
		'pytest-dotenv==0.5.2',
		'Flask-Alembic==2.0.1'
	],
)
