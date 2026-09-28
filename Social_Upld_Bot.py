from pyrogram.types import InlineKeyboardMarkup , InlineKeyboardButton , CallbackQuery , ForceReply,Message,BotCommand
from pyrogram.errors import FloodWait
from pyrogram import Client, filters

from apscheduler.schedulers.background import BackgroundScheduler

import time,json,os,shutil,requests

from Mongo_Class import *

Small_line_break = '\n\n'
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

Audio_Forms = (".mp3",".ogg",".m4a",".aac",".flac",".wav",".wma",".opus",".3gpp")
Video_Forms = (".mp4",".mkv",".mov",".avi",".wmv",".avchd",".webm",".flv")
Image_forms = (".jpg",".png",'.tif','webp')


Bot_Token = os.environ['Social_Bot_Token']
Api_Id = os.environ['Api_Id']
Api_Hash =  os.environ['Api_Hash']
admins = os.environ['admins']
Admin_Ids = admins.split(',')

# My_Db

def Pyrogram_Client(Bot_Token):
  Bot_Identifier = Bot_Token.split(':')[0]
  Session_file = Bot_Identifier+'_session_prm_bot'
  bot = Client(Session_file,api_id=Api_Id,api_hash=Api_Hash,bot_token=Bot_Token)
  return bot,Bot_Identifier


bot,Bot_Identifier = Pyrogram_Client(Bot_Token)

upld_dir = f"/{Bot_Identifier}_Dir/"

Bulking,Accum = {},{}
Skip_Key = 'skip'

MNDB = Mongo_Db("Telegram_Db","FbBot")

Back_Chnl_Id = 'hvjjgvb'


################# Extra Funcs ##########


def Msg_Reply(Msg,Text,Buttons):
  try : 
     Replied = Msg.reply(text = Text,reply_markup = InlineKeyboardMarkup(Buttons),quote=True)
     return Replied
  except FloodWait as e :
      time.sleep(e.value)
      return  Msg_Reply(Msg,Text,Buttons)
  except Exception as err : 
    Replied = Msg.reply('تمت الإضافة')
    # Msg.reply(err)
    return Replied

def Msg_Delete(Msg):
  try : 
      Msg.delete()
  except FloodWait as e :
      time.sleep(e.value)
      return Msg_Delete(Msg)
  except Exception as err : 
    Msg.reply(err)
    pass

def Msg_Copy(Msg,Chnl_Id):
  try : 
     Copy =  Msg.copy(Chnl_Id)
     return Copy
  except FloodWait as e :
      time.sleep(e.value)
      return  Msg_Copy(Msg,Chnl_Id)
  except Exception as err : 
    Msg.reply(err)
    pass
  
  
def Get_Msg(bot,Chat_id,msg_id):
  try : 
     msg =  bot.get_messages(Chat_id,int(msg_id))
     return msg
  except FloodWait as e :
      time.sleep(e.value)
      return  Get_Msg(bot,Chat_id,msg_id)
  except : 
      pass

def Check_Dir(Dir):
  if os.path.isdir(Dir):
      shutil.rmtree(Dir)
  for file in os.listdir(Dir) :
    Check_File(Dir+file)

def Check_File(File):
  if os.path.isfile(File):
      os.remove(File)

def File_Dl(File_Msg,dl_path):
  if File_Msg.photo : 
    ex = '.jpg'
    file_n = File_Msg.photo.file_unique_id
  elif File_Msg.video : 
    ex = '.mp4'
    file_n = File_Msg.video.file_unique_id
  file = f'./{file_n+ex}'
  File = File_Msg.download(file_name=file)
  return File 

def Media_Compress(file_path,Rate=None):
  if file_path.lower().endswith(Audio_Forms) : 
   Res_File = ('.' if file_path.startswith('.') else '') + file_path.split('.')[(1 if file_path[0] == '.' else 0)] + '_Comp.mp3'
   Comp_Cmd = f'ffmpeg -i "{file_path}" -b:a "{Rate}" "{Res_File}" -y '
  else :
    Res_File = ('.' if file_path.startswith('.') else '') + file_path.split('.')[(1 if file_path[0] == '.' else 0)] + '_Comp.mp4'
    Comp_Cmd = f'ffmpeg -i "{file_path}" -c:v libx265 -crf 28 "{Res_File}" -y'
  os.system(Comp_Cmd)
  return Res_File

########### Fb Funcs ############


def Fb_Upld(bot,back_id,Creds,upld_fb_dir,pack):
   Page_Id,Page_Prof_id,Access_Token = Creds.split('|')
   # Check_Dir(upld_fb_dir)
   Main_Cap = ''
   Media_Msgs = []
   for msg_id in pack : 
     if '-' in msg_id : 
       msg_pack = msg_id.split('-')
       Sub_Cap = ''
       for msg_pack_id in msg_pack : 
         msg = Get_Msg(bot,back_id,msg_pack_id)
         if msg.photo or msg.video: 
           Media_N = msg
           if msg.caption != None :
             Sub_Cap += msg.caption+Small_line_break
         elif msg.text : 
           Sub_Cap += msg.text+Small_line_break
         elif msg.document : 
          if msg.document.file_name.lower().endswith('txt'):
           txt_file = File_Dl(msg,upld_fb_dir)
           Sub_Cap += open(txt_file,'r').read()+Small_line_break
          else :
           Media_N = msg
           if msg.caption != None :
            Sub_Cap += msg.caption+Small_line_break
            
       fb_path = File_Dl(Media_N,upld_fb_dir)
       Media_id = up_func(Access_Token,Page_Id,Sub_Cap,fb_path)
       Media_Msgs.append([Media_id])
     else : 
       msg = Get_Msg(bot,back_id,int(msg_id))
       if msg.text : 
         Main_Cap += msg.text + Small_line_break
       elif msg.document : 
        if msg.document.file_name.lower().endswith('txt'):
         txt_file = File_Dl(msg,upld_fb_dir)
         Main_Cap += open(txt_file,'r').read() + Small_line_break
        else :
          Media_Msgs.append(msg)
       elif msg.photo or msg.video: 
         Media_Msgs.append(msg)
   
   if len(Media_Msgs) > 1 : 
     Feed_Link = upld_album(Access_Token,Page_Id,Page_Prof_id,Media_Msgs,Main_Cap)
   elif len(Media_Msgs) == 1   : 
     if Media_Msgs[0].caption : 
       msgMedia_Cap = Media_Msgs[0].caption
     else : 
       msgMedia_Cap = ' '
     fb_path = File_Dl(Media_Msgs[0],upld_fb_dir)
     Feed_Link = up_func(Access_Token,Page_Id,msgMedia_Cap+Small_line_break+Main_Cap,fb_path,True)
   else : 
    Feed_Link = post_text(Access_Token,Page_Id,Main_Cap)
   return Feed_Link

def delete_post(Access_Token,Page_Id,post_link):
  post_id = post_link.split('/')[-2]
  payload = {
        'access_token': Access_Token}
  url = f'https://graph.facebook.com/v22.0/{Page_Id}_{post_id}'
  response = requests.delete(url,data=payload)

def post_text(Access_Token,Page_Id,text):
    url = f'https://graph.facebook.com/v22.0/{Page_Id}/feed'
    payload = {
        'access_token': Access_Token,
        'message': text }
    try :
      response = requests.post(url, data=payload)
    except Exception as err :
      pass
    feedid = response.text.replace('"','').replace('{','').replace('}','').split(':')[1].split('_')[1]
    feedlink = f"https://www.facebook.com/{Page_Id}/posts/{feedid}/"
    return feedlink
    
def up_func(Access_Token,Page_Id,Media_Cap,fb_path,publish=False) : 
  if fb_path.lower().endswith(Image_forms) : 
        section = 'photos'
        cap = 'message'
  else :
        section = 'videos'
        cap = 'description'
        
  files = {'source' : open(fb_path,'rb')}
  payload = {'access_token': Access_Token.strip() , cap : Media_Cap,'published':f"{publish}" }
  url = f'''https://graph.facebook.com/v22.0/{Page_Id.strip()}/{section}'''
  response = requests.post(url,data=payload,files=files,headers=headers)
  try:
    Media_id = json.loads(response.text)["id"]
  except Exception as err  :
    print(response.text)
    # if section == 'videos' :
    #   fb_path = Media_Compress(fb_path)
    #   return up_func(Access_Token,Page_Id,Media_Cap,fb_path,publish) 
  os.remove(fb_path)
  if publish :
    medialink = f"https://www.facebook.com/{Page_Id}/{section}/{Media_id}/"
    return medialink
  else :
    return Media_id
  
def upld_album(Access_Token,Page_Id,prof_id,msg_list,Media_Cap):
    file_ids = []
    for msg in msg_list : 
      if not isinstance(msg, list) : 
       file_id = up_func(Page_Id,Access_Token,msg,msg.caption)
      else : 
        file_id = msg[0]
        
      item = {"media_fbid" : file_id}
      file_ids.append(item)
    url = f"https://graph.facebook.com/v22.0/{Page_Id}/feed"
    params = {
      "access_token": Access_Token,
      "message": Media_Cap ,"attached_media": json.dumps(file_ids)}
    response = requests.post(url,data = params)
    Feed_id = json.loads(response.text)["id"].split('_')[-1]
    medialink = f"https://www.facebook.com/story.php?story_fbid={Feed_id}&id={prof_id}"
    return medialink

############## Main Bot Funcs ########### 

@bot.on_message(filters.command('start') & filters.private)
def command1(bot,message):
   bot.set_bot_commands([
     BotCommand("start", "بدء"),
     BotCommand("add_platform", "إضافة منصة"),
     BotCommand("start_bulk", "تجميع متخصص"),
     BotCommand("clear_bulk", "إلغاء التجميع المتخصص"),
     BotCommand("bulk", "إنهاء التجميع المتخصص"),
     BotCommand("start_accum", "تجميع عام"),
     BotCommand("clear_accum", "إلغاء التجميع العام"),
     BotCommand("end_accum", "إنهاء التجميع العام"),
     BotCommand("skip", "تخطي"),
     BotCommand("stat", "عدد الجدولات")])
   
   message.reply('لبقية البوتات \n\n @sunnaybots \n\n للبدء \n\n /add_platform')


def Get_Item(Page_Posts,Msg_Id):
  for post in Page_Posts :
    if Msg_Id in post :
      return post
        
@bot.on_message(filters.command('add_platform') & filters.private)
def command1(bot,message):
    Add_Acc_Name = f"أدخل اسم صفحة الفيسبوك🌿"
    message.reply(Add_Acc_Name,reply_markup=ForceReply(True))

@bot.on_message(filters.command('skip') & filters.private)
def command1(bot,message):
  User_Id = message.from_user.id
  Keys_List = MNDB.Grap_Keys(User_Id)
  if not globals()['Skip_Key'] in Keys_List :
    MNDB.Insert_Key(User_Id,globals()['Skip_Key'])
  User_Ids = MNDB.Grap_Users()
  if not User_Id in User_Ids :
      message.reply('قم بإضافة قناة أولاً \n\n /add_Channel')
      return
  Call_id = Call_List_Mk(message,User_Id,'Skip')

@bot.on_message(filters.command('stat') & filters.private)
def command1(bot,message):
  Reply = ''''''
  User_Id = message.from_user.id
  Reply += f"♦️ مُعرّفك 👈 {User_Id} \n\n"
  Pages_List = MNDB.Grap_Keys(User_Id)
  if len(Pages_List) != 0 :
    for Page in Pages_List :
      if not Page == 'skip':
        Page_Posts = MNDB.Grap_Values(User_Id,Page).get('Sched')
        try :
          Posts_Num = len(Page_Posts)
        except :
          Posts_Num = 0
        Reply += f"🔸 {Page} 👈 {Posts_Num} جدولة \n"
  else :
    Reply += "🔸 لا توجد صفحات مرتبطة بالحساب"
  message.reply(Reply)


@bot.on_message(filters.command('start_accum') & filters.private)
def command1(bot,message):
  User_Id = message.from_user.id
  if User_Id in list(Accum.keys()) : 
    Accum.pop(User_Id)
  Reply = message.reply('تم تفعيل التجميع 🌿')
  Call_id = Call_List_Mk(message,message.id,'Schedule')
  Accum[User_Id] = [Reply.id,Call_id]

@bot.on_message(filters.command('clear_accum') & filters.private)
def command1(bot,message):
  User_Id = message.from_user.id
  if User_Id in list(Accum.keys()) :
    Call_Id = Accum[User_Id][1]
    Reply_Id = Accum[User_Id][0]
    Call_Msg = Get_Msg(bot,User_Id,Call_Id)
    Reply_Msg = Get_Msg(bot,User_Id,Reply_Id)
    if not Call_Msg.empty :
      Call_Msg.delete()
    Reply_Msg.edit_text('تم تعطيل التجميع 🌷')
    Accum.pop(User_Id)
  
@bot.on_message(filters.command('end_accum') & filters.private)
def command1(bot,message):
  User_Id = message.from_user.id
  if User_Id in list(Accum.keys()) : 
    reply_Id = Accum[User_Id][0]
    if len(Accum[User_Id]) > 3 :
      Data = Accum[User_Id][2]
      for Case in Accum[User_Id][3:] :
        Case_Msg = Get_Msg(bot,User_Id,Case)
        Copied = Msg_Copy(Case_Msg,Back_Chnl_Id)
        Add_Item(Case_Msg,Data,Copied.id)
    else :
      Call_Id = Accum[User_Id][1]
      Call_Msg = Get_Msg(bot,User_Id,Call_Id)
      Call_Msg.delete()
    Reply_Msg = Get_Msg(bot,User_Id,reply_Id)
    Reply_Msg.edit_text('تم تعطيل التجميع 🌷')
    Accum.pop(User_Id)

@bot.on_message(filters.command('start_bulk') & filters.private)
def command1(bot,message):
  replied = message.reply('تم تفعيل التجميع 🌿')
  User_Id = message.from_user.id
  if User_Id in list(Bulking.keys()) : 
    Bulking.pop(User_Id)
  Bulking[User_Id] = [replied.id,]

@bot.on_message(filters.command('clear_bulk') & filters.private)
def command1(bot,message):
  User_Id = message.from_user.id
  if User_Id in list(Bulking.keys()) : 
    Bulking.pop(User_Id)
    replied = message.reply('تم الإلغاء 🌿')
    
@bot.on_message(filters.command('bulk') & filters.private)
def command1(bot,message):
  User_Id = message.from_user.id
  if User_Id in list(Bulking.keys()) : 
    Msg_Ids = message.text[6:].strip()
    if not len(Msg_Ids.strip()) == 0 :
      Msg_Ids = Msg_Ids.replace(' ','|')
      Bulking[User_Id].append(Msg_Ids)
      Call_id = Call_List_Mk(message,message.id,'Schedule')

def Call_List_Mk(message,Msg_Ids,Mode):
  User_Id = message.chat.id
  User_Ids = MNDB.Grap_Users()
  if not User_Id in User_Ids :
      message.reply('قم بإضافة صفحة أولاً \n\n /add_platform')
      return
  else :
      Pages_List = MNDB.Grap_Keys(User_Id)
      Choose_Page = 'اختر صفحتك 🌿'
      Page_Buttons = []
      for Page in Pages_List :
       if not Page == 'skip':
         Page_Name = Page + '| فيسبوك'
         Page_Buttons.append([InlineKeyboardButton(Page_Name,callback_data=f'{Mode}_{Msg_Ids}_{Page.replace(" ","|")}')])
      replied = message.reply(text = Choose_Page,reply_markup = InlineKeyboardMarkup(Page_Buttons),quote=True)
  return replied.id
  
@bot.on_callback_query()
def callback_query(CLIENT,CallbackQuery):
  Callback_List = CallbackQuery.data.split('_')
  Method = Callback_List[0]
  User_Id = CallbackQuery.from_user.id
  Page_Name = Callback_List[2].replace('|',' ')
  
  if Method == 'Delete' : 

    Rpl_Id = Callback_List[1]
    Msg = Get_Msg(bot,User_Id,Rpl_Id)
    Feed_Link = Msg.text
    Creds = MNDB.Grap_Values(User_Id,Page_Name).get('Data')[0]
    Creds_List = Creds.split('|')
    Page_Id = int(Creds_List[0])
    Access_Token = Creds_List[-1]
    delete_post(Access_Token,Page_Id,Feed_Link)
    CallbackQuery.edit_message_text("تم الحذف 🌿")

  elif Method in ('Cancel','Send','Schedule','Skip')  : 
    Msg_Ids = Callback_List[1]
    if Method in ('Cancel','Send')  : 
      try:
        Page_Posts = MNDB.Grap_Values(User_Id,Page_Name).get('Sched')
        Item = Get_Item(Page_Posts,Msg_Ids)
        if Method == 'Send' :
          Msg_List = Item.split('_')
          Msg_Id = Msg_List[0]
          Rpl_Id = Msg_List[1]
          if '|' in Msg_Id : 
            Bulk_List = Msg_Id.split('|')
          else :
            Bulk_List = [Msg_Id,]
          Creds = MNDB.Grap_Values(User_Id,Page_Name).get('Data')[0]
          try :
            Feed_Link = Fb_Upld(bot,Back_Chnl_Id,Creds,upld_dir,Bulk_List)
          except Exception as err:
            pass
          Reply_Msg = Get_Msg(bot,User_Id,Rpl_Id)
          try :
            Rep_Text = Feed_Link
            Rep_Ops = ['حذف','Delete']
            Rep_Buttons = [[InlineKeyboardButton(Rep_Ops[0],callback_data=f"{Rep_Ops[1]}_{Rpl_Id}_{Callback_List[2]}")]]
            CallbackQuery.edit_message_text(text = Feed_Link,reply_markup = InlineKeyboardMarkup(Rep_Buttons))
          except Exception as err :
            pass
        elif Method in ('Cancel')  :
          CallbackQuery.edit_message_text("تم الحذف 🌿")
        MNDB.Delete_Item(User_Id,Page_Name+'.Sched',Item)
      except Exception as err :
       pass
    
    elif Method == 'Skip' :
      MNDB.Insert_Item(User_Id,globals()['Skip_Key'],Page_Name)
      CallbackQuery.edit_message_text("تم التخطي 🌿")
    
    elif Method == 'Schedule' :
     if not User_Id in list(Accum.keys()) :
      Msg_Ids = Bulking[User_Id][1] if User_Id in list(Bulking.keys()) else Msg_Ids
      Msg_Ids += '|' if not '|' in Msg_Ids else ''
      Copied = """"""
      Msgs_Bulk = Msg_Ids.split('|')
      for No,Msg_Mass in enumerate(Msgs_Bulk):
        if '-' in Msg_Mass :
          Msg_List = Msg_Mass.split('-')
          for N,Msg in enumerate(Msg_List) : 
           Msg = Get_Msg(bot,User_Id,Msg)
           Copy = Msg_Copy(Msg,Back_Chnl_Id)
           #Copy = Msg.copy(int(Back_Chnl_Id))
           Copied+= str(Copy.id) + ('-' if N < len(Msg_List)-1 else '')
        else :
          if (No == len(Msgs_Bulk)-1) and (len(Msg_Mass.strip()) == 0) :
             continue
          Msg = Get_Msg(bot,User_Id,Msg_Mass)
          Copy = Msg_Copy(Msg,Back_Chnl_Id)
          #Copy = Msg.copy(int(Back_Chnl_Id))
          Copied+= str(Copy.id)
        if not (((No == len(Msgs_Bulk)-1) and (len(Msg_Mass.strip()) == 0)) or ((No == len(Msgs_Bulk)-2) and (len(Msgs_Bulk[No+1].strip()) == 0))) :
          Copied+= '|' if No < len(Msgs_Bulk)-1 else ''
        
     if User_Id in list(Accum.keys()) :
        Accum[User_Id].append(Page_Name)
     elif User_Id in list(Bulking.keys()) :
      reply_Id = Bulking[User_Id][0]
      Reply_Msg = Get_Msg(bot,User_Id,reply_Id)
      Reply_Msg.edit_text('تم تعطيل التجميع 🌷')
      Bulking.pop(User_Id)
      Add_Item(Msg,Page_Name,Copied)
     else :
        Add_Item(Msg,Page_Name,Copied)
     CallbackQuery.message.delete()

  
def Add_Item(Msg,Data,Msg_Id):
      User_Id = Msg.from_user.id
      Cancel_Option = 'اختر'
      Cancel_Op = [['سحب','Cancel'],['إرسال الآن','Send']]
      Cancel_BUTTONS = []
      for Op in Cancel_Op :
        Cancel_BUTTONS.append([InlineKeyboardButton(Op[0],callback_data=f"{Op[1]}_{Msg_Id}_{Data.replace(' ','|')}")])
      Replied = Msg_Reply(Msg,Cancel_Option,Cancel_BUTTONS)
      Item = f"{Msg_Id}_{Replied.id}"
      MNDB.Insert_Item(User_Id,Data+'.Sched',Item)

#################

@bot.on_message(filters.private & filters.reply)
def refunc(client,message):
   if (message.reply_to_message.reply_markup) and isinstance(message.reply_to_message.reply_markup, ForceReply)  :
    
    User_Id = message.from_user.id
    Msg_Text = message.text
    reply_id = message.reply_to_message_id
    reply_msg = Get_Msg(bot,User_Id,reply_id)
    message.delete()
    
    if 'اسم صفحة' in reply_msg.text:
      Page_Name = Msg_Text.strip()
      Data_Vars = """
      Page Id
      Profile Id
      Access Token
      """
      Add_Acc_Data = f"أدخل بيانات صفحة الفيسبوك |{Page_Name}" + Data_Vars
      
      reply_msg.reply(Add_Acc_Data,reply_markup=ForceReply(True))
      if User_Id not in MNDB.Grap_Users() :
        MNDB.Insert_User(User_Id)
      MNDB.Insert_OKey(User_Id,Page_Name)
      reply_msg.delete()
    
    elif 'بيانات'  in reply_msg.text:
      Acc_Token = '|'.join(Msg_Text.split('\n'))
      Page_Name = reply_msg.text.split('|')[-1].split('\n')[0].strip()
      MNDB.Insert_Item(User_Id,Page_Name +'.Data',Acc_Token)
      reply_msg.reply('تمت الإضافة بنجاح 🌿')
      reply_msg.delete()
      
      
@bot.on_message(filters.incoming & filters.private)
def command1(bot,message):
 User_Id = message.from_user.id
 if User_Id in list(Bulking.keys()) :
   message.reply(message.id,quote=True)
 else :
   if User_Id in list(Accum.keys()) :
     Accum[User_Id].append(message.id)
   else :
    Call_id = Call_List_Mk(message,message.id,'Schedule')
    
def Send_Post(Spec=None):
 User_Ids = MNDB.Grap_Users()
 if len(User_Ids) != 0 :
  for User in User_Ids :
    Pages_List = MNDB.Grap_Keys(User)
    for Page in Pages_List :
     if (not (Page in MNDB.Grap_Values(User,globals()['Skip_Key']) or Page == 'skip')) if Spec== None else (Page == Spec)  :
      Page_Posts = MNDB.Grap_Values(User,Page).get('Sched')
      Post_Num = len(Page_Posts)
      if Post_Num != 0  :
        Post = Page_Posts[0]
        Msg_List = Post.split('_')
        Msg_Id = Msg_List[0]
        Rpl_Id = Msg_List[1]
        if '|' in Msg_Id : 
          Bulk_List = Msg_Id.split('|')
        else :
          Bulk_List = [Msg_Id,]
        Creds = MNDB.Grap_Values(User,Page).get('Data')[0]
        try :
          Feed_Link = Fb_Upld(bot,Back_Chnl_Id,Creds,upld_dir,Bulk_List)
        except :
          pass
        Reply_Msg = Get_Msg(bot,User,Rpl_Id)
        try :
          Rep_Text = Feed_Link
          Rep_Ops = ['حذف','Delete']
          Rep_Buttons = [[InlineKeyboardButton(Rep_Ops[0],callback_data=f"{Rep_Ops[1]}_{Rpl_Id}_{Page.replace(' ','|')}")]]
          Reply_Msg.edit_text(text = Feed_Link,reply_markup = InlineKeyboardMarkup(Rep_Buttons))
        except Exception as err :
          pass
        MNDB.Delete_Item(User,Page+'.Sched',Post)
        if Post_Num == 5 :
          Reply = f'''
          جدولات قناتك {Page} شارفت على الانتهاء ، بقي {Post_Num-1} 🌿
          '''
          Reply_Msg.reply(Reply)
        time.sleep(15)
    MNDB.Delete_AllItems(User,globals()['Skip_Key'])
      
      
scheduler = BackgroundScheduler()
# scheduler.add_job(Send_Post, "interval", seconds=600)
scheduler.add_job(Send_Post, "cron", hour=8)

scheduler.start()
bot.run()
