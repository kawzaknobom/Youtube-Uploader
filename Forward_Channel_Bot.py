import asyncio

try:
    loop = asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup , InlineKeyboardButton , CallbackQuery , ForceReply,Message,BotCommand
from pyrogram.errors import FloodWait
from apscheduler.schedulers.background import BackgroundScheduler

import time
from Mongo_Class import *

Bot_Token = os.environ['Schedule_Bot_Token']
Api_Id = os.environ['Api_Id']
Api_Hash =  os.environ['Api_Hash']

def Pyrogram_Client(Bot_Token):
  Bot_Identifier = Bot_Token.split(':')[0]
  Session_file = Bot_Identifier+'_session_prm_bot'
  bot = Client(Session_file,api_id=Api_Id,api_hash=Api_Hash,bot_token=Bot_Token)
  return bot,Bot_Identifier

def Msg_Reply(Msg,Text,Buttons):
  try : 
     Replied = Msg.reply(text = Text,reply_markup = InlineKeyboardMarkup(Buttons),quote=True)
     return Replied
  except FloodWait as e :
      time.sleep(e.value)
      return Msg_Reply(Msg,Text,Buttons)
  except Exception as err : 
    Msg.reply(err)
    pass

def Msg_Delete(Msg):
  try : 
     Msg.delete()
  except FloodWait as e :
      time.sleep(e.value)
      return Msg_Delete(Msg)
  except Exception as err : 
    Msg.reply(err)
    pass
    
  
def Reply_Query(Msg,Text,Buttons):
  try : 
     Query = Msg.reply(text = Text,reply_markup = InlineKeyboardMarkup(Buttons),quote=True)
     return Query
  except FloodWait as e :
      time.sleep(e.value)
      return Reply_Query(Msg,Text,Buttons)
  except Exception as err: 
    Msg.reply(err)
    pass


def is_int(val):
    try:
        int(val)
        return True
    except Exception as err :
      return False
    
def Get_Chnl_N(bot,Chnl_Id):
  try : 
     Chnl_Name = bot.get_chat(int(Chnl_Id) if is_int(Chnl_Id) else str(Chnl_Id).replace('=','_')).title
     return Chnl_Name
  except FloodWait as e :
      time.sleep(e.value)
      return Get_Chnl_N(bot,Chnl_Id)
  except Exception as err : 
    pass

def Msg_Copy(Msg,Chnl_Id):
  try : 
     Copy = Msg.copy(int(Chnl_Id) if is_int(Chnl_Id) else str(Chnl_Id).replace('=','_'))
     return Copy
  except FloodWait as e :
      time.sleep(e.value)
      return Msg_Copy(Msg,Chnl_Id)
  except Exception as err : 
    Msg.reply(err)
    pass
    
def Get_Msg(bot,Chat_id,msg_id):
  try : 
     msg = bot.get_messages(int(Chat_id) if is_int(Chat_id) else str(Chat_id).replace('=','_'),int(msg_id))
     return msg
  except FloodWait as e :
      time.sleep(e.value)
      return Get_Msg(bot,Chat_id,msg_id)
  except Exception as err : 
      pass

def Check_Admin(bot,Channel_id):
  try : 
     bot.get_chat_members(int(Channel_id) if is_int(Channel_id) else str(Channel_id).replace('=','_'))
     return True
  except FloodWait as e :
      time.sleep(e.value)
      return Check_Admin(bot,Channel_id)
  except : 
      False


bot,Bot_Identifier = Pyrogram_Client(Bot_Token)

Accum = {}
Add_Keys = []
Skip_Key = 'skip'

MNDB = Mongo_Db("Telegram_Db","ScheduleBot")

Add_Chnl_Text = "قم بتعيين البوت مشرفاً في قناتك ثم حوّل له أحد منشورات القناة المكتوبة🌿"
Back_Chnl_Id = 'hvjjgvb'

@bot.on_message(filters.command('start') & filters.private)
def command1(bot,message):
  bot.set_bot_commands([
     BotCommand("start", "بدء"),
     BotCommand("add_channel", "إضافة قناة"),
     BotCommand("del_channel", "حذف قناة"),
     BotCommand("start_accum", "تجميع عام"),
     BotCommand("clear_accum", "إلغاء التجميع العام"),
     BotCommand("end_accum", "إنهاء التجميع العام"),
     BotCommand("help", " مساعدة"),
     BotCommand("stat", "عدد الجدولات"),
     BotCommand("skip", "تخطي"),
     BotCommand("clear_stat", "حذف جميع الجدولات")
     ])
  message.reply('لبقية البوتات \n\n @sunnaybots \n\n للبدء \n\n /add_channel')
  
@bot.on_message(filters.command('help') & filters.private)
def command1(bot,message):
  message.reply("♦️ موعد النشر | 18:00 | 6:00 PM | بتوقيت مصر ")
  
@bot.on_message(filters.command('add_channel') & filters.private)
def command1(bot,message):
  User_Id = message.from_user.id
  Add_Keys.append(User_Id)
  message.reply(Add_Chnl_Text)

@bot.on_message(filters.command('stat') & filters.private)
def command1(bot,message):
  Reply = ''''''
  User_Id = message.from_user.id
  Reply += f"♦️ مُعرّفك 👈 {User_Id} \n\n"
  Channels_List = MNDB.Grap_Keys(User_Id)
  # Channels_List = My_Db.Select_Columns(User_Id)
  if len(Channels_List) != 0 :
    for Chnl in Channels_List :
     Chnl_Posts = MNDB.Grap_Values(User_Id,Chnl)
    #  Chnl_Posts = My_Db.Select_Items(User_Id,Chnl)
     Posts_Num = len(Chnl_Posts)
     Reply += f"🔸 {Get_Chnl_N(bot,Chnl)} 👈 {Posts_Num} جدولة \n"
  else :
    Reply += "🔸 لا توجد قنوات مرتبطة بالحساب"
  message.reply(Reply)

@bot.on_message(filters.command('clear_stat') & filters.private)
def command1(bot,message):
  User_Id = message.from_user.id
  User_Ids = MNDB.Grap_Users()
  # User_Ids = My_Db.Select_Tables()
  if not User_Id in User_Ids :
      message.reply('قم بإضافة قناة أولاً \n\n /add_Channel')
      return
  Channels_List = MNDB.Grap_Keys(User_Id)
  for Chnl in Channels_List :
    Chnl_Posts = MNDB.Grap_Values(User_Id,Chnl)
    # Chnl_Posts = My_Db.Select_Items(User_Id,Chnl)
    Post_Num = len(Chnl_Posts)
    if Post_Num != 0 :
      for post in Chnl_Posts : 
        MNDB.Delete_Item(User_Id,Chnl,post)
        # My_Db.Delete_Item(User_Id,Chnl,post)
  message.reply('تم الحذف ')
  
@bot.on_message(filters.command('del_channel') & filters.private)
def command1(bot,message):
  User_Id = message.from_user.id
  # User_Ids = My_Db.Select_Tables()
  User_Ids = MNDB.Grap_Users()
  if not User_Id in User_Ids :
      message.reply('قم بإضافة قناة أولاً \n\n /add_Channel')
      return
  Call_id = Chnl_List_Query(message,User_Id,'DelChnl')

@bot.on_message(filters.command('skip') & filters.private)
def command1(bot,message):
  User_Id = message.from_user.id
  Keys_List = MNDB.Grap_Keys(User_Id)
  if not globals()['Skip_Key'] in Keys_List :
    MNDB.Insert_Key(User_Id,globals()['Skip_Key'])
  # User_Ids = My_Db.Select_Tables()
  User_Ids = MNDB.Grap_Users()
  if not User_Id in User_Ids :
      message.reply('قم بإضافة قناة أولاً \n\n /add_Channel')
      return
  Call_id = Chnl_List_Query(message,User_Id,'Skip')

@bot.on_message(filters.command('start_accum') & filters.private)
def command1(bot,message):
  User_Id = message.from_user.id
  User_Ids = MNDB.Grap_Users()
  # User_Ids = My_Db.Select_Tables()
  if not User_Id in User_Ids :
      message.reply('قم بإضافة قناة أولاً \n\n /add_Channel')
      return
  if User_Id in list(Accum.keys()) : 
    Accum.pop(User_Id)
  Reply = message.reply('تم تفعيل التجميع 🌿')
  Call_id = Chnl_List_Query(message,User_Id,'Schedule')
  Accum[User_Id] = [Reply.id,Call_id]

@bot.on_message(filters.command('clear_accum') & filters.private)
def command1(bot,message):
  User_Id = message.from_user.id
  User_Ids = MNDB.Grap_Users()
  # User_Ids = My_Db.Select_Tables()
  if not User_Id in User_Ids :
      message.reply('قم بإضافة قناة أولاً \n\n /add_Channel')
      return
  if User_Id in list(Accum.keys()) : 
    Accum.pop(User_Id)
    replied = message.reply('تم الإلغاء 🌿')
  
@bot.on_message(filters.command('end_accum') & filters.private)
def command1(bot,message):
  User_Id = message.from_user.id
  User_Ids = MNDB.Grap_Users()
  # User_Ids = My_Db.Select_Tables()
  if not User_Id in User_Ids :
      message.reply('قم بإضافة قناة أولاً \n\n /add_Channel')
      return
  if User_Id in list(Accum.keys()) : 
    reply_Id = Accum[User_Id][0]
    if len(Accum[User_Id]) > 3 :
      Data = Accum[User_Id][2]
      Copied_List = []
      for Case in Accum[User_Id][3:] :
        Msg = Get_Msg(bot,User_Id,Case)
        Copied = Msg_Copy(Msg,Back_Chnl_Id)
        Copied_List.append(str(Copied.id))
      Item = '-'.join(Copied_List)
      Add_Item(Msg,Item,Data)
    else :
      Call_Id = Accum[User_Id][1]
      Call_Msg = Get_Msg(bot,User_Id,Call_Id)
      Call_Msg.delete()
    Reply_Msg = Get_Msg(bot,User_Id,reply_Id)
    Reply_Msg.edit_text('تم تعطيل التجميع 🌷')
    Accum.pop(User_Id)
      
@bot.on_message(filters.private & filters.incoming)
def _telegram_file(client, message):
  User_Id = message.chat.id
  User_Ids = MNDB.Grap_Users()
  # User_Ids = My_Db.Select_Tables()
  Msg_Id = message.id
  Msg = Get_Msg(bot,User_Id,Msg_Id-1)
  if not Msg.text == Add_Chnl_Text :
    if not User_Id in User_Ids :
      message.reply('قم بإضافة قناة أولاً \n\n /add_Channel')
    else :
      if User_Id in list(Accum.keys()) :
         Accum[User_Id].append(message.id)
      else :
          Query_Id = Chnl_List_Query(message,User_Id,'Schedule')
  else :
   if User_Id in Add_Keys :
    if message.forward_from_chat :
     if message.forward_from_chat.username :
      Channel_id = message.forward_from_chat.username
     else :
      Channel_id = message.forward_from_chat.id
     Channels_List = MNDB.Grap_Keys(User_Id)
    #  Channels_List = My_Db.Select_Columns(User_Id)
     if Check_Admin(bot,Channel_id): 
      Channel_id = Channel_id.replace('_','=')
      if User_Id in User_Ids :
        if str(Channel_id) in Channels_List :
          message.reply('القناة موجودة بالفعل 🌿')
        else :
          MNDB.Insert_Key(User_Id,Channel_id)
          # My_Db.Add_Column(User_Id,Channel_id)
          message.reply('تم حفظ القناة 🌿')
      else :
        MNDB.Insert_User(User_Id)
        MNDB.Insert_Key(User_Id,Channel_id)
        # My_Db.Create_Table(User_Id)
        # My_Db.Add_Column(User_Id,Channel_id)
        message.reply('تم حفظ القناة 🌿')
      Add_Keys.remove(User_Id)
     else :
        message.reply('قم بتعيين البوت في إشراف قناتك أولاً')
        

@bot.on_callback_query()
def callback_query(CLIENT,CallbackQuery):
  Callback_List = CallbackQuery.data.split('_')
  Method = Callback_List[0]
  User_Id = CallbackQuery.from_user.id
  Msg_Id = Callback_List[1]
  Channel_Id = (int(Callback_List[-1]) if Callback_List[-1][0]=='-' else Callback_List[-1])
  if Method in ('Cancel','Send') : 
    try:
      Chnl_Posts = MNDB.Grap_Values(User_Id,Channel_Id)
      # Chnl_Posts = My_Db.Select_Items(User_Id,Channel_Id)
      for post in Chnl_Posts :
        if Msg_Id in post :
          Item = post
          break
      if Method == 'Send' :
        Msg_List = Item.split('_')
        Msg_Id = Msg_List[0]
        Rpl_Id = Msg_List[1]
        Res_list = []
        if '-' in Msg_Id : 
          Msgs = Msg_Id.split('-')
          for msg_id in Msgs :
            Msg = Get_Msg(bot,Back_Chnl_Id,msg_id)
            Copied = Msg_Copy(Msg,Channel_Id)
            Res_list.append(str(Copied.id))
        else :
          Msg = Get_Msg(bot,Back_Chnl_Id,Msg_Id)
          Copied = Msg_Copy(Msg,Channel_Id)
          Res_list.append(str(Copied.id))
        Reply_Msg = Get_Msg(bot,User_Id,Rpl_Id)
        try :
          Rep_Text = 'تم الإرسال 🌿'
          Rep_Ops = ['حذف','Delete']
          Rep_Buttons = [[InlineKeyboardButton(Rep_Ops[0],callback_data=f"{Rep_Ops[1]}_{'-'.join(Res_list)}_{Channel_Id}")]]
          Reply_Msg.edit_text(text = Rep_Text,reply_markup = InlineKeyboardMarkup(Rep_Buttons))
        except Exception as err :
          pass
      
      MNDB.Delete_Item(User_Id,Channel_Id,Item)
      # My_Db.Delete_Item(User_Id,Channel_Id,Item)
    except Exception as err :
     pass
    if Method == 'Cancel' :
      CallbackQuery.edit_message_text("تم الحذف 🌿")
  
  elif Method == 'Delete' :
    if '-' in Msg_Id :
      Msg_Ids = Msg_Id.split('-')
      for Id in Msg_Ids : 
        Msg = Get_Msg(bot,Channel_Id,Id)
        Msg_Delete(Msg)
    else :
      Msg = Get_Msg(bot,Channel_Id,Msg_Id)
      Msg_Delete(Msg)
    CallbackQuery.edit_message_text("تم الحذف 🌿")
  elif Method == 'DelChnl' :
    MNDB.Delete_Key(User_Id,Channel_Id)
    # My_Db.Drop_Column(User_Id,Channel_Id)
    CallbackQuery.edit_message_text("تم الحذف 🌿")
  elif Method == 'Skip' :
    MNDB.Insert_Item(User_Id,globals()['Skip_Key'],Channel_Id)
    CallbackQuery.edit_message_text("تم التخطي 🌿")
  elif Method == 'Schedule' : 
   if User_Id in list(Accum.keys()) :
    Accum[User_Id].append(Channel_Id)
   else :
     Msg = Get_Msg(bot,User_Id,Msg_Id)
     Copied = Msg_Copy(Msg,Back_Chnl_Id)
     Add_Item(Msg,Copied.id,Channel_Id)
   CallbackQuery.message.delete()
   

def Add_Item(Msg,Item,Channel_Id):
    User_Id = Msg.from_user.id
    Cancel_Option = 'اختر'
    Cancel_Op = [['سحب','Cancel'],['إرسال الآن','Send']]
    Cancel_BUTTONS = []
    for Op in Cancel_Op :
      Cancel_BUTTONS.append([InlineKeyboardButton(Op[0],callback_data=f"{Op[1]}_{Item}_{Channel_Id}")])
    Replied = Msg_Reply(Msg,Cancel_Option,Cancel_BUTTONS)
    MNDB.Insert_Item(User_Id,Channel_Id,f"{Item}_{Replied.id}")
    # My_Db.Insert_Item(User_Id,Channel_Id,f"{Item}_{Replied.id}")

def Chnl_List_Query(message,User_Id,Mode):
  Channels_List = MNDB.Grap_Keys(User_Id)
  CHOOSE_CHNL = 'اختر قناتك 🌿'
  Channel_Buttons = []
  for Chnl in Channels_List :
     if Check_Admin(bot,Chnl) == False :
      Chnl_Link = (f"https://t.me/c/{Chnl}/1" if is_int(Chnl) else f"https://t.me/{Chnl.replace('=','_')}/1")
      message.reply(f'قم بتعيين البوت في إشراف [قناتك]({Chnl_Link}) أولاً ')
      return
     Chnl_Name = Get_Chnl_N(bot,Chnl)
     Channel_Buttons.append([InlineKeyboardButton(Chnl_Name,callback_data=f'{Mode}_{message.id}_{Chnl}')])
  Query = Reply_Query(message,CHOOSE_CHNL,Channel_Buttons)
  return Query.id 
  
def Send_Post():
 User_Ids = MNDB.Grap_Users()
#  User_Ids = My_Db.Select_Tables()
 if len(User_Ids) != 0 :
  for User in User_Ids :
    Channels_List = MNDB.Grap_Keys(User)
    # Channels_List = My_Db.Select_Columns(User)
    for Chnl in Channels_List :
     try:
      if (int(Chnl) if Chnl[0]=='-' else Chnl) not in MNDB.Grap_Values(User,globals()['Skip_Key']) :
        Chnl_Posts = MNDB.Grap_Values(User,Chnl)
        # Chnl_Posts = My_Db.Select_Items(User,Chnl)
        Post_Num = len(Chnl_Posts)
        if Post_Num != 0 :
          Msg_List = Chnl_Posts[0].split('_')
          Msg_Id = Msg_List[0]
          Rpl_Id = Msg_List[1]
          Res_list = []
          if '-' in Msg_Id : 
            Msgs = Msg_Id.split('-')
            for msg_id in Msgs :
              Msg = Get_Msg(bot,Back_Chnl_Id,msg_id)
              Copied = Msg_Copy(Msg,Chnl)
              Res_list.append(str(Copied.id))
          else :
            Msg = Get_Msg(bot,Back_Chnl_Id,Msg_Id)
            Copied = Msg_Copy(Msg,Chnl)
            Res_list.append(str(Copied.id))
          Reply_Msg = Get_Msg(bot,User,Rpl_Id)
          Rep_Text = 'تم الإرسال 🌿'
          Rep_Ops = ['حذف','Delete']
          Rep_Buttons = [[InlineKeyboardButton(Rep_Ops[0],callback_data=f"{Rep_Ops[1]}_{'-'.join(Res_list)}_{Chnl}")]]
          Reply_Msg.edit_text(text = Rep_Text,reply_markup = InlineKeyboardMarkup(Rep_Buttons))
          MNDB.Delete_Item(User,Chnl,Chnl_Posts[0])
          # My_Db.Delete_Item(User,Chnl,Chnl_Posts[0])
          if Post_Num == 5 :
            Reply = f'''
            جدولات قناتك {Get_Chnl_N(bot,Chnl)} شارفت على الانتهاء ، بقي {Post_Num-1} 🌿
            '''
            Reply_Msg.reply(Reply)
     except Exception as err :
            pass
    MNDB.Delete_AllItems(User,globals()['Skip_Key'])

scheduler = BackgroundScheduler()
scheduler.add_job(Send_Post, "cron", hour=8)

scheduler.start()
bot.run()
