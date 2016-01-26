import json

# PID class
class PID:
    def __init__(self, currentPID):
        # required attributes
        self.id = currentPID
        self.MODS = tree.xpath("//mets:dmdSec[@ID='"+currentPID+"']/mets:mdWrap/mets:xmlData/mods:mods", namespaces=ns)
        self.serializedMODS = etree.tostring(self.MODS, pretty_print=True, xml_declaration=True, encoding='UTF-8')[0]
        self.modsStruct = tree.xpath("//mets:div[@DMDID='"+currentPID+"']", namespaces=ns)
        # if pre-existing PID exists, override defaults
        self.__dict__.update(currentPID)


    def MODStoDisk(self, MODS):
        try:
            fileName = "MODS.xml"
            MODSpath = "./"+currentPID+"/"
            filePath = os.path.join(MODSpath, fileName)
            with open(filePath, 'wb') as stream:
                stream.write(MODS)
        except OSError:
            print "File already exists"

    def createDir(self, currentPID):
        path = "./"+currentPID+"/datastreams"
        try:
            os.makedirs(path)
        except OSError:
            print "Your directory, "+path+",is already created"


#objMeta class Object
class ObjMeta:
    # requires JSONEncoder

    def __init__(self, **obj_dict):
        # required attributes
        self.id = "Object ID"
        self.policy = "info:fedora/wayne:WSUDORSecurity-permit-apia-unrestricted"
        self.content_type = "ContentTypes"
        self.isRepresentedBy = "Datastream ID that represents object"
        self.object_relationships = []
        self.datastreams = []

        # optional attributes
        self.label = "Object label"

        # if pre-existing objMeta exists, override defaults
        self.__dict__.update(obj_dict)

    def writeToFile(self, destination):
        fhand = open(destination,'w')
        fhand.write(self.toJSON())
        fhand.close()

    #uses JSONEncoder class, exports only attributes
    def toJSON(self):
        return json.JSONEncoder().encode(self.__dict__)


# MODS class
class MODS:
    # requires JSONEncoder

    def __init__(self, currentPID):
        # required attributes
        self.id = currentPID
        self.policy = "info:fedora/wayne:WSUDORSecurity-permit-apia-unrestricted"
        self.content_type = "ContentTypes"
        self.isRepresentedBy = "Datastream ID that represents object"
        self.object_relationships = []
        self.datastreams = []

        # optional attributes
        self.label = "Object label"

        # if pre-existing objMeta exists, override defaults
        self.__dict__.update(obj_dict)

    def writeToFile(self,destination):
        stringMODS = etree.tostring(self, pretty_print=True, xml_declaration=True, encoding='UTF-8')
        try:
            fileName = "MODS.xml"
            MODSpath = "./"+self.id+"/"
            filePath = os.path.join(MODSpath, fileName)
            with open(filePath, 'wb') as stream:
                stream.write(stringMODS)
        except OSError:
            print "File already exists"

    #uses JSONEncoder class, exports only attributes
    def toJSON(self):
        return json.JSONEncoder().encode(self.__dict__)