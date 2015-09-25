# Catalog project
## Intro
This is the catalog project from Udacity's Full Stack Web Developer Nanodegree

## Requirements
* python (2.x)
* python-pip

## Getting started
### Download the repo
```
git clone https://github.com/rahimnathwani/fullstack-nanodegree-vm
```

### Change to the app directory and install dependencies using pip:
```
cd fullstack-nanodegree-vm/vagrant/catalog
sudo pip install -r requirements.txt
```
### Delete the existing SQlite database if it exists
```
rm -f /tmp/catalog.db
```
### Create sample data
```
python create_sample_data.py
```
### Update the constants in application.py with your own values
```
GITHUB_CLIENT_ID = ''
GITHUB_CLIENT_SECRET = ''
OAUTH_REDIRECT_URI = "http://host:port/oauth_callback"
HOME_URI = "http://host:port/"
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
