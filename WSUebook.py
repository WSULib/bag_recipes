# local
from objMetaClass import ObjMeta

# lib
import os
import sys
import md5
import bagit
import WSUDOR_bagger
import requests
import json
import xmltodict
from lxml import etree
import re


def main():

	# check for output dir
	if not os.path.exists(output_dir):
		os.mkdir(output_dir)

	# iterate through dir
	for each in [d for d in os.listdir(input_dir) if os.path.isdir("/".join([input_dir,d])) ]:

		# run
		try:
			createBag( "/".join([input_dir,each]) )
		except:
			print "Skipping / Fail",each


def createBag(d):
	
	print "working on",d

	# find MODS
	MODS = [f for f in os.listdir(d) if f.startswith("DSJ") and f.endswith(".xml")][0]
	print "MODS file:",MODS
	MODS_tree = etree.parse("/".join([d,MODS]))
	MODS_root = MODS_tree.getroot()
	ns = MODS_root.nsmap
	MODS_proper = MODS_root.xpath('//mods:mods', namespaces=ns)[0]

	# get identifier
	identifier = MODS_proper.xpath('//mods:identifier[@type="local"]', namespaces=ns)[0].text
	print "identifier:",identifier

	# get volume / issue
	volume = MODS_proper.xpath('//mods:detail[@type="volume"]/mods:number', namespaces=ns)[0].text
	issue = MODS_proper.xpath('//mods:detail[@type="issue"]/mods:number', namespaces=ns)[0].text

	# gen full identifier
	full_identifier = "DSJv" + volume + "i" + issue + identifier
	print full_identifier

	# generate PID
	PID = "wayne:%s" % (full_identifier)
	print "PID:",PID

	# - create object directory
	obj_dir = "{output_dir}/{PID}".format(output_dir=output_dir, PID=PID)
	os.mkdir(obj_dir)
	os.mkdir(obj_dir+"/datastreams")

	# - export MODS.xml	
	MODS_string = etree.tostring(MODS_proper)
	fhand = open("{obj_dir}/MODS.xml".format(obj_dir=obj_dir),"w")
	fhand.write(MODS_string)
	fhand.close()

	# get title for DSJ
	book_title = MODS_proper.xpath('mods:titleInfo/mods:title',namespaces=ns)[0].text
	book_sub_title = MODS_proper.xpath('mods:titleInfo/mods:subTitle',namespaces=ns)[0].text
	full_title = " ".join([book_title,book_sub_title])
	print "full title:",full_title
	

	# instantiate object with quick variables
	known_values = {
		"id":"wayne:"+full_identifier,
		"identifier":full_identifier,
		"label":full_title,
		"content_type":"WSUDOR_WSUebook",
		"image_filetype":"tif"
	}

	# instantiate ObjMeta object
	om_handle = ObjMeta(**known_values)	

	# show relationships
	om_handle.object_relationships = [				
		{
			"predicate": "info:fedora/fedora-system:def/relations-external#isMemberOfCollection",
			"object": "info:fedora/wayne:collection"+collection_name
		},
		{
			"predicate": "info:fedora/fedora-system:def/relations-external#isMemberOfCollection",
			"object": "info:fedora/wayne:collectionWSUebooks"
		},
		{
			"predicate": "http://digital.library.wayne.edu/fedora/objects/wayne:WSUDOR-Fedora-Relations/datastreams/RELATIONS/content/isDiscoverable",
			"object": "info:fedora/True"
		},
		{
			"predicate": "http://digital.library.wayne.edu/fedora/objects/wayne:WSUDOR-Fedora-Relations/datastreams/RELATIONS/content/preferredContentModel",
			"object": "info:fedora/CM:WSUebook"
		},
		{
			"predicate": "http://digital.library.wayne.edu/fedora/objects/wayne:WSUDOR-Fedora-Relations/datastreams/RELATIONS/content/hasSecurityPolicy",
			"object": "info:fedora/wayne:WSUDORSecurity-permit-apia-unrestricted"
		}		
	]


	# iterate through SORTED binaries and create symlinks and write to objMeta		
	print "creating symlinks and writing to objMeta for",d
	binary_files = [ binary for binary in os.listdir(d) if not binary.startswith('DSJ') ]
	binary_files.sort() #sort
	for ebook_binary in binary_files:

		# skip some undesirables
		if ebook_binary == ".DS_Store" or ebook_binary.endswith('bak'):
			continue

		# write symlink
		source = "/".join([ d, ebook_binary ])
		symlink = "/".join([ obj_dir,"datastreams",ebook_binary ])
		os.symlink(source, symlink)		

		# get mimetype of file
		filetype_hash = {
			'tif': ('image/tiff','IMAGE'),
			'jpg': ('image/jpeg','IMAGE'),
			'png': ('image/png','IMAGE'),
			'xml': ('text/xml','ALTOXML'),
			'html': ('text/html','HTML'),
			'htm': ('text/html','HTML'),
			'pdf': ('application/pdf','PDF')
		}
		filetype_tuple = filetype_hash[ebook_binary.split(".")[-1]] 			
		page_num = ebook_binary.split(".")[0].split("_")[2].lstrip('0')

		# write to datastreams list		
		ds_dict = {
			"filename":ebook_binary,
			"ds_id":filetype_tuple[1]+"_"+page_num,
			"mimetype":filetype_tuple[0], # generate dynamically based on file extension
			"label":filetype_tuple[1]+"_"+page_num,
			"internal_relationships":{},
			'order':page_num			
		}
		om_handle.datastreams.append(ds_dict)

		# set isRepresentedBy relationsihp
		if page_num == "1" and filetype_tuple[1] == 'IMAGE':
			om_handle.isRepresentedBy = ds_dict['ds_id']

	
	# write to objMeta.json file 
	om_handle.writeToFile("{obj_dir}/objMeta.json".format(obj_dir=obj_dir))

	# finally, BagIt-ify the directory
	print "creating bag..."
	# LOC bagit.py
	# bag = bagit.make_bag("{obj_dir}".format(obj_dir=obj_dir),{
	# 	'Collection PID' : "wayne:collection"+collection_name,
	# 	'Object PID' : PID
	# })
	# local WSUDOR bagger
	bag = WSUDOR_bagger.make_bag("{obj_dir}".format(obj_dir=obj_dir),{
		'Collection PID' : "wayne:collection"+collection_name,
		'Object PID' : PID
	})	



if __name__ == '__main__':
	run_msg = '''
	This script requires the following arguments:
		- location of bags 
		- destination for bags
		- collection name (without prefix)		
	'''
	if len(sys.argv) < 4:
		print run_msg
	else:
		input_dir = sys.argv[1]
		output_dir = sys.argv[2]
		collection_name = sys.argv[3]		

		main()

