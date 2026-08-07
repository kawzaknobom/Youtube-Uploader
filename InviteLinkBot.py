from pyrogram.types import Message
from pyrogram import Client, filters
from pyrogram.errors import FloodWait

import os,time

#### Token ####

Bot_Token = os.environ['Invite_Bot_Token']
Api_Id = os.environ['Api_Id']
Api_Hash =  os.environ['Api_Hash']


Bot_Identifier = Bot_Token.split(':')[0]
Session_file = Bot_Identifier+'_session_prm_bot'


bot = Client(Session_file,api_id=Api_Id,api_hash=Api_Hash,bot_token=Bot_Token)



def is_int(val):
    try:
        int(val)
        return True
    except Exception as err :
      return False

def Check_Admin(bot,Channel_id):
  try : 
     bot.get_chat_members(int(Channel_id) if is_int(Channel_id) else str(Channel_id))
     return True
  except FloodWait as e :
      time.sleep(e.value)
      return Check_Admin(bot,Channel_id)
  except : 
      False

@bot.on_message(filters.command('start') & filters.private)
def command1(bot,message):
  Msg_Text = """
هذا بوت صناعة روابط دعوة للقنوات والمجموعات  

♦️ خطوات الاستخدام 

1️⃣ قم بتعيين البوت في إشراف القناة أو المجموعة
2️⃣ انسخ رابط رسالة من القناة أو المجموعة وأرسله للبوت
"""
  message.reply(Msg_Text)


@bot.on_message(filters.incoming & filters.private & filters.text)
def command1(bot,message):
  if '/c/' in message.text : 
    Channel_Id = int(str(-100) + message.text.split('/c/')[1].split('/')[0])
  else : 
    Channel_Id =  message.text.split('/')[-2]
  if Check_Admin(bot,Channel_Id) :
    invite_link = bot.create_chat_invite_link(Channel_Id)
    message.reply(invite_link.invite_link)
  else :
     message.reply("قم بتعيين البوت في الإشراف")


  
bot.run()