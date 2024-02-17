import xml.etree.ElementTree as ET

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
	
	print(f"\nItem Title: {item_title}")
	print(f"Item Link: {item_link}")
	print(f"Item Description: {item_description}")
