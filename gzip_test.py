# -*- coding: utf-8 -*-
"""
Created on Tue May 29 21:35:04 2018

@author: tzhou
"""

import gzip

content = b'lots of content here'
with gzip.open('file.txt.gz', 'wb') as f:
    f.write(content)
    
with gzip.open('file.txt.gz', 'rb') as f:
    file_content = f.read()
    print(file_content)