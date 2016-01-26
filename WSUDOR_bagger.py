#!/usr/bin/env python

# WSUDOR_bagger script

import datetime
import hashlib
import md5
import os
import subprocess
import uuid

'''
OVERVIEW
	1) create temp directory with hash name
		- such that another won't exist already in that dir	
	2) move everything from that dir into temp directory
	3) rename temp dir to "/data"
	4) create files, eg.: 
		- bag-info.txt
			Bag-Software-Agent: bagit.py <http://github.com/libraryofcongress/bagit-python>
			Bagging-Date: 2016-01-26
			Collection PID: wayne:collectionDSJ
			Object PID: wayne:DSJv1i1DSJ19951119
			Payload-Oxum: 1514432709.194

		- bagit.txt
			BagIt-Version: 0.97
			Tag-File-Character-Encoding: UTF-8

		- manifest-md5.txt
			...
			5e04946e13e7d9b53f4b2b03de457f39  data/datastreams/vol01no01_19951119_05.pdf
			be58aa04bee4b2dfed9db9603d958465  data/datastreams/vol01no01_19951119_05.tif
			45479a182ae8b3bc3c41b55bb18efb38  data/datastreams/vol01no01_19951119_05.xml
			...

		- tagmanifest-md5.txt
			2a92e9c09542c14e9b2ccf753de4323a manifest-md5.txt
			9e5ad981e0d29adc278f6a294b8c2aca bagit.txt
			11cc77346c7bca0a7b369e46a7da4275 bag-info.txt

TO-DO
	- include logging
	- include command line arg parsing
	- error checking
	- rollback?
'''


def make_bag(d,metadata,skip_manifests=False):
	'''
	requires d - string of directory
	accepts metadata - dictionary of elements: values for bag-info.txt
	'''

	# strip tailing slash
	if d.endswith('/'):
		d = d[:-1]

	# 1) create temp data dir
	temp_data_dir = str(uuid.uuid4())+"_WSUDOR_temp_data_dir"
	os.mkdir("/".join( [d,temp_data_dir] ))

	# 2) move content to temp data dir
	os.system( 'mv %s/* %s/%s/' % (d,d,temp_data_dir) )
	os.system( 'mv %s/.* %s/%s/' % (d,d,temp_data_dir) )

	# 3) rename temp data dir
	os.rename( "/".join( [d,temp_data_dir] ), "/".join( [d,"data"] ))

	# 4) write metadata files		
	write_baginfo(d,metadata)
	write_bagit(d)
	write_manifest(d,skip_manifests)
	write_tagmanifest(d)

	# 5) cleanup and finish
	return True


## HELPERES #########

# write bag-info.txt
def write_baginfo(d,metadata):

	with open("%s/bag-info.txt" % d,'w') as fhand:
		
		# base lines
		lines = [
			"Bag-Software-Agent: WSUDOR_bagger",
			"Bagging-Date: %s" % datetime.datetime.today().strftime('%m-%d-%Y'),			
			"Payload-Oxum: %i" % get_size(d),
		]
		
		# include metadata lines
		for entry in metadata:
			lines.append("%s: %s" % (entry,metadata[entry]))

		fhand.writelines([line+"\n" for line in lines])


# write bagit.txt
def write_bagit(d):

	with open("%s/bagit.txt" % d,'w') as fhand:
		
		# base lines
		lines = [
			"BagIt-Version: 0.97",
			"Tag-File-Character-Encoding: UTF-8"
		]

		fhand.writelines([line+"\n" for line in lines])
		


# write manifest-md5.txt
def write_manifest(d,skip_manifests):

	with open("%s/manifest-md5.txt" % d,'w') as fhand:
		
		# base lines
		lines = []
		
		# iterate through files, gen hash
		files = _walk(d)

		if skip_manifests == True:
			for f in files:
				f_hash = "Null"
				print f,"--->",f_hash
				lines.append("%s  %s" % (f_hash,f))
		else:
			for f in files:
				f_hash = md5(f)
				print f,"--->",f_hash
				lines.append("%s  %s" % (f_hash,f))

		fhand.writelines([line+"\n" for line in lines])


# write tagmanifest-md5.txt
def write_tagmanifest(d):

	with open("%s/tagmanifest-md5.txt" % d,'w') as fhand:
		
		# base lines
		lines = []
		
		# iterate through files, gen hash
		dirpath, dirnames, filenames = os.walk(d).next()		
		for f in filenames:			
			f_hash = md5(os.path.join(d,f))
			lines.append("%s  %s" % (f_hash,f))

		fhand.writelines([line+"\n" for line in lines])


# handy size generator
# http://stackoverflow.com/questions/1392413/calculating-a-directory-size-using-python
def get_size(start_path = '.'):
	total_size = 0
	for dirpath, dirnames, filenames in os.walk(start_path):
		for f in filenames:
			fp = os.path.join(dirpath, f)
			total_size += os.path.getsize(fp)
	return total_size


# nice walk function from LOC bagit.py
# https://github.com/LibraryOfCongress/bagit-python/blob/master/bagit.py
def _walk(data_dir):
	for dirpath, dirnames, filenames in os.walk(data_dir):
		# if we don't sort here the order of entries is non-deterministic
		# which makes it hard to test the fixity of tagmanifest-md5.txt
		filenames.sort()
		dirnames.sort()
		for fn in filenames:
			path = os.path.join(dirpath, fn)
			# BagIt spec requires manifest to always use '/' as path separator
			if os.path.sep != '/':
				parts = path.split(os.path.sep)
				path = '/'.join(parts)
			yield path

# gen md5
# http://stackoverflow.com/questions/3431825/generating-a-md5-checksum-of-a-file
def md5(fname):
    hash = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash.update(chunk)
    return hash.hexdigest()


# main
if __name__ == '__main__':
	make_bag()


	
