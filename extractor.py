import xml.etree.ElementTree as ET
from datetime import datetime

# Load the RSS feed XML file
filename = "/Users/benwheatley/Downloads/Exported ks-wp blog/kitsunesoftware.wordpress.com-2023-12-04-15_56_29/kitsunesoftware.wordpress.2023-12-04.000.xml"
tree = ET.parse(filename)
root = tree.getroot()

# Accessing channel information
channel = root.find('channel')
title = channel.find('title').text
description = channel.find('description').text

print(f"Feed Title: {title}")
print(f"Feed Description: {description}")

# Accessing and printing information for each item
for item in channel.findall('item'):
	item_title = item.find('title').text
	item_link = item.find('link').text
	item_description = item.find('description').text
	
	# Accessing <content:encoded> (CDATA)
	content_encoded = item.find('.//content:encoded', namespaces={'content': 'http://purl.org/rss/1.0/modules/content/'})
	
	# Extracting content inside CDATA
	if content_encoded is not None and content_encoded.text is not None:
		content = content_encoded.text
	else:
		content = None
	
	# Extracting post date from <pubDate>
	pub_date_element = item.find('pubDate')
	if pub_date_element is not None and pub_date_element.text is not None:
		post_date_object = datetime.strptime(pub_date_element.text, "%a, %d %b %Y %H:%M:%S %z")
		post_date_formatted = post_date_object.strftime("%Y/%m/%d")
		path = f"{post_date_formatted}.content"
	else:
		path = None
	
	print(f"\n---\nOutput:\n")
	print(f"<h1>{item_title}</h1>\n\n")
	print(f"Content Encoded: {content}")
	print(f"<a href=\"{item_link}\">Original post: {item_link}</a>")
	
	print(f"Output path: `{path}`")
