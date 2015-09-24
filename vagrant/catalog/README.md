# Catalog project

## Getting started
### Delete the existing SQlite database if it exists
```
rm -f /tmp/catalog.db
```
### Install SQLAlchemy
```
sudo pip install flask-sqlalchemy
```
### Create sample data
```
cd /vagrant/catalog
python
import application
application.create_sample_data()
exit()
```
### Run the application
```
python application.py
```
### Use the application
* Visit http://localhost:5000
* Click through the categories to see the sample items
* Click the sample items to see more detail
* Log in with your GitHub account
* Add one or more items
* Edit one or more of your items
* Visit http://localhost:5000/catalog.json to get a JSON dump of all the items
