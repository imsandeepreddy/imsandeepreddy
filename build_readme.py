from imgurpython.helpers.error import ImgurClientError
from imgurpython import ImgurClient
import requests
import pathlib
import random
import json
import sys
import re
import os

# https://help.medium.com/hc/en-us/articles/214874118-RSS-feeds

root = pathlib.Path(__file__).parent.resolve()

def replace_chunk(content, marker, chunk, inline=False):
	# build the regular expression pattern, DOTALL will match any character, including a newline
	r = re.compile(
		r"<!-- {} starts -->.*<!-- {} ends -->".format(marker, marker),
		re.DOTALL,
	)
	# add newline before and after
	if not inline:
		chunk = "\n{}\n".format(chunk)
	# build the final chunk by adding comments before and after the chunk
	chunk = "<!-- {} starts -->{}<!-- {} ends -->".format(marker, chunk, marker)
	# replace matched string using pattern provided with the chunk
	return r.sub(chunk, content)

def fetch_blog_posts(link):
	result = []
	response = requests.get(link)
	if response.status_code == 200:
		posts = json.loads(response.text)["items"]
		for post in posts:
			# skip the comments
			if len(post["categories"]) != 0:
				post["pubDate"] = post["pubDate"].split()[0]
				result.append(post)
	elif response.status_code == 404:
		print('Not Found: ') + link
	return result

if __name__ == "__main__":
	readme = root / "README.md"

	readme_contents = readme.open().read()
	rewritten = readme_contents

	posts = fetch_blog_posts("https://api.rss2json.com/v1/api.json?rss_url=https://medium.com/feed/@imsandeepreddy")
	if len(posts) != 0:
		# markdown formatting
		posts_md = "\n".join(
			["* [{title}]({link}) <br/> <sub>{pubDate}</sub>".format(**post) for post in posts]
		)

		rewritten = replace_chunk(rewritten, "blog", posts_md)

	readme.open("w").write(rewritten)
