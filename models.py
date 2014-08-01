from google.appengine.ext import ndb


class DataList(ndb.Model):
  data = ndb.StringProperty(repeated=True)
  timestamp = ndb.DateTimeProperty(auto_now=True)


class StepData(ndb.Model):
  name = ndb.StringProperty()
  data = ndb.JsonProperty()
  timestamp = ndb.DateTimeProperty(auto_now=True)


class BuilderData(ndb.Model):
  builders = ndb.StringProperty(repeated=True)
  timestamp = ndb.DateTimeProperty(auto_now=True)


class MasterData(ndb.Model):
  steps = ndb.StructuredProperty(StepData, repeated=True)
  builders = ndb.StructuredProperty(BuilderData)
