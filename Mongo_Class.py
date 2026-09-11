import pymongo,os

Mongo_String = os.environ['Mongo_String']

class Mongo_Db():
  
  def __init__(self,Db_Name,Col_Name):
    self.Db_Name = Db_Name
    self.Col_Name = Col_Name
    myclient = pymongo.MongoClient(Mongo_String)
    MyDb = myclient[self.Db_Name]
    self.Col = MyDb[self.Col_Name]
  
    
  def Grap_Users(self):
    Users = []
    for user in self.Col.find({}) :
      Users.append(user.get("_id"))
    return Users
  
  def Grap_Keys(self,data):
    if not data in self.Grap_Users() :
      self.Insert_User(data)
    for user in self.Col.find({ "_id": data }) :
      Keys = list(user.keys())
    if 'id' in Keys :
      Keys.remove('id')
    if '_id' in Keys:
      Keys.remove('_id')
    if 'skip' in Keys:
      Keys.remove('skip')
    if data in Keys :
      Keys.remove(data)
    return Keys
  
  def Grap_Values(self,data,field):
    Values = self.Col.find_one({"_id": data},{str(field): 1, "_id": 0}).get(str(field))
    return Values
  
  def Insert_User(self,data):
    self.Col.insert_one({"_id":data})

  def Insert_Key(self,data,field):
    self.Col.update_one({"_id": data}, {"$set" :{str(field):[]}},upsert=True)
  
  def Insert_OKey(self,data,field):
    self.Col.update_one({"_id": data}, {"$set" :{str(field):{}}},upsert=True)
    
  def Insert_Item(self,data,field,Value):
    # if not data in self.Grap_Users() :
    #   self.Insert_User(data)
    # if not field in self.Grap_Keys(data):
    #   self.Insert_Key(data,field)
    self.Col.update_one({"_id": data},{ "$push": { str(field): Value } })

  def Delete_Item(self,data,field,Value):
    self.Col.update_one({ "_id": data },{ "$pull": { str(field): Value } })
  def Delete_AllItems(self,data,field):
    self.Col.update_one({"_id": data},{"$set": {field: []}})

  def Delete_Key(self,data,field):
    self.Col.update_one({ "_id": data },{ "$unset": { str(field): "" } })
  
  def Edit_Item(self,data,field,Value,New_Value):
    # if not data in self.Grap_Users() :
    #   self.Insert_User(data)
    # if not field in self.Grap_Keys(data):
    #   self.Insert_Key(data,field)
    self.Col.update_one({"_id": data, str(field): Value},{"$set": {f"{field}.$": New_Value}})
  
  def Edit_Loop(self,data,field,New_Value):
    # if not data in self.Grap_Users() :
    #   self.Insert_User(data)
    # if not field in self.Grap_Keys(data):
    #   self.Insert_Key(data,field)
    self.Col.update_one({"_id":data},{"$set":{field:New_Value}})
