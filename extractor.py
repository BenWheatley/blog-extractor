import xml.etree.ElementTree as ET
from datetime import datetime
import re
import sys
import os
import subprocess
import platform

# Load the RSS feed XML file
filename = "/Users/benwheatley/Downloads/Exported ks-wp blog/kitsunesoftware.wordpress.com-2023-12-04-15_56_29/kitsunesoftware.wordpress.2023-12-04.000.xml"
tree = ET.parse(filename)
root = tree.getroot()

root_url = "https://benwheatley.github.io/blog"
output_root = "/Users/benwheatley/Documents/Personal/Projects/Code/blog"
DEBUG = False

# Accessing channel information
channel = root.find('channel')
title = channel.find('title').text
description = channel.find('description').text

print(f"Feed Title: {title}")
print(f"Feed Description: {description}")

def remove_strings(source, to_remove):
	for s in to_remove:
		source = source.replace(s, "")
	return source


def remove_wp_image(source):
	pattern1 = re.compile(r' ?wp-image-\d+')
	result = re.sub(pattern1, '', source)
	
	pattern2 = re.compile(r'\n<!-- wp:image .* -->')
	result = re.sub(pattern2, '', result)
	
	return result

def format_linked_keyword_list(base_url, items):
	return ", ".join([f"<a href='{base_url}/{item}'>{item}</a>" for item in items])

def update_all_img_src(input_string):
	pattern = re.compile(r'<img src="https://kitsunesoftware\.files\.wordpress\.com/(\d{4}/\d{2}/[^"]+)"')
	return pattern.sub(fr'<img src="{root_url}/\1"', input_string)

def add_missing_p_tags(input_string):
	paragraphs = input_string.split('\n')
	output = ""
	for p in paragraphs:
		stripped = p.strip()
		if stripped.startswith("<") or len(stripped) == 0:
			output += p
		else:
			output += f"<p>{stripped}</p>"
		output += "\n"
	
	return output

def remove_wp_open_tag_comments_with_json(source):
	pattern = re.compile(r'<!--\s*wp:(\w+)\s+({[^}]+})\s*-->')
	return re.sub(pattern, "", source)

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
		content = remove_wp_image(content)
		content = remove_strings(content, ["<!-- wp:paragraph -->\n", "\n<!-- /wp:paragraph -->", 'wp-element-caption', 'wp-', 'class=""', "<!--more-->", "<!-- wp:page-list /-->", "\n<!-- /wp:image -->", "\n<p><!-- wp:paragraph --></p>", "<!-- wp:quote -->", "<!-- /wp:quote -->", "<!-- wp:heading -->", "<!-- wp:heading -->", "<!-- wp:table -->", "<!-- /wp:table -->", "p1", "s1", ' class=""', "<!-- wp:paragraph —&gt;-->", "<!-- wp:paragraph —&gt;-->", "<!-- /wp:paragraph -->", "<!-- wp:group -->", "<!-- /wp:group -->", "<!-- wp:columns -->", "<!-- /wp:columns -->", "<!-- /wp:column -->", "<!-- /wp:heading -->"])
		content = content.replace('&nbsp;', " ")
		content = update_all_img_src(content)
		content = remove_wp_open_tag_comments_with_json(content)
		content = add_missing_p_tags(content)
		content = content.replace("<p></p>", "")
	else:
		content = None
	
	# Extracting post date from <pubDate>
	pub_date_element = item.find('pubDate')
	if pub_date_element is not None and pub_date_element.text is not None:
		post_date_object = datetime.strptime(pub_date_element.text, "%a, %d %b %Y %H:%M:%S %z")
		post_date_formatted = post_date_object.strftime("%Y/%m/%d-%H.%M.%S.content")
		path = post_date_formatted
	else:
		path = None
	
	
	# Extracting categories and tags
	categories = []
	tags = []
	for category in item.findall('.//category'):
		domain = category.get('domain')
		name = category.text.strip()
		if domain == 'category':
			categories.append(name)
		elif domain == 'post_tag':
			tags.append(name)
	
	print(f"pub_date_element = {pub_date_element.text}")
	if content == None or path == None:
		sys.stderr.write(f"error with item at {pub_date_element.text}+ '\n'")
		continue
	
	output_lines = [
		f"<h1>{item_title}</h1>",
		content,
		f"<p><a href=\"{item_link}\">Original post: {item_link}</a></p>\n",
		f"<p>Original post timestamp: {pub_date_element.text}</a></p>\n"
	]
	
	if tags:
		tags_html = format_linked_keyword_list(f"{root_url}/tags", tags)
		output_lines.append(f"<p>Tags: {tags_html}</p>\n")
	
	if categories:
		categories_html = format_linked_keyword_list(f"{root_url}/categories", categories)
		output_lines.append(f"<p>Categories: {categories_html}</p>\n")
	
	output_string = '\n'.join(output_lines)
	path = f"{output_root}/{path}"
	
	if DEBUG:
		print(f"\n---\nOutput:\n")
		print(output_string)
		print(f"Output path: `{path}`")
	else:
		try:
			os.makedirs(os.path.dirname(path), exist_ok=True)
			with open(path, 'x') as file: file.write(output_string)
		except Exception as e:
			sys.stderr.write(f"An unexpected error occurred: {e}\n")
			sys.stderr.write(f"New content was going to be:\n\n{content}\n\n")
			if platform.system() == 'Darwin':
				subprocess.run(['open', '-R', path])
