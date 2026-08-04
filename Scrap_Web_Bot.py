from pyrogram.types import Message
from pyrogram import Client, filters
import requests,os,random
from bs4 import BeautifulSoup
from textwrap import wrap

#### Token ####

Bot_Token = os.environ['Web_Bot_Token']
Api_Id = os.environ['Api_Id']
Api_Hash =  os.environ['Api_Hash']


linebreak = '\n'

Bot_Identifier = Bot_Token.split(':')[0]
Session_file = Bot_Identifier+'_session_prm_bot'


bot = Client(Session_file,api_id=Api_Id,api_hash=Api_Hash,bot_token=Bot_Token)

#######

def Get_Name(Lines_List): 
    for line in Lines_List : 
      if len(line.strip()) != 0 : 
        Main_Name = line 
        break
    Txt_File = f'{Main_Name[:19]}_{random.randint(0,1000)}_Scraped.txt'
    return Txt_File
   
@bot.on_message(filters.command('noline') & filters.private)
def command1(bot,message):
   globals()['linebreak'] = ' '
   
@bot.on_message(filters.command('line') & filters.private)
def command1(bot,message):
   globals()['linebreak'] = '\n'
   
@bot.on_message(filters.command('start') & filters.private)
def command1(bot,message):
   message.reply('لبقية البوتات \n\n @sunnaybots')
   
Direct_Link_Regex = r"^((?:https?:)?\/\/)"

@bot.on_message(filters.private & filters.incoming & (filters.text and filters.regex(Direct_Link_Regex)))
def _telegram_file(client, message):
    Replied = message.reply('جار السحب ☕')
    Link = message.text
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    Response = requests.get(Link,headers=headers)
    Soup = BeautifulSoup(Response.text, 'html.parser')
    Page_Text_Lines = Soup.get_text().splitlines()
    Txt_File = Get_Name(Page_Text_Lines)
    with open(Txt_File, 'a') as file:
      for line in Page_Text_Lines : 
        if len(line.strip()) != 0 : 
         file.write(line.strip()+globals()['linebreak'])
    message.reply_document(Txt_File)
    os.remove(Txt_File)
    Replied.edit_text('تم السحب ✅')
  
bot.run()
