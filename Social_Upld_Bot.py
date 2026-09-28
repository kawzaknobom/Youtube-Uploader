import asyncio

try:
    loop = asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ForceReply, Message, BotCommand
from pyrogram.errors import FloodWait
from pyrogram import Client, filters

from apscheduler.schedulers.background import BackgroundScheduler

import time, json, os, shutil, requests

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
Api_Hash = os.environ['Api_Hash']
admins = os.environ['admins']
Admin_Ids = admins.split(',')

def Pyrogram_Client(Bot_Token):
    Bot_Identifier = Bot_Token.split(':')[0]
    Session_file = Bot_Identifier + '_session_prm_bot'
    bot = Client(Session_file, api_id=Api_Id, api_hash=Api_Hash, bot_token=Bot_Token)
    return bot, Bot_Identifier

bot, Bot_Identifier = Pyrogram_Client(Bot_Token)

# تصحيح مسار التنزيل ليصبح نسبياً
upld_dir = f"./{Bot_Identifier}_Dir/"
os.makedirs(upld_dir, exist_ok=True)

Bulking, Accum = {}, {}
Skip_Key = 'skip'

MNDB = Mongo_Db("Telegram_Db", "FbBot")

# تأكد من وضع ID صحيح للقناة (Integer يبدأ بـ -100)
Back_Chnl_Id = "hvjjgvb" 

################# Extra Funcs ##########

def Msg_Reply(Msg, Text, Buttons):
    try: 
        Replied = Msg.reply(text=Text, reply_markup=InlineKeyboardMarkup(Buttons), quote=True)
        return Replied
    except FloodWait as e:
        time.sleep(e.value)
        return Msg_Reply(Msg, Text, Buttons)
    except Exception as err: 
        Replied = Msg.reply('تمت الإضافة')
        return Replied

def Msg_Delete(Msg):
    try: 
        Msg.delete()
    except FloodWait as e:
        time.sleep(e.value)
        return Msg_Delete(Msg)
    except Exception as err: 
        print(f"Delete Error: {err}")

def Msg_Copy(Msg, Chnl_Id):
    try: 
        Copy = Msg.copy(Chnl_Id)
        return Copy
    except FloodWait as e:
        time.sleep(e.value)
        return Msg_Copy(Msg, Chnl_Id)
    except Exception as err: 
        print(f"Copy Error: {err}")
        return None

def Get_Msg(bot, Chat_id, msg_id):
    try: 
        msg = bot.get_messages(Chat_id, int(msg_id))
        return msg
    except FloodWait as e:
        time.sleep(e.value)
        return Get_Msg(bot, Chat_id, msg_id)
    except Exception as err: 
        print(f"Get Msg Error: {err}")
        return None

def Check_Dir(Dir):
    if os.path.exists(Dir):
        for file in os.listdir(Dir):
            Check_File(os.path.join(Dir, file))

def Check_File(File):
    if os.path.isfile(File):
        try:
            os.remove(File)
        except Exception:
            pass

def File_Dl(File_Msg, dl_path):
    os.makedirs(dl_path, exist_ok=True)
    ex = '.jpg'
    file_n = 'temp_file'
    if File_Msg.photo: 
        ex = '.jpg'
        file_n = File_Msg.photo.file_unique_id
    elif File_Msg.video: 
        ex = '.mp4'
        file_n = File_Msg.video.file_unique_id
    elif File_Msg.document:
        ex = os.path.splitext(File_Msg.document.file_name)[1]
        file_n = File_Msg.document.file_unique_id

    file = os.path.join(dl_path, f'{file_n}{ex}')
    File = File_Msg.download(file_name=file)
    return File 

########### Fb Funcs ############

def Fb_Upld(bot, back_id, Creds, upld_fb_dir, pack):
    Page_Id, Page_Prof_id, Access_Token = Creds.split('|')
    Main_Cap = ''
    Media_Msgs = []
    for msg_id in pack: 
        if '-' in str(msg_id): 
            msg_pack = str(msg_id).split('-')
            Sub_Cap = ''
            Media_N = None
            for msg_pack_id in msg_pack: 
                msg = Get_Msg(bot, back_id, msg_pack_id)
                if not msg: continue
                if msg.photo or msg.video: 
                    Media_N = msg
                    if msg.caption:
                        Sub_Cap += msg.caption + Small_line_break
                elif msg.text: 
                    Sub_Cap += msg.text + Small_line_break
                elif msg.document: 
                    if msg.document.file_name and msg.document.file_name.lower().endswith('.txt'):
                        txt_file = File_Dl(msg, upld_fb_dir)
                        with open(txt_file, 'r', encoding='utf-8') as f:
                            Sub_Cap += f.read() + Small_line_break
                        Check_File(txt_file)
                    else:
                        Media_N = msg
                        if msg.caption:
                            Sub_Cap += msg.caption + Small_line_break
            if Media_N:
                fb_path = File_Dl(Media_N, upld_fb_dir)
                Media_id = up_func(Access_Token, Page_Id, Sub_Cap, fb_path)
                Media_Msgs.append([Media_id])
        else: 
            msg = Get_Msg(bot, back_id, int(msg_id))
            if not msg: continue
            if msg.text: 
                Main_Cap += msg.text + Small_line_break
            elif msg.document: 
                if msg.document.file_name and msg.document.file_name.lower().endswith('.txt'):
                    txt_file = File_Dl(msg, upld_fb_dir)
                    with open(txt_file, 'r', encoding='utf-8') as f:
                        Main_Cap += f.read() + Small_line_break
                    Check_File(txt_file)
                else:
                    Media_Msgs.append(msg)
            elif msg.photo or msg.video: 
                Media_Msgs.append(msg)
    
    if len(Media_Msgs) > 1: 
        Feed_Link = upld_album(Access_Token, Page_Id, Page_Prof_id, Media_Msgs, Main_Cap)
    elif len(Media_Msgs) == 1: 
        msgMedia_Cap = Media_Msgs[0].caption if Media_Msgs[0].caption else ' '
        fb_path = File_Dl(Media_Msgs[0], upld_fb_dir)
        Feed_Link = up_func(Access_Token, Page_Id, msgMedia_Cap + Small_line_break + Main_Cap, fb_path, True)
    else: 
        Feed_Link = post_text(Access_Token, Page_Id, Main_Cap)
    return Feed_Link

def delete_post(Access_Token, Page_Id, post_link):
    try:
        post_id = post_link.strip('/').split('/')[-2]
        payload = {'access_token': Access_Token}
        url = f'https://graph.facebook.com/v22.0/{Page_Id}_{post_id}'
        requests.delete(url, data=payload)
    except Exception as e:
        print(f"Delete post error: {e}")

def post_text(Access_Token, Page_Id, text):
    url = f'https://graph.facebook.com/v22.0/{Page_Id}/feed'
    payload = {'access_token': Access_Token, 'message': text}
    res = requests.post(url, data=payload).json()
    feedid = res["id"].split('_')[1]
    return f"https://www.facebook.com/{Page_Id}/posts/{feedid}/"
    
def up_func(Access_Token, Page_Id, Media_Cap, fb_path, publish=False): 
    section = 'photos' if fb_path.lower().endswith(Image_forms) else 'videos'
    cap = 'message' if section == 'photos' else 'description'
        
    with open(fb_path, 'rb') as f:
        files = {'source': f}
        payload = {'access_token': Access_Token.strip(), cap: Media_Cap, 'published': str(publish).lower()}
        url = f'https://graph.facebook.com/v22.0/{Page_Id.strip()}/{section}'
        response = requests.post(url, data=payload, files=files, headers=headers)
        
    res_data = response.json()
    Media_id = res_data.get("id")
    Check_File(fb_path)

    if publish:
        return f"https://www.facebook.com/{Page_Id}/{section}/{Media_id}/"
    return Media_id
  
def upld_album(Access_Token, Page_Id, prof_id, msg_list, Media_Cap):
    file_ids = []
    for msg in msg_list: 
        if not isinstance(msg, list): 
            fb_path = File_Dl(msg, upld_dir)
            file_id = up_func(Access_Token, Page_Id, msg.caption or "", fb_path, publish=False)
        else: 
            file_id = msg[0]
        file_ids.append({"media_fbid": file_id})

    url = f"https://graph.facebook.com/v22.0/{Page_Id}/feed"
    params = {
        "access_token": Access_Token,
        "message": Media_Cap,
        "attached_media": json.dumps(file_ids)
    }
    response = requests.post(url, data=params).json()
    Feed_id = response["id"].split('_')[-1]
    return f"https://www.facebook.com/story.php?story_fbid={Feed_id}&id={prof_id}"

############## Main Bot Funcs ########### 

@bot.on_message(filters.command('start') & filters.private)
def command_start(bot, message):
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
        BotCommand("stat", "عدد الجدولات")
    ])
    message.reply('لبقية البوتات \n\n @sunnaybots \n\n للبدء \n\n /add_platform')

def Get_Item(Page_Posts, Msg_Id):
    if not Page_Posts: return None
    for post in Page_Posts:
        if Msg_Id in post:
            return post

@bot.on_message(filters.command('add_platform') & filters.private)
def command_add_platform(bot, message):
    message.reply("أدخل اسم صفحة الفيسبوك🌿", reply_markup=ForceReply(True))

@bot.on_message(filters.command('skip') & filters.private)
def command_skip(bot, message):
    User_Id = message.from_user.id
    Keys_List = MNDB.Grap_Keys(User_Id)
    if Skip_Key not in Keys_List:
        MNDB.Insert_Key(User_Id, Skip_Key)
    User_Ids = MNDB.Grap_Users()
    if User_Id not in User_Ids:
        message.reply('قم بإضافة قناة أولاً \n\n /add_platform')
        return
    Call_List_Mk(message, User_Id, 'Skip')

@bot.on_message(filters.command('stat') & filters.private)
def command_stat(bot, message):
    User_Id = message.from_user.id
    Reply = f"♦️ مُعرّفك 👈 {User_Id} \n\n"
    Pages_List = MNDB.Grap_Keys(User_Id)
    if Pages_List:
        for Page in Pages_List:
            if Page != 'skip':
                Page_Posts = MNDB.Grap_Values(User_Id, Page).get('Sched', [])
                Posts_Num = len(Page_Posts) if Page_Posts else 0
                Reply += f"🔸 {Page} 👈 {Posts_Num} جدولة \n"
    else:
        Reply += "🔸 لا توجد صفحات مرتبطة بالحساب"
    message.reply(Reply)

@bot.on_message(filters.command('start_accum') & filters.private)
def command_start_accum(bot, message):
    User_Id = message.from_user.id
    Accum.pop(User_Id, None)
    Reply = message.reply('تم تفعيل التجميع 🌿')
    Call_id = Call_List_Mk(message, message.id, 'Schedule')
    Accum[User_Id] = [Reply.id, Call_id]

@bot.on_message(filters.command('clear_accum') & filters.private)
def command_clear_accum(bot, message):
    User_Id = message.from_user.id
    if User_Id in Accum:
        Call_Id = Accum[User_Id][1]
        Reply_Id = Accum[User_Id][0]
        Call_Msg = Get_Msg(bot, User_Id, Call_Id)
        Reply_Msg = Get_Msg(bot, User_Id, Reply_Id)
        if Call_Msg: Call_Msg.delete()
        if Reply_Msg: Reply_Msg.edit_text('تم تعطيل التجميع 🌷')
        Accum.pop(User_Id)

@bot.on_message(filters.command('end_accum') & filters.private)
def command_end_accum(bot, message):
    User_Id = message.from_user.id
    if User_Id in Accum: 
        reply_Id = Accum[User_Id][0]
        if len(Accum[User_Id]) > 2:
            Data = Accum[User_Id][2]
            for Case in Accum[User_Id][3:]:
                Case_Msg = Get_Msg(bot, User_Id, Case)
                if Case_Msg:
                    Copied = Msg_Copy(Case_Msg, Back_Chnl_Id)
                    if Copied: Add_Item(Case_Msg, Data, Copied.id)
        else:
            Call_Id = Accum[User_Id][1]
            Call_Msg = Get_Msg(bot, User_Id, Call_Id)
            if Call_Msg: Call_Msg.delete()
        Reply_Msg = Get_Msg(bot, User_Id, reply_Id)
        if Reply_Msg: Reply_Msg.edit_text('تم تعطيل التجميع 🌷')
        Accum.pop(User_Id)

@bot.on_message(filters.command('start_bulk') & filters.private)
def command_start_bulk(bot, message):
    replied = message.reply('تم تفعيل التجميع 🌿')
    User_Id = message.from_user.id
    Bulking[User_Id] = [replied.id]

@bot.on_message(filters.command('clear_bulk') & filters.private)
def command_clear_bulk(bot, message):
    User_Id = message.from_user.id
    if User_Id in Bulking: 
        Bulking.pop(User_Id)
        message.reply('تم الإلغاء 🌿')

@bot.on_message(filters.command('bulk') & filters.private)
def command_bulk(bot, message):
    User_Id = message.from_user.id
    if User_Id in Bulking: 
        Msg_Ids = message.text[6:].strip()
        if Msg_Ids:
            Msg_Ids = Msg_Ids.replace(' ', '|')
            Bulking[User_Id].append(Msg_Ids)
            Call_List_Mk(message, message.id, 'Schedule')

def Call_List_Mk(message, Msg_Ids, Mode):
    User_Id = message.chat.id
    User_Ids = MNDB.Grap_Users()
    if User_Id not in User_Ids:
        message.reply('قم بإضافة صفحة أولاً \n\n /add_platform')
        return None
    
    Pages_List = MNDB.Grap_Keys(User_Id)
    Page_Buttons = []
    for Page in Pages_List:
        if Page != 'skip':
            Page_Name = Page + '| فيسبوك'
            Page_Buttons.append([InlineKeyboardButton(Page_Name, callback_data=f'{Mode}_{Msg_Ids}_{Page.replace(" ", "|")}')])
    replied = message.reply(text='اختر صفحتك 🌿', reply_markup=InlineKeyboardMarkup(Page_Buttons), quote=True)
    return replied.id

@bot.on_callback_query()
def callback_query(CLIENT, CallbackQuery):
    Callback_List = CallbackQuery.data.split('_')
    Method = Callback_List[0]
    User_Id = CallbackQuery.from_user.id
    Page_Name = Callback_List[2].replace('|', ' ')
  
    if Method == 'Delete': 
        Rpl_Id = Callback_List[1]
        Msg = Get_Msg(bot, User_Id, Rpl_Id)
        if Msg:
            Creds = MNDB.Grap_Values(User_Id, Page_Name).get('Data')[0]
            Creds_List = Creds.split('|')
            delete_post(Creds_List[-1], int(Creds_List[0]), Msg.text)
            CallbackQuery.edit_message_text("تم الحذف 🌿")

    elif Method in ('Cancel', 'Send', 'Schedule', 'Skip'): 
        Msg_Ids = Callback_List[1]
        if Method in ('Cancel', 'Send'): 
            try:
                Page_Posts = MNDB.Grap_Values(User_Id, Page_Name).get('Sched', [])
                Item = Get_Item(Page_Posts, Msg_Ids)
                if Method == 'Send' and Item:
                    Msg_List = Item.split('_')
                    Bulk_List = Msg_List[0].split('|') if '|' in Msg_List[0] else [Msg_List[0]]
                    Creds = MNDB.Grap_Values(User_Id, Page_Name).get('Data')[0]
                    Feed_Link = Fb_Upld(bot, Back_Chnl_Id, Creds, upld_dir, Bulk_List)
                    
                    Rep_Buttons = [[InlineKeyboardButton('حذف', callback_data=f"Delete_{Msg_List[1]}_{Callback_List[2]}")]]
                    CallbackQuery.edit_message_text(text=Feed_Link, reply_markup=InlineKeyboardMarkup(Rep_Buttons))
                elif Method == 'Cancel':
                    CallbackQuery.edit_message_text("تم الحذف 🌿")
                if Item: MNDB.Delete_Item(User_Id, Page_Name + '.Sched', Item)
            except Exception as err:
                print(f"Error in Callback: {err}")
        
        elif Method == 'Skip':
            MNDB.Insert_Item(User_Id, Skip_Key, Page_Name)
            CallbackQuery.edit_message_text("تم التخطي 🌿")
        
        elif Method == 'Schedule':
            Copied = ""
            if User_Id not in Accum:
                Msg_Ids = Bulking[User_Id][1] if User_Id in Bulking else Msg_Ids
                Msgs_Bulk = Msg_Ids.split('|')
                for No, Msg_Mass in enumerate(Msgs_Bulk):
                    if '-' in Msg_Mass:
                        Msg_List = Msg_Mass.split('-')
                        for N, Msg_Id_Item in enumerate(Msg_List): 
                            Msg = Get_Msg(bot, User_Id, Msg_Id_Item)
                            Copy = Msg_Copy(Msg, Back_Chnl_Id)
                            if Copy: Copied += str(Copy.id) + ('-' if N < len(Msg_List)-1 else '')
                    else:
                        if not Msg_Mass.strip(): continue
                        Msg = Get_Msg(bot, User_Id, Msg_Mass)
                        Copy = Msg_Copy(Msg, Back_Chnl_Id)
                        if Copy: Copied += str(Copy.id)
                    Copied += '|'
                Copied = Copied.strip('|')
            
            if User_Id in Accum:
                Accum[User_Id].append(Page_Name)
            elif User_Id in Bulking:
                reply_Id = Bulking[User_Id][0]
                Reply_Msg = Get_Msg(bot, User_Id, reply_Id)
                if Reply_Msg: Reply_Msg.edit_text('تم تعطيل التجميع 🌷')
                Bulking.pop(User_Id)
                Add_Item(CallbackQuery.message, Page_Name, Copied)
            else:
                Add_Item(CallbackQuery.message, Page_Name, Copied)
            CallbackQuery.message.delete()

def Add_Item(Msg, Data, Msg_Id):
    User_Id = Msg.from_user.id if Msg.from_user else Msg.chat.id
    Cancel_Op = [['سحب', 'Cancel'], ['إرسال الآن', 'Send']]
    Cancel_BUTTONS = [[InlineKeyboardButton(Op[0], callback_data=f"{Op[1]}_{Msg_Id}_{Data.replace(' ', '|')}")] for Op in Cancel_Op]
    Replied = Msg_Reply(Msg, 'اختر', Cancel_BUTTONS)
    if Replied:
        Item = f"{Msg_Id}_{Replied.id}"
        MNDB.Insert_Item(User_Id, Data + '.Sched', Item)

@bot.on_message(filters.private & filters.reply)
def refunc(client, message):
    if message.reply_to_message.reply_markup and isinstance(message.reply_to_message.reply_markup, ForceReply):
        User_Id = message.from_user.id
        Msg_Text = message.text
        reply_id = message.reply_to_message_id
        reply_msg = Get_Msg(bot, User_Id, reply_id)
        message.delete()
        
        if reply_msg and 'اسم صفحة' in reply_msg.text:
            Page_Name = Msg_Text.strip()
            Add_Acc_Data = f"أدخل بيانات صفحة الفيسبوك |{Page_Name}\nPage Id\nProfile Id\nAccess Token"
            reply_msg.reply(Add_Acc_Data, reply_markup=ForceReply(True))
            if User_Id not in MNDB.Grap_Users():
                MNDB.Insert_User(User_Id)
            MNDB.Insert_OKey(User_Id, Page_Name)
            reply_msg.delete()
        
        elif reply_msg and 'بيانات' in reply_msg.text:
            Acc_Token = '|'.join(Msg_Text.split('\n'))
            Page_Name = reply_msg.text.split('|')[-1].split('\n')[0].strip()
            MNDB.Insert_Item(User_Id, Page_Name + '.Data', Acc_Token)
            reply_msg.reply('تمت الإضافة بنجاح 🌿')
            reply_msg.delete()

@bot.on_message(filters.incoming & filters.private)
def incoming_messages(bot, message):
    User_Id = message.from_user.id
    if User_Id in Bulking:
        message.reply(message.id, quote=True)
    elif User_Id in Accum:
        Accum[User_Id].append(message.id)
    else:
        Call_List_Mk(message, message.id, 'Schedule')

def Send_Post(Spec=None):
    User_Ids = MNDB.Grap_Users()
    for User in User_Ids:
        Pages_List = MNDB.Grap_Keys(User)
        for Page in Pages_List:
            Skip_Vals = MNDB.Grap_Values(User, Skip_Key) or []
            if (Page not in Skip_Vals and Page != 'skip') if Spec is None else (Page == Spec):
                Page_Posts = MNDB.Grap_Values(User, Page).get('Sched', [])
                if Page_Posts:
                    Post = Page_Posts[0]
                    Msg_List = Post.split('_')
                    Bulk_List = Msg_List[0].split('|') if '|' in Msg_List[0] else [Msg_List[0]]
                    Creds = MNDB.Grap_Values(User, Page).get('Data')[0]
                    try:
                        Feed_Link = Fb_Upld(bot, Back_Chnl_Id, Creds, upld_dir, Bulk_List)
                        Reply_Msg = Get_Msg(bot, User, Msg_List[1])
                        if Reply_Msg:
                            Rep_Buttons = [[InlineKeyboardButton('حذف', callback_data=f"Delete_{Msg_List[1]}_{Page.replace(' ', '|')}")]]
                            Reply_Msg.edit_text(text=Feed_Link, reply_markup=InlineKeyboardMarkup(Rep_Buttons))
                    except Exception as e:
                        print(f"Error in Send_Post: {e}")
                    
                    MNDB.Delete_Item(User, Page + '.Sched', Post)
                    time.sleep(15)
        MNDB.Delete_AllItems(User, Skip_Key)

scheduler = BackgroundScheduler()
scheduler.add_job(Send_Post, "cron", hour=8)
scheduler.start()

bot.run()