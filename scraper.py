import scraperwiki
from bs4 import BeautifulSoup # BeautifulSoup helps you to find what you want in HTML

url = "http://catphotos.org/" # loading your url from the csv/database
html = scraperwiki.scrape(url) # download the html content of the page
#html = ""
soup = BeautifulSoup(html) # load the html into beautifulsoup

catphotos = [] # start with an empty list
for photothumb in soup.find_all(class_ = "photo-thumb"): # for each thumbnail...
    url = photothumb.h2.a['href'] # find the photo page link
    image_url = photothumb.a.img['src'] # find the image URL
    caption = photothumb.h2.a['title'] # find the caption.
    catphotos.append({"url": url, "image_url": image_url, "caption": caption}) # put the values extracted into a list

scraperwiki.sqlite.save(unique_keys=["url"], data=catphotos) # save the list of cat photos and captions

# CKAN Integration
import os
if 'MORPH_CKAN_URL' in os.environ and 'MORPH_CKAN_API_KEY' in os.environ:
    ckan_url = os.environ['MORPH_CKAN_URL'] # http://demo.ckan.org can be used to test API usage
    ckan_apikey = os.environ['MORPH_CKAN_API_KEY']
    ckan_resourceid = '417a1ea4-16e7-4fd4-a435-2c14ce7c032b' # cat-photos on data.disclosurelo.gs
    ckan_records = catphotos

    ''' #ckanapi is a wrapper around the REST API, if you need to use many actions can be easier to write
    import ckanapi # download from https://github.com/ckan/ckanapi and include in your scraper repo
    ckan = ckanapi.RemoteCKAN(os.environ['MORPH_CKAN_URL'], apikey=os.environ['MORPH_CKAN_API_KEY'])
    try:
        # pkg = ckan.action.package_create(name='cat-photos', title='Cat Photos') # create a new dataset?
	# resource = ckan.action.datastore_create(resource={"package_id":'cat-photos'},
			fields=[{"id":"url","type":"text"},{"id":"image_url","type":"text"},{"id":"caption","type":"text"}]) # create a new data resource?
	# ckan.action.datastore_upsert(resource_id=resource.resource_id, records= catphotos, method="insert") # insert data if not duplicate
    except ckanapi.NotAuthorized:
        print 'Access denied, check your CKAN API Key is correct" 
    '''

    # or if you are just doing datastore updates, you can just use HTTP and JSON directly.
    import requests
    import json
    datastore_action_url = ckan_url + "/api/3/action/datastore_upsert";
    datastore_action_body = json.dumps({"resource_id": ckan_resourceid, "records": ckan_records, "method": "insert"})
    #print datastore_action_body
    r = requests.post(datastore_action_url, data=datastore_action_body, headers={'Authorization': ckan_apikey, 'content-type': 'application/json'})
    if r.status_code != 200:
	print r.json()
	r.raise_for_status() # if there are any errors, raise an exception


