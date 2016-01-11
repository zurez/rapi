from flask import Flask
from flask_restful import Resource, Api
import pymongo
from bson.objectid import ObjectId
from bson.json_util import dumps
import json

from hashids import Hashids
import json
app = Flask(__name__)
api = Api(app)

connection= pymongo.MongoClient('localhost', 27017)
db = connection['qwer']
survey= db.response

class HashId(object):
    hashids = Hashids(salt = "123345666666666666666666666666666")

    @staticmethod
    def encode(uid):
        """
        Encodes a UUID String to Hashid.
        """
        w = str(ObjectId(uid))
        return HashId.hashids.encode(int(w, 16))

    @staticmethod
    def decode(hid):
        """
        """
        try:
            b = hex(HashId.hashids.decode(hid)[0])[2:]
            return ObjectId(b)
        except Exception:
            raise TypeError

class ResponseAggregation(Resource):

    def get(self, survey_id, action = 'flat'):
        try:
            s_id = HashId.decode(survey_id)
            svey = Survey.objects(id = s_id).first()

            if svey is None:
                raise TypeError

            if svey.hidden:
                raise APIException("This Survey has been deleted", 404)

        except TypeError:
            raise APIException("Invalid Survey ID", 404)

        responses = ResponseAggregation(svey)

        if action == 'flat':
            return responses.flat(), 201
        elif action == 'nested':
            return responses.nested(), 201

        # raise APIException("Must specify a valid option", 400)
class Response(Resource):
    def get(self,survey_id):

    	try:
            s_id = HashId.decode(survey_id)
            svey = Survey.objects(id = s_id).first()

            if svey is None:
                raise TypeError

            if svey.hidden:
                print "No Data"

        except TypeError as e:
            print e

        responses = ResponseAggregation(svey)

        if action == 'flat':
            return responses.flat(), 201
        elif action == 'nested':
            return responses.nested(), 201
        return json.loads(dumps(survey.find()))
class Survey(Resource):
	"""docstring for Survey"""
	def get (self):
		srvy= db['survey']
		try:
			srvy
		except Exception, e:
			raise e
		return json.loads(dumps(srvy.find()))
class Test(Resource):
	"""docstring for Test"""
	def get(self):
		return json.loads(dumps(db['response'].find()))
class Test1(Resource):
	"""docstring for Test1"""
	def get(self):
		return json.loads(dumps(db['survey'].find()))
def d(data):return json.loads(dumps(data))
class DataSort(object):
	"""docstring for DataSort"""
	def __init__(self,survey_id,uuid):
		self.sid= survey_id
		self.sid="56582299857c5616113814ae"
		self.uuid= uuid
	def get_survey(self):
		survey= db.survey.find({"_id":ObjectId(self.sid)}) #Got the particular survey.
		return survey
	def get_response(self):
		response= db.response.find({"parent_survey":ObjectId(self.sid)})
		return d(response)
	def get_uuid_label(self):
		"""labels: question text ; options ; etc"""
		#Extract the particular cid from the survey structure
		raw_label=db.survey.find() #returns empty
		aList= d(raw_label)[0]['structure']['fields'] #A backup list?
		for i in aList:
			if i['cid']==self.uuid:
				return i


		
class RAPI(Resource):
		"""docstring for RAPI"""
		def get(self,uuid):
			survey_id="IAMASURVEY"
			lol= DataSort(survey_id,uuid)
			survey_data = lol.get_uuid_label()
			j_data= d(survey_data)
			# Get Responses for  a cid
			response_data= d(lol.get_response())
			# Options
			try:
				options=[]
				option_code={}
				for i in xrange(len(j_data['field_options']['options'])):
					options.append(j_data['field_options']['options'][i]['label'])
					option_code["a_"+str(i+1)]=j_data['field_options']['options'][i]['label']

			except:

				pass
			
			#Response Count
			temp= []
			for i in range(len(response_data)):

				temp.append(response_data[i]['responses'][uuid])
			

			options_count={}
			if j_data['field_type'] not in ["ranking","rating","group_rating"]:
				for i in temp:
					if i in options_count:pass
					else:options_count[i]= temp.count(i)
			elif j_data['field_type'] in ["ranking","group_rating"]:
				for i in temp:
					aTempList= i.split("###")
					for j in aTempList:
						bTempList= j.split("##")
						l = bTempList[0]
						if l in options_count:
							
							options_count[l]= int(options_count[l])+len(aTempList)-int(bTempList[1])
						else:
							options_count[l]=len(aTempList)-int(bTempList[1])
			# elif j_data['field_type']=="rating":
			# 	for i in temp:
			# 		aTempList= i.split("###") #Check if this breaks the logic
			# 		for j in aTempList:
			# 			bTempList= j.split("##")
			# 			if j in options_count:
			# 				options_count[j]= int(options_count[j])+ int(bTempList[1])
			# 			else:
			# 				options_count[j]= int(bTempList[1])
			elif j_data['field_type']=="rating":
				for i in temp:
					if int(i)>6:
						if "above_5" in options_count:
							options_count["above_5"]= options_count["above_5"]+1
						else:
							options_count["above_5"]=1
					elif int(i)<6 and int(i)>3 :
						if "above_3" in options_count:
							options_count["above_3"]= options_count["above_3"]+1
						else:
							options_count["above_3"]=1
					elif int(i)<=3:
						if "below_3" in options_count:
							options_count["below_3"]= options_count["below_3"]+1
						else:
							options_count["below_3"]=1




			response= {}
			response['cid']= uuid
			response['survey_id']=survey_id
			response['label']=j_data['label']
			response['type']=j_data['field_type']
			response['option_code']=option_code
			response['option_count']=options_count
			response['total_resp']=len(temp)

			return response
				
api.add_resource(Response, '/<string:survey_id>/s')
api.add_resource(Survey,"/s")
api.add_resource(Test,"/x")
api.add_resource(Test1,"/y")
api.add_resource(RAPI,"/a/<string:uuid>/")
		
if __name__ == '__main__':
    app.run(debug=True)