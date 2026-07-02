import re
import json
import os
import sys
import random
import asyncio
import string
import time
from datetime import datetime, time as dtime, timedelta
from threading import Thread
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# ============ FLASK FOR RENDER ============
flask_app = Flask(__name__)

@flask_app.route('/')
@flask_app.route('/health')
def health():
    return "KALYUG ESCROW BOT is running!", 200

def run_flask():
    port = int(os.environ.get('PORT', 10000))
    flask_app.run(host='0.0.0.0', port=port)

# ============ CONFIG ============
BOT_TOKEN = "8885172416:AAFRtSo5uGlTSZBBQgU62Xal8XPgu571tjg"
OWNER_ID = 7977493987
ADMIN_IDS = [OWNER_ID]

# Group IDs
GROUP_ID = -1003920615096
JOIN_GROUP_ID = -1002353854365
JOIN_GROUP_LINK = "https://t.me/+5Z_XCSm-BzE4YTJl"

USERS_FILE = "users.json"
DEALS_FILE = "deals.json"
ADMINS_FILE = "admins.json"
CONFIG_FILE = "config.json"
GIFS_FILE = "gifs.json"

# ============ LOAD/SAVE ============
def load_json(filepath, default=None):
    if default is None:
        default = {}
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except:
            return default
    return default

def save_json(filepath, data):
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

# ============ DATA ============
users = load_json(USERS_FILE)
deals = load_json(DEALS_FILE)
admins_data = load_json(ADMINS_FILE, {"approved": [str(OWNER_ID)]})
config = load_json(CONFIG_FILE, {
    "lock_enabled": False,
    "lock_time": None,
    "unlock_time": None,
    "morning_speech": "",
    "locked": False
})
gifs_data = load_json(GIFS_FILE, {"gifs": {}})

if str(OWNER_ID) not in admins_data.get("approved", []):
    admins_data.setdefault("approved", []).append(str(OWNER_ID))
    save_json(ADMINS_FILE, admins_data)

# ============ EMOJI SYSTEM ============
EMOJI_LIST = [
    "✅", "👁️", "👀", "🔥", "💥", "❤️", "💙", "💚", "💛", "💜", "🖤",
    "⭐", "🌟", "✨", "🧛", "👹", "👻", "👿", "👑", "💰", "💵", "💎",
    "👍", "👎", "👏", "😀", "😂", "😍", "😎", "😢", "😡", "🤔",
    "🔒", "🔓", "⚡", "🥃", "🍂", "💀", "❤️‍🔥", "💠", "🎲", "📋",
    "👤", "💳", "⏰", "📝", "📅", "📊", "🛡️", "🔐", "📌", "🔹",
    "👑", "❌", "✅", "📢", "🆔", "💰", "💳"
]

def re():
    return random.choice(EMOJI_LIST)

def wr(text):
    lines = text.split('\n')
    result = []
    for line in lines:
        if line.strip():
            result.append(f"{re()} {line} {re()}")
        else:
            result.append(line)
    return '\n'.join(result)

def fancy(text):
    result = ""
    for c in text:
        if 'A' <= c <= 'Z':
            result += chr(0x1D400 + ord(c) - ord('A'))
        elif 'a' <= c <= 'z':
            result += chr(0x1D41A + ord(c) - ord('a'))
        elif '0' <= c <= '9':
            result += chr(0x1D7CE + ord(c) - ord('0'))
        else:
            result += c
    return result

def gen_deal():
    return "KAL-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def is_adm(uid):
    return str(uid) in admins_data.get("approved", [])

def is_own(uid):
    return uid == OWNER_ID

def reg_user(uid, uname, fname):
    uid_s = str(uid)
    if uid_s not in users:
        users[uid_s] = {"id": uid, "username": uname or "NoUsername", "name": fname, "joined": str(datetime.now())}
        save_json(USERS_FILE, users)

# ============ COMMANDS ============

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    reg_user(u.id, u.username, u.first_name)
    if update.effective_chat.type == "private":
        btn = [[InlineKeyboardButton("🔹 JOIN GROUP 🔹", url=JOIN_GROUP_LINK)]]
        msg = f"""
👋 WELCOME {fancy(u.first_name)}
━━━━━━━━━━━━━━━━━━
Join our group first to use the bot:
👉 {JOIN_GROUP_LINK}
━━━━━━━━━━━━━━━━━━
This bot is for:
• KALYUG ESCROW DEAL FORM
• Deal Management
• Group Lock/Unlock
• Dice Game
━━━━━━━━━━━━━━━━━━
"""
        await update.message.reply_text(wr(msg), parse_mode="HTML", reply_markup=InlineKeyboardMarkup(btn))
    else:
        await update.message.reply_text(f"{re()} Bot is active! {re()}", parse_mode="HTML")

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if update.effective_chat.type == "private" and not is_adm(uid) and not is_own(uid):
        btn = [[InlineKeyboardButton("🔹 JOIN GROUP 🔹", url=JOIN_GROUP_LINK)]]
        await update.message.reply_text(f"Please join the group first:\n{JOIN_GROUP_LINK}", reply_markup=InlineKeyboardMarkup(btn), parse_mode="HTML")
        return
    msg = f"""
KALYUG ESCROW BOT - HELP
━━━━━━━━━━━━━━━━━━
AVAILABLE COMMANDS:
/start - Start bot
/help - This menu
/time - Show current bot time
━━━━━━━━━━━━━━━━━━
ADMIN COMMANDS:
/lock - Lock group
/unlock - Unlock group
/setlock HH:MM - Auto lock
/setunlock HH:MM - Auto unlock
/setspeech text - Set morning speech
/broadcast msg - Broadcast
/send - Send photo/file
/check DEAL_ID - Check deal
/approve UID - Approve admin
/removeadmin UID - Remove admin
/admins - List admins
/dice - Dice Game
/owner - Owner panel
━━━━━━━━━━━━━━━━━━
"""
    await update.message.reply_text(wr(msg), parse_mode="HTML")

async def time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now()
    msg = f"""
BOT TIME
━━━━━━━━━━━━━━━━━━
Date: {fancy(now.strftime("%d %B %Y"))}
Time: {fancy(now.strftime("%I:%M:%S %p"))}
Timezone: IST (UTC+5:30)
━━━━━━━━━━━━━━━━━━
"""
    await update.message.reply_text(wr(msg), parse_mode="HTML")

async def lock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_adm(uid) and not is_own(uid):
        await update.message.reply_text(f"{re()} Admin only! {re()}", parse_mode="HTML")
        return
    try:
        perms = {
            "can_send_messages": False,
            "can_send_media_messages": False,
            "can_send_polls": False,
            "can_send_other_messages": False,
            "can_add_web_page_previews": False,
            "can_change_info": False,
            "can_invite_users": False,
            "can_pin_messages": False
        }
        await context.bot.set_chat_permissions(update.effective_chat.id, perms)
        config["locked"] = True
        save_json(CONFIG_FILE, config)
        speech = config.get("morning_speech", "")
        msg = f"""
🔒 GROUP IS LOCKED 🔒
━━━━━━━━━━━━━━━━━━
Group has been locked by admin!
Only admins can send messages now.
━━━━━━━━━━━━━━━━━━
"""
        if speech:
            msg += f"\n{speech}\n━━━━━━━━━━━━━━━━━━\n"
        await update.message.reply_text(wr(msg), parse_mode="HTML")
    except Exception as e:
        await update.message.reply_text(f"{re()} Error: {str(e)} {re()}", parse_mode="HTML")

async def unlock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_adm(uid) and not is_own(uid):
        await update.message.reply_text(f"{re()} Admin only! {re()}", parse_mode="HTML")
        return
    try:
        perms = {
            "can_send_messages": True,
            "can_send_media_messages": True,
            "can_send_polls": True,
            "can_send_other_messages": True,
            "can_add_web_page_previews": True,
            "can_change_info": False,
            "can_invite_users": True,
            "can_pin_messages": False
        }
        await context.bot.set_chat_permissions(update.effective_chat.id, perms)
        config["locked"] = False
        save_json(CONFIG_FILE, config)
        msg = f"""
🔓 GROUP IS UNLOCKED 🔓
━━━━━━━━━━━━━━━━━━
Group has been unlocked!
Everyone can send messages now.
━━━━━━━━━━━━━━━━━━
"""
        await update.message.reply_text(wr(msg), parse_mode="HTML")
    except Exception as e:
        await update.message.reply_text(f"{re()} Error: {str(e)} {re()}", parse_mode="HTML")

async def setlock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_own(uid) and not is_adm(uid):
        await update.message.reply_text(f"{re()} Admin only! {re()}", parse_mode="HTML")
        return
    if not context.args:
        await update.message.reply_text(f"{re()} Usage: /setlock HH:MM {re()}", parse_mode="HTML")
        return
    try:
        h, m = map(int, context.args[0].split(':'))
        if h < 0 or h > 23 or m < 0 or m > 59:
            raise ValueError
        config["lock_time"] = f"{h:02d}:{m:02d}"
        save_json(CONFIG_FILE, config)
        await update.message.reply_text(f"{re()} Auto-lock set for {fancy(context.args[0])} {re()}", parse_mode="HTML")
    except:
        await update.message.reply_text(f"{re()} Invalid time! Use HH:MM {re()}", parse_mode="HTML")

async def setunlock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_own(uid) and not is_adm(uid):
        await update.message.reply_text(f"{re()} Admin only! {re()}", parse_mode="HTML")
        return
    if not context.args:
        await update.message.reply_text(f"{re()} Usage: /setunlock HH:MM {re()}", parse_mode="HTML")
        return
    try:
        h, m = map(int, context.args[0].split(':'))
        if h < 0 or h > 23 or m < 0 or m > 59:
            raise ValueError
        config["unlock_time"] = f"{h:02d}:{m:02d}"
        save_json(CONFIG_FILE, config)
        await update.message.reply_text(f"{re()} Auto-unlock set for {fancy(context.args[0])} {re()}", parse_mode="HTML")
    except:
        await update.message.reply_text(f"{re()} Invalid time! Use HH:MM {re()}", parse_mode="HTML")

async def setspeech(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_own(uid) and not is_adm(uid):
        await update.message.reply_text(f"{re()} Admin only! {re()}", parse_mode="HTML")
        return
    if not context.args:
        await update.message.reply_text(f"{re()} Usage: /setspeech your text {re()}", parse_mode="HTML")
        return
    config["morning_speech"] = " ".join(context.args)
    save_json(CONFIG_FILE, config)
    await update.message.reply_text(f"{re()} Morning speech set! {re()}", parse_mode="HTML")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_own(uid) and not is_adm(uid):
        await update.message.reply_text(f"{re()} Admin only! {re()}", parse_mode="HTML")
        return
    if not context.args and not update.message.reply_to_message:
        await update.message.reply_text(f"{re()} Usage: /broadcast message {re()}", parse_mode="HTML")
        return
    if update.message.reply_to_message:
        text = update.message.reply_to_message.text or update.message.reply_to_message.caption or ""
    else:
        text = " ".join(context.args)
    if not text:
        await update.message.reply_text(f"{re()} No message! {re()}", parse_mode="HTML")
        return
    await context.bot.send_message(chat_id=GROUP_ID, text=wr(f"📢 BROADCAST 📢\n━━━━━━━━━━━━━━━━━━\n{text}\n━━━━━━━━━━━━━━━━━━"), parse_mode="HTML")
    await update.message.reply_text(f"{re()} Broadcast sent! ✅ {re()}", parse_mode="HTML")

async def send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_own(uid) and not is_adm(uid):
        await update.message.reply_text(f"{re()} Admin only! {re()}", parse_mode="HTML")
        return
    if update.message.reply_to_message and update.message.reply_to_message.photo:
        photo = update.message.reply_to_message.photo[-1].file_id
        caption = " ".join(context.args) if context.args else None
        await context.bot.send_photo(chat_id=GROUP_ID, photo=photo, caption=caption)
        await update.message.reply_text(f"{re()} Photo sent! ✅ {re()}", parse_mode="HTML")
        return
    if not context.args:
        await update.message.reply_text(f"{re()} Usage: /send text or reply to photo {re()}", parse_mode="HTML")
        return
    await context.bot.send_message(chat_id=GROUP_ID, text=wr(f"📢 FROM ADMIN 📢\n━━━━━━━━━━━━━━━━━━\n{' '.join(context.args)}\n━━━━━━━━━━━━━━━━━━"), parse_mode="HTML")
    await update.message.reply_text(f"{re()} Message sent! ✅ {re()}", parse_mode="HTML")

async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_own(uid):
        await update.message.reply_text(f"{re()} Owner only! {re()}", parse_mode="HTML")
        return
    if not context.args:
        await update.message.reply_text(f"{re()} Usage: /approve USER_ID {re()}", parse_mode="HTML")
        return
    tid = context.args[0].strip()
    if tid in admins_data.get("approved", []):
        await update.message.reply_text(f"{re()} Already an admin! {re()}", parse_mode="HTML")
        return
    admins_data.setdefault("approved", []).append(tid)
    save_json(ADMINS_FILE, admins_data)
    await update.message.reply_text(f"{re()} ✅ ADMIN APPROVED ✅ {re()}\nUser ID: {fancy(tid)}", parse_mode="HTML")

async def removeadmin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_own(uid):
        await update.message.reply_text(f"{re()} Owner only! {re()}", parse_mode="HTML")
        return
    if not context.args:
        await update.message.reply_text(f"{re()} Usage: /removeadmin USER_ID {re()}", parse_mode="HTML")
        return
    tid = context.args[0].strip()
    if tid == str(OWNER_ID):
        await update.message.reply_text(f"{re()} Cannot remove owner! {re()}", parse_mode="HTML")
        return
    if tid not in admins_data.get("approved", []):
        await update.message.reply_text(f"{re()} Not an admin! {re()}", parse_mode="HTML")
        return
    admins_data["approved"].remove(tid)
    save_json(ADMINS_FILE, admins_data)
    await update.message.reply_text(f"{re()} ❌ ADMIN REMOVED ❌ {re()}\nUser ID: {fancy(tid)}", parse_mode="HTML")

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(f"{re()} Usage: /check DEAL_ID {re()}", parse_mode="HTML")
        return
    did = context.args[0].strip().upper()
    if did in deals:
        d = deals[did]
        msg = f"""
📋 DEAL FOUND 📋
━━━━━━━━━━━━━━━━━━
🆔 <code>{did}</code>
💰 Amount: {d.get('deal_amount', 'N/A')}
👤 Buyer: {d.get('buyers', 'N/A')}
👤 Seller: {d.get('seller', 'N/A')}
📝 Detail: {d.get('deal_detail', 'N/A')}
⏰ Escrow Till: {d.get('escrow_till', 'N/A')}
📅 Created: {d.get('created_at', 'N/A')}
━━━━━━━━━━━━━━━━━━
"""
        await update.message.reply_text(wr(msg), parse_mode="HTML")
    else:
        await update.message.reply_text(f"{re()} Deal '{did}' not found! {re()}", parse_mode="HTML")

async def dice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    btn = [[InlineKeyboardButton("🎲 SET GIF 🎲", callback_data="set_gif")]]
    await update.message.reply_text(f"{re()} DICE GAME {re()}\n━━━━━━━━━━━━━━━━━━\nClick below to set a GIF with a keyword!\nThen send me a GIF with the keyword", reply_markup=InlineKeyboardMarkup(btn), parse_mode="HTML")

async def owner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_own(update.effective_user.id):
        await update.message.reply_text(f"{re()} Owner only! {re()}", parse_mode="HTML")
        return
    tu = len(users)
    td = len(deals)
    ta = len(admins_data.get("approved", []))
    ls = "🔒 Locked" if config.get("locked") else "🔓 Unlocked"
    msg = f"""
👑 OWNER PANEL 👑
━━━━━━━━━━━━━━━━━━
📊 STATISTICS:
👥 Users: {tu}
📋 Deals: {td}
🛡️ Admins: {ta}
🔐 Group: {ls}
━━━━━━━━━━━━━━━━━━
📌 COMMANDS:
🔹 /lock
🔹 /unlock
🔹 /setlock HH:MM
🔹 /setunlock HH:MM
🔹 /setspeech
🔹 /broadcast
🔹 /approve ID
🔹 /removeadmin ID
🔹 /check DEAL_ID
🔹 /time
━━━━━━━━━━━━━━━━━━
⏰ Lock: {config.get('lock_time', 'None')}
⏰ Unlock: {config.get('unlock_time', 'None')}
━━━━━━━━━━━━━━━━━━
"""
    await update.message.reply_text(wr(msg), parse_mode="HTML")

async def admins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_own(uid) and not is_adm(uid):
        await update.message.reply_text(f"{re()} Admin only! {re()}", parse_mode="HTML")
        return
    al = admins_data.get("approved", [])
    msg = f"ADMIN LIST\n━━━━━━━━━━━━━━━━━━\n"
    for i, aid in enumerate(al, 1):
        ot = " 👑" if aid == str(OWNER_ID) else ""
        ui = users.get(aid, {})
        un = ui.get('username', 'None')
        msg += f"{i}. 🆔 {aid}\n   @{un}{ot}\n\n"
    msg += "━━━━━━━━━━━━━━━━━━"
    await update.message.reply_text(wr(msg), parse_mode="HTML")

# ============ CALLBACK ============
async def button_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if q.data == "set_gif":
        uid = update.effective_user.id
        if not is_own(uid) and not is_adm(uid):
            await q.edit_message_text(f"{re()} Admin only! {re()}", parse_mode="HTML")
            return
        context.user_data["awaiting_gif_keyword"] = True
        await q.edit_message_text(f"{re()} SEND GIF KEYWORD {re()}\n━━━━━━━━━━━━━━━━━━\nSend me a keyword for your GIF\nExample: welcome\n━━━━━━━━━━━━━━━━━━", parse_mode="HTML")

# ============ DEAL PARSER ============
def parse_deal(text):
    data = {}
    lines = text.split('\n')
    current_key = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Check for various field patterns
        if 'AMOUNT' in line.upper() or '𝘼𝙈𝙊𝙐𝙉𝙏' in line:
            parts = line.split(':-') if ':-' in line else line.split(':') if ':' in line else line.split('-') if '-' in line else [line]
            if len(parts) > 1:
                data['deal_amount'] = parts[1].strip()
            else:
                data['deal_amount'] = 'N/A'
        elif 'BUYER' in line.upper() or '𝘽𝙐𝙔𝙀𝙍' in line:
            parts = line.split(':-') if ':-' in line else line.split(':') if ':' in line else line.split('-') if '-' in line else [line]
            if len(parts) > 1:
                val = parts[1].strip()
                val = val.replace('@', '@')
                data['buyers'] = val
            else:
                data['buyers'] = 'N/A'
        elif 'SELLER' in line.upper() or '𝙎𝙀𝙇𝙇𝙀𝙍' in line:
            parts = line.split(':-') if ':-' in line else line.split(':') if ':' in line else line.split('-') if '-' in line else [line]
            if len(parts) > 1:
                val = parts[1].strip()
                val = val.replace('@', '@')
                data['seller'] = val
            else:
                data['seller'] = 'N/A'
        elif 'DETAIL' in line.upper() or '𝘿𝙀𝙏𝘼𝙄𝙇' in line:
            parts = line.split(':-') if ':-' in line else line.split(':') if ':' in line else line.split('-') if '-' in line else [line]
            if len(parts) > 1:
                data['deal_detail'] = parts[1].strip()
            else:
                data['deal_detail'] = 'N/A'
        elif 'RLS' in line.upper() or '𝙍𝙇𝙎' in line:
            parts = line.split(':-') if ':-' in line else line.split(':') if ':' in line else line.split('-') if '-' in line else [line]
            if len(parts) > 1:
                data['rls_upi'] = parts[1].strip()
            else:
                data['rls_upi'] = 'N/A'
        elif 'CONDITION' in line.upper() or '𝘾𝙊𝙉𝘿𝙄𝙏𝙄𝙊𝙉' in line:
            parts = line.split(':-') if ':-' in line else line.split(':') if ':' in line else line.split('-') if '-' in line else [line]
            if len(parts) > 1:
                data['condition'] = parts[1].strip()
            else:
                data['condition'] = 'N/A'
        elif 'TILL' in line.upper() or '𝙏𝙄𝙇𝙇' in line:
            parts = line.split(':-') if ':-' in line else line.split(':') if ':' in line else line.split('-') if '-' in line else [line]
            if len(parts) > 1:
                data['escrow_till'] = parts[1].strip()
            else:
                data['escrow_till'] = 'N/A'
    
    return data

async def handle_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    text = update.message.text
    chat_id = update.effective_chat.id
    if chat_id != GROUP_ID:
        return
    
    # Check for deal form
    has_deal = 'DEAL' in text.upper()
    has_field = any(f in text.upper() for f in ['AMOUNT', 'BUYER', 'SELLER', 'DETAIL', 'RLS', 'CONDITION', 'TILL'])
    
    if not (has_deal and has_field):
        return
    
    data = parse_deal(text)
    buyers = data.get('buyers', '').strip()
    seller = data.get('seller', '').strip()
    
    if not buyers and not seller:
        return
    
    did = gen_deal()
    deals[did] = {
        "deal_amount": data.get('deal_amount', 'N/A'),
        "buyers": buyers,
        "seller": seller,
        "deal_detail": data.get('deal_detail', 'N/A'),
        "rls_upi": data.get('rls_upi', 'N/A'),
        "condition": data.get('condition', 'N/A'),
        "escrow_till": data.get('escrow_till', 'N/A'),
        "created_at": datetime.now().strftime("%d-%m-%Y %I:%M %p"),
        "created_by": update.effective_user.id
    }
    save_json(DEALS_FILE, deals)
    
    msg = f"""
✅ DEAL ID CREATED ✅
━━━━━━━━━━━━━━━━━━
🆔 <code>{did}</code> (Tap to copy)
💰 Deal Amount: {data.get('deal_amount', 'N/A')}
👤 Buyer: {buyers}
👤 Seller: {seller}
📝 Deal Detail: {data.get('deal_detail', 'N/A')}
💳 RLS UPI: {data.get('rls_upi', 'N/A')}
📋 Condition: {data.get('condition', 'N/A')}
⏰ Escrow Till: {data.get('escrow_till', 'N/A')}
━━━━━━━━━━━━━━━━━━
ESCROW FEES IS NON - REFUNDABLE
RG : @KALYUGESCROWSERVICE
━━━━━━━━━━━━━━━━━━
"""
    await update.message.reply_text(wr(msg), parse_mode="HTML")
    
    # Send to admins
    for aid in admins_data.get("approved", []):
        try:
            amsg = f"""
📋 NEW DEAL FORM 📋
━━━━━━━━━━━━━━━━━━
🆔 <code>{did}</code>
💰 Amount: {data.get('deal_amount', 'N/A')}
👤 Buyer: {buyers}
👤 Seller: {seller}
👤 Posted by: @{update.effective_user.username or 'None'}
━━━━━━━━━━━━━━━━━━
"""
            await context.bot.send_message(chat_id=int(aid), text=wr(amsg), parse_mode="HTML")
        except:
            pass

async def handle_private(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or update.effective_chat.type != "private":
        return
    
    uid = update.effective_user.id
    text = update.message.text
    
    if not text:
        if update.message.animation and context.user_data.get("awaiting_gif_file"):
            kw = context.user_data.get("gif_keyword", "")
            if kw:
                gifs_data["gifs"][kw] = update.message.animation.file_id
                save_json(GIFS_FILE, gifs_data)
                context.user_data["awaiting_gif_keyword"] = False
                context.user_data["awaiting_gif_file"] = False
                context.user_data["gif_keyword"] = ""
                await update.message.reply_text(f"✅ GIF SAVED!\nKeyword: {kw}\nUse /dice {kw} in group", parse_mode="HTML")
            return
        return
    
    if text.lower() in gifs_data.get("gifs", {}):
        gif_id = gifs_data["gifs"][text.lower()]
        await context.bot.send_animation(chat_id=GROUP_ID, animation=gif_id)
        await update.message.reply_text(f"✅ GIF sent to group!", parse_mode="HTML")
        return
    
    if context.user_data.get("awaiting_gif_keyword"):
        kw = text.strip().lower()
        context.user_data["gif_keyword"] = kw
        context.user_data["awaiting_gif_keyword"] = False
        context.user_data["awaiting_gif_file"] = True
        await update.message.reply_text(f"✅ Keyword saved: {kw}\nNow send me a GIF!", parse_mode="HTML")
        return

# ============ AUTO LOCK/UNLOCK ============
async def auto_check(context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now()
    ct = now.strftime("%H:%M")
    
    lt = config.get("lock_time")
    ut = config.get("unlock_time")
    
    if lt and ct == lt and not config.get("locked"):
        try:
            perms = {
                "can_send_messages": False,
                "can_send_media_messages": False,
                "can_send_polls": False,
                "can_send_other_messages": False,
                "can_add_web_page_previews": False,
                "can_change_info": False,
                "can_invite_users": False,
                "can_pin_messages": False
            }
            await context.bot.set_chat_permissions(GROUP_ID, perms)
            config["locked"] = True
            save_json(CONFIG_FILE, config)
            speech = config.get("morning_speech", "")
            m = f"🔒 AUTO LOCKED 🔒\n━━━━━━━━━━━━━━━━━━\nGroup has been auto-locked!\n━━━━━━━━━━━━━━━━━━"
            if speech:
                m += f"\n{speech}\n━━━━━━━━━━━━━━━━━━\n"
            await context.bot.send_message(chat_id=GROUP_ID, text=wr(m), parse_mode="HTML")
        except:
            pass
    
    if ut and ct == ut and config.get("locked"):
        try:
            perms = {
                "can_send_messages": True,
                "can_send_media_messages": True,
                "can_send_polls": True,
                "can_send_other_messages": True,
                "can_add_web_page_previews": True,
                "can_change_info": False,
                "can_invite_users": True,
                "can_pin_messages": False
            }
            await context.bot.set_chat_permissions(GROUP_ID, perms)
            config["locked"] = False
            save_json(CONFIG_FILE, config)
            await context.bot.send_message(chat_id=GROUP_ID, text=wr("🔓 AUTO UNLOCKED 🔓\n━━━━━━━━━━━━━━━━━━\nGroup has been auto-unlocked!\n━━━━━━━━━━━━━━━━━━"), parse_mode="HTML")
        except:
            pass

# ============ MAIN ============
def main():
    Thread(target=run_flask, daemon=True).start()
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help))
    app.add_handler(CommandHandler("time", time))
    app.add_handler(CommandHandler("lock", lock))
    app.add_handler(CommandHandler("unlock", unlock))
    app.add_handler(CommandHandler("setlock", setlock))
    app.add_handler(CommandHandler("setunlock", setunlock))
    app.add_handler(CommandHandler("setspeech", setspeech))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("send", send))
    app.add_handler(CommandHandler("approve", approve))
    app.add_handler(CommandHandler("removeadmin", removeadmin))
    app.add_handler(CommandHandler("check", check))
    app.add_handler(CommandHandler("dice", dice))
    app.add_handler(CommandHandler("owner", owner))
    app.add_handler(CommandHandler("admins", admins))
    
    app.add_handler(CallbackQueryHandler(button_cb))
    app.add_handler(MessageHandler(filters.TEXT & filters.Chat(GROUP_ID), handle_group))
    app.add_handler(MessageHandler(filters.TEXT & filters.PRIVATE, handle_private))
    app.add_handler(MessageHandler(filters.ANIMATION & filters.PRIVATE, handle_private))
    
    job_q = app.job_queue
    job_q.run_repeating(auto_check, interval=60, first=10)
    
    print("=" * 50)
    print("KALYUG ESCROW BOT STARTED!")
    print(f"Owner: {OWNER_ID}")
    print(f"Group: {GROUP_ID}")
    print("Bot is ready!")
    print("=" * 50)
    
    app.run_polling()

if __name__ == "__main__":
    main()