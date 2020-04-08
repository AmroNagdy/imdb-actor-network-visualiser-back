import gzip
import requests
import io
import csv

base_url = 'https://datasets.imdbws.com/'

title_basics = 'title.basics.tsv.gz'
title_ratings = 'title.ratings.tsv.gz'
title_principals = 'title.principals.tsv.gz'
name_basics = 'name.basics.tsv.gz'

output_file_name = '../actor_relationships.json'

# Collect movie tconsts from title_basics
movie_tconsts = {}
response = requests.get(base_url+title_basics, stream=True)
content = gzip.decompress(response.content)
split_content = content.splitlines()

for line in split_content:
    split_line = line.decode('utf-8').split('\t')
    print(split_line)
