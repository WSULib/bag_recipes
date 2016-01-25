#objMeta class Object
from json import JSONEncoder

'''
#############################################################################
OLD VERSION - WSUDOR_ContentTypes.WSUDOR_ObjMeta IS THE CANONICAL VERSION NOW
#############################################################################
'''

class ObjMeta(object):
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

	
	# function to validate ObjMeta instance as WSUDOR compliant
	def validate(self):
		pass

	def writeToFile(self,destination):
		fhand = open(destination,'w')
		fhand.write(self.toJSON())
		fhand.close()

	def importFromFile(self):
		pass

	def writeToObject(self):
		pass

	def importFromObject(self):
		pass

	#uses JSONEncoder class, exports only attributes
	def toJSON(self):
		return JSONEncoder().encode(self.__dict__)

