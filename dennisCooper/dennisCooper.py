#!/usr/bin/python

from lxml import etree
import os
import re
import sys
from classes import ObjMeta
import signal
import time

#### 1) SETUP ####
# Set file
file = "/repository/ingest_workspace/dennis_cooper/CooperSlides_2.xml"
image_path = "images"
pwd = os.popen('pwd').read()
pwd = re.split('\n', pwd)[0]
image_path = pwd + "/" + image_path + "/"
# Load file into memory and find Object ID for first MODS object
tree = etree.parse(file)

# Establish namespaces
root = tree.getroot()
ns = root.nsmap
print ns

#### 2) IDENTIFY MAJOR CONTENT ####
# Wrap into a for loop that goes through and finds each MODS object one by one

collectionObj = "DennisCooper"
collectionPID = "wayne:collectionDennisCooper"

MODS = tree.xpath("//mods:mods", namespaces=ns)
for eachMODS in MODS:
    currentPID = eachMODS.findall("mods:identifier", namespaces=ns)[0].text
    # Make a directory
    path = "./"+currentPID+"/datastreams"
    try:
        os.makedirs(path)
    except OSError:
        print "Your directory, "+path+",is already created"

#### 3) SAVE MODS CHUNKS TO DISK ####
# Copy all that MODS XML (associated with CurrentPID) and save into a .xml file inside PID folder

    # Save as a MODS file aka save .tostring and add .xml declaration at the beginning of the file
    stringMODS = etree.tostring(eachMODS, pretty_print=True, xml_declaration=True, encoding='UTF-8')

    # Grab file name and copy file to PID folder
    try:
        fileName = "MODS.xml"
        MODSpath = "./"+currentPID+"/"
        filePath = os.path.join(MODSpath, fileName)
        with open(filePath, 'wb') as stream:
            stream.write(stringMODS)
    except OSError:
        print "File already exists"
        # raise

#### 4) PARSE MODS STRUCTURE FOR MANIFEST ####
    file_dictionary = {}
    currentFile = eachMODS.findall(".//mods:extension", namespaces=ns)
    for each in currentFile:
        for element in each.iter():
            if "1" in element.tag:
                file_dictionary[1] = element.text
            elif "2" in element.tag:
                file_dictionary[2] = element.text

    datastreamDictionary = {}
    datastreamList = []

    for order, current_file in file_dictionary.iteritems():
        file_path = image_path + current_file
        file_extension = re.search('[0-9A-Za-z]+$', current_file).group(0)
        skip_processing = False
        cStrOrder = {}

        try:
            with open(file_path) as file:
                # grab and place in PID folder
                os.system("ln -s " + "/" + file_path + " " + path + "/" + current_file)
                print file_path
                print "copying "+file_path + " to its new directory"


                # MAKE A Dictionary that has Order and ID of current_file image
                cStrOrder[order] = current_file.split("."+file_extension)[0]

                # Construct Dictionary for datastreams
                datastreamDictionary['ds_id'] = current_file.split("."+file_extension)[0]
                datastreamDictionary['label'] = current_file
                datastreamDictionary['filename'] = current_file
                datastreamDictionary['order'] = cStrOrder
                datastreamDictionary['internal_relationships'] = {}
                datastreamDictionary['mimetype'] = "image/tiff"
                if skip_processing:
                    datastreamDictionary['skip_processing'] = True
                datastreamList.append(datastreamDictionary.copy())
        except:
            print file_path
            print "No files"
            print "Unexpected error:", sys.exc_info()[0]
            raise


#### 5) CREATE OBJMETA MANIFEST

        # Make all the properties
        label = eachMODS.findall(".//mods:title", namespaces=ns)[0].text
        representativeImage = file_dictionary[1].split("."+file_extension)[0]
        
        objMetaTemplate = {
            "content_type": "WSUDOR_Image",
            "datastreams": datastreamList,
            "id": "wayne:"+currentPID,
            "isRepresentedBy": representativeImage,
            "label": label,
            "policy": "info:fedora/wayne:WSUDORSecurity-permit-apia-unrestricted",
            "object_relationships": [
                {
                    "predicate": "http://digital.library.wayne.edu/fedora/objects/wayne:WSUDOR-Fedora-Relations/datastreams/RELATIONS/content/isMemberOfOAISet",
                    "object": "info:fedora/"+collectionPID

                },
                {
                    "predicate": "info:fedora/fedora-system:def/relations-external#isMemberOfCollection",
                    "object": "info:fedora/"+collectionPID
                },
                {
                    "predicate": "http://digital.library.wayne.edu/fedora/objects/wayne:WSUDOR-Fedora-Relations/datastreams/RELATIONS/content/isDiscoverable",
                    "object": "info:fedora/False"
                },
                {
                    "predicate": "http://digital.library.wayne.edu/fedora/objects/wayne:WSUDOR-Fedora-Relations/datastreams/RELATIONS/content/preferredContentModel",
                    "object": "info:fedora/CM:Image"
                },
                {
                    "predicate": "http://digital.library.wayne.edu/fedora/objects/wayne:WSUDOR-Fedora-Relations/datastreams/RELATIONS/content/hasSecurityPolicy",
                    "object": "info:fedora/wayne:WSUDORSecurity-permit-apia-unrestricted"
                },
                {
                    "predicate": "info:fedora/fedora-system:def/relations-external#hasContentModel",
                    "object": "info:fedora/CM:Image"
                },
            ],
        }



#### 6) WRITE A MANIFEST, SAVE TO DISK BESIDE ITS ASSOCIATED MODS, MOVE FILES TO SPOT FOR INGEST ####

    # instantiate ObjMeta class
    # pass it a dictionary of values
    # writetoFile


    om = ObjMeta(**objMetaTemplate)
    print om.toJSON()

    om.writeToFile(path + "/../objMeta.json")

    print "bagging 'em up!"
    os.system("bagit.py " + currentPID + "/")

print "moving 'em over"
os.system("find . -type d -name MSS\* -exec mv {} bags/ \;")


# Kill it with Ctrl+C
def signal_handler(signal, frame):
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
print 'Press Ctrl+C'
while True:
    time.sleep(1)
