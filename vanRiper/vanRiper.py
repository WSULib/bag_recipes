#!/usr/bin/python

from lxml import etree
import os
import mimetypes
import json
import re
import xmltodict
import sys
from classes import ObjMeta
import functions


#### 1) SETUP ####
# Set file
file = raw_input("Please input the full path to your xml file. For example, /repository/civil_war/civilwarmods.xml. Remember to start with a / and press enter/return: \n")
# file = "/repository/civil_war/civilwarmods.xml"

image_path = raw_input("What is the name of the folder in which you have placed your images? \n")
pwd = os.popen('pwd').read()
pwd = re.split('\n', pwd)[0]
image_path = pwd + "/" + image_path + "/"
# Load file into memory and find Object ID for first MODS object
tree = etree.parse(file)


# Establish namespaces
root = tree.getroot()
ns = root.nsmap
print ns
confirm = raw_input("are the correct namespaces listed above? Type 'yes' or 'no' and press enter/return: \n")
if confirm == "yes":
    print "thank you"
else:
    sys.exit("please correct your XML to have the correct namespaces")

# ns = {'mods': 'http://www.loc.gov/mods/v3', 'mets': 'http://www.loc.gov/METS/'}

#### 2) IDENTIFY MAJOR CONTENT ####
# Wrap into a for loop that goes through and finds each MODS object one by one

# TESTING GET RID OF START
# currentPID = ['MSS-001-006-008']
# for each in currentPID:
#     currentPID = each

# TESTING GET RID OF END


collectionObj = raw_input("Okay, Look in your XML document. What is the mets:dmdSec ID of your collection object? For example, MSS-001. Type it in below and press enter/return: \n")

collectionPID = raw_input("Now, what PID will you be giving your collection in Fedora? For example, wayne:collectionVanRiperLetters: \n")

# KEEP AND UNCOMMENT IN PRODUCTION
PIDS = tree.xpath('//mets:dmdSec', namespaces=ns)
for eachPID in PIDS:
    currentPID = eachPID.attrib['ID']
    print currentPID

    # KEEP AND UNCOMMENT IN PRODUCTION
    # Make a directory
    path = "./"+currentPID+"/datastreams"
    try:
        os.makedirs(path)
    except OSError:
        print "Your directory, "+path+",is already created"

#### 3) SAVE MODS CHUNKS TO DISK ####
# Copy all that MODS XML (associated with CurrentPID) and save into a .xml file inside PID folder

    # Identify current MODS chunk and give temp name
    currentMODS = tree.xpath("//mets:dmdSec[@ID='"+currentPID+"']/mets:mdWrap/mets:xmlData/mods:mods", namespaces=ns)

    # Save as a MODS file aka save .tostring and add .xml declaration at the beginning of the file
    for each in currentMODS:
        stringMODS = etree.tostring(each, pretty_print=True, xml_declaration=True, encoding='UTF-8')

    # KEEP AND UNCOMMENT IN PRODUCTION

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
    # Make our dictionary of files and ORDER for each PID
    # We have 2 major functions here. get_all()--which extracts values matching certain keys--and orderIT()--which orders lists of numbers by assuming that none sequential ordering indicates nested depth

    modsStruct = tree.xpath("//mets:div[@DMDID='"+currentPID+"']", namespaces=ns)

    for each in modsStruct:
        xml_parsing = xmltodict.parse(etree.tostring(each))

        json_string = json.dumps(xml_parsing)
        JSONd = json.loads(json_string)

        numberData = list(functions.get_all(JSONd, '@ORDER'))
        fileData = list(functions.get_all(JSONd, '@FILEID'))

        # convert to integers and identify non-sequential ordering in list
        numberData = list(map(int, numberData))
        numberList = functions.orderIT(numberData)

    # Set number of files to a variable
    if len(numberData) == len(fileData):
        fileAmount = len(numberData)
    else:
        print "error: you have different amounts of files and Order numbers"

    # Find the area that has the files associated with PID. aka Find DMDID="PID" //<element>
    # currentFiles = tree.xpath("//mets:div[@DMDID='"+currentPID+"']/mets:div/mets:fptr", namespaces=ns)
    # nestedFiles = False
    # #How many files do we have?
    # fileAmount = len(currentFiles)

    # if fileAmount == 0:
    # #     # check that it's not just grabbing the wrong part
    #     currentFiles = tree.xpath("//mets:div[@DMDID='"+currentPID+"']/mets:div/mets:div/mets:fptr", namespaces=ns)
    #     fileAmount = len(currentFiles)
    #     nestedFiles = True
    # else:
    # #     # keep old fileAmount/aka it must be zero
    #     fileAmount = len(currentFiles)

    datastreamList = []
    datastreamDictionary = {}
    datastreamDictionaryCR2 = {}
    orderDictionary = {}

    # currentPID = "MSS-001"
    if currentPID == collectionObj:
        objMetaTemplate = {
            "content_type": "WSUDOR_Collection",
            "datastreams": [
                {
                    "mimetype": "image/jpeg",
                    "label": "Collection Art",
                    "ds_id": "COLLECTIONART",
                    "internal_relationships": {},
                    "filename": "COLLECTIONART.jpg"
                }
                ],
            "id": collectionPID,
            "isRepresentedBy": "COLLECTIONART",
            "label": "Van Riper Collection",
            "object_relationships": [
                {
                    "object": "False",
                    "predicate": "http://digital.library.wayne.edu/fedora/objects/wayne:WSUDOR-Fedora-Relations/datastreams/RELATIONS/content/isOAIHarvestable"
                },
                {
                    "predicate": "http://digital.library.wayne.edu/fedora/objects/wayne:WSUDOR-Fedora-Relations/datastreams/RELATIONS/content/isRenderedBy",
                    "object": "info:fedora/collection"
                },
                {
                    "object": "info:fedora/False",
                    "predicate": "http://digital.library.wayne.edu/fedora/objects/wayne:WSUDOR-Fedora-Relations/datastreams/RELATIONS/content/isDiscoverable"
                },
                {
                    "object": "info:fedora/CM:Collection",
                    "predicate": "http://digital.library.wayne.edu/fedora/objects/wayne:WSUDOR-Fedora-Relations/datastreams/RELATIONS/content/preferredContentModel"
                },
                {
                    "object": "info:fedora/wayne:WSUDORSecurity-permit-apia-unrestricted",
                    "predicate": "http://digital.library.wayne.edu/fedora/objects/wayne:WSUDOR-Fedora-Relations/datastreams/RELATIONS/content/hasSecurityPolicy"
                },
                {
                    "object": "info:fedora/CM:Collection",
                    "predicate": "info:fedora/fedora-system:def/relations-external#hasContentModel"
                }
            ],
            "policy": "info:fedora/wayne:WSUDORSecurity-permit-apia-unrestricted"
        }
    else:
        for each in range(0, fileAmount):
            currentStrFileID = fileData[each].encode('utf-8')
            cStrOrder = numberList[each]

            currentStrFileIDshort = currentStrFileID.split("workspace-civil_war-").pop()

            # replace - to / in order to make file path
            currentStrFileIDPath = currentStrFileID.replace("-", "/")
            currentStrFileIDPath = image_path + currentStrFileIDPath
            # currentStrFileIDPath = image_path + currentStrFileID
            currentStrFileExtension = re.search('[0-9A-Za-z]+$', currentStrFileID).group(0)
            print currentStrFileID
            print currentStrFileIDPath
            if currentStrFileExtension == "CR2":
                skip_processing = True
            else:
                skip_processing = False

            try:
                with open(currentStrFileIDPath) as file:
                    # grab and place in PID folder
# UNCOMMENT FOR PRODUCTION
                    os.system("ln -s " + "/" + currentStrFileIDPath + " " + path + "/" + currentStrFileID)
                    print currentStrFileIDPath
                    print "copying "+currentStrFileIDPath + " to its new directory"

                    try:
                        ddLabel = tree.xpath("//mets:div[@DMDID='" + currentPID + "']/mets:div/mets:div/mets:fptr[@FILEID='" + currentStrFileID + "']/..", namespaces=ns)[0].attrib['LABEL']
                    except IndexError:
                        ddLabel = tree.xpath("//mets:div[@DMDID='" + currentPID + "']/mets:div/mets:fptr[@FILEID='" + currentStrFileID + "']/..", namespaces=ns)[0].attrib['LABEL']

                    # MAKE A Dictionary that has Order and ID of each image
                    orderDictionary[cStrOrder] = currentStrFileID.split(currentStrFileExtension)[0]

                    # Construct Dictionary for datastreams
                    datastreamDictionary['ds_id'] = currentStrFileID.split(currentStrFileExtension)[0]
                    datastreamDictionary['label'] = ddLabel
                    datastreamDictionary['filename'] = currentStrFileID
                    datastreamDictionary['order'] = cStrOrder
                    datastreamDictionary['internal_relationships'] = {}
                    datastreamDictionary['mimetype'] = mimetypes.guess_type(currentStrFileID)
                    if skip_processing:
                        datastreamDictionary['skip_processing'] = True
                    datastreamList.append(datastreamDictionary.copy())
            except:
                print currentStrFileIDPath
                print "No files"
                print "Unexpected error:", sys.exc_info()[0]
                raise


#### 5) CREATE OBJMETA MANIFEST


        # Make all the properties
        label = tree.xpath("//mets:div[@DMDID='"+currentPID+"']", namespaces=ns)[0].attrib['LABEL']
        representativeImage = orderDictionary[min(orderDictionary)]
        # try:
        #     remove_prefix = orderDictionary["1"].split("-").pop()
        #     remove_suffix = remove_prefix.split(".jpg")[0]
        #     representativeImage = currentPID + "-" + remove_suffix
        # except KeyError:
        #     representativeImage = ''

        # make into a class and populate its properties?
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

# KEEP AND UNCOMMENT IN PRODUCTION
    om.writeToFile(path + "/../objMeta.json")

    print "bagging 'em up!"
    os.system("bagit.py " + currentPID + "/")

    if currentPID == collectionPID:
        os.system("mv " + currentPID + "/" "bags/")

print "moving 'em over"
os.system("find . -type d -name MSS\* -exec mv {} bags/ \;")

xml_files = tree.xpath("//mets:fileGrp/mets:file/@ID", namespaces=ns)
hard_disk_files = os.popen('ls '+image_path).read().split()
differences = list(set(hard_disk_files) - set(xml_files))
print "These files were in your folder on the hard drive, but were not listed in the XML: \n"
for each in differences:
    print each + "\n"
