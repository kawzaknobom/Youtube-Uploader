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
  
  def Grap_Keys(self,User_Id):
    if not User_Id in self.Grap_Users() :
      self.Insert_User(User_Id)
    for user in self.Col.find({ "_id": User_Id }) :
      Keys = list(user.keys())
    if 'id' in Keys :
      Keys.remove('id')
    if '_id' in Keys:
      Keys.remove('_id')
    if 'skip' in Keys:
      Keys.remove('skip')
    if User_Id in Keys :
      Keys.remove(User_Id)
    return Keys
  
  def Grap_Values(self,User_Id,Key):
    Values = self.Col.find_one({"_id": User_Id},{str(Key): 1, "_id": 0}).get(str(Key))
    return Values
  
  def Insert_User(self,User_Id):
    self.Col.insert_one({"_id":User_Id})

  def Insert_Key(self,User_Id,Key):
    self.Col.update_one({"_id": User_Id}, {"$set" :{str(Key):[]}},upsert=True)
  
  def Insert_OKey(self,User_Id,Key):
    self.Col.update_one({"_id": User_Id}, {"$set" :{str(Key):{}}},upsert=True)
    
  def Insert_Item(self,User_Id,Key,Value):
    # if not User_Id in self.Grap_Users() :
    #   self.Insert_User(User_Id)
    # if not Key in self.Grap_Keys(User_Id):
    #   self.Insert_Key(User_Id,Key)
    self.Col.update_one({"_id": User_Id},{ "$push": { str(Key): Value } })

  def Delete_Item(self,User_Id,Key,Value):
    self.Col.update_one({ "_id": User_Id },{ "$pull": { str(Key): Value } })
  def Delete_AllItems(self,User_Id,Key):
    self.Col.update_one({"_id": User_Id},{"$set": {Key: []}})

  def Delete_Key(self,User_Id,Key):
    self.Col.update_one({ "_id": User_Id },{ "$unset": { str(Key): "" } })
  
  def Edit_Item(self,User_Id,Key,Value,New_Value):
    # if not User_Id in self.Grap_Users() :
    #   self.Insert_User(User_Id)
    # if not Key in self.Grap_Keys(User_Id):
    #   self.Insert_Key(User_Id,Key)
    self.Col.update_one({"_id": User_Id, str(Key): Value},{"$set": {f"{Key}.$": New_Value}})
  







