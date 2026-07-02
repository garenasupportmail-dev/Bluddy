import re
import os
import json
import random
import threading
from uuid import uuid4
from datetime import datetime
from flask import Flask, jsonify
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, ContextTypes, CallbackQueryHandler
)

# ======================== FLASK FOR RENDER ========================
flask_app = Flask(__name__)

@flask_app.route('/')
@flask_app.route('/health')
def health():
    return jsonify({"status": "ok", "bot": "running", "time": str(datetime.now())}), 200

def run_flask():
    port = int(os.environ.get('PORT', 5000))
    flask_app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

# ======================== CONFIG ========================
BOT_TOKEN = "8885172416:AAFRtSo5uGlTSZBBQgU62Xal8XPgu571tjg"
OWNER_ID = 7977493987
ADMIN_IDS = [OWNER_ID]
CHANNEL_LINK = "@KALYUGESCROWSERVICE"

USERS_FILE = "users.json"
BANNED_FILE = "banned.json"
DEALS_FILE = "deals.json"

# ======================== EXACT STYLISH ALPHABETS ========================
BOLD_CAPS = "𝐀𝐁𝐂𝐃𝐄𝐅𝐆𝐇𝐈𝐉𝐊𝐋𝐌𝐍𝐎𝐏𝐐𝐑𝐒𝐓𝐔𝐕𝐖𝐗𝐘𝐙"
BOLD_SMALL = "𝐚𝐛𝐜𝐝𝐞𝐟𝐠𝐡𝐢𝐣𝐤𝐥𝐦𝐧𝐨𝐩𝐪𝐫𝐬𝐭𝐮𝐯𝐰𝐱𝐲𝐳"
BOLD_DIGITS = "𝟎𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗"
NORMAL_CAPS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
NORMAL_SMALL = "abcdefghijklmnopqrstuvwxyz"
NORMAL_DIGITS = "0123456789"

FANCY_MAP = {}
for n, f in zip(NORMAL_CAPS, BOLD_CAPS): FANCY_MAP[n] = f
for n, f in zip(NORMAL_SMALL, BOLD_SMALL): FANCY_MAP[n] = f
for n, f in zip(NORMAL_DIGITS, BOLD_DIGITS): FANCY_MAP[n] = f

def to_fancy(text):
    return ''.join(FANCY_MAP.get(c, c) for c in text)

# ======================== PREMIUM EMOJIS (SIRF YAHI USE HONGE) ========================
PREMIUM_EMOJIS = {
    "verified": {"id": "6246537187614005254", "fallback": "✅"},
    "fire": {"id": "4956222745814762495", "fallback": "🔥"},
    "heart": {"id": "5783157259152397008", "fallback": "❤️"},
    "heart_red": {"id": "5801084710343938087", "fallback": "❤️"},
    "heart_pink": {"id": "6010280773351904888", "fallback": "❤️"},
    "heart_blue": {"id": "5780496071645991525", "fallback": "💙"},
    "heart_green": {"id": "5888789252493283486", "fallback": "💚"},
    "heart_purple": {"id": "5840265018655703965", "fallback": "💜"},
    "crown": {"id": "5794422335599546668", "fallback": "👑"},
    "star": {"id": "6244496562752331516", "fallback": "⭐"},
    "star_gold": {"id": "5904618938578243567", "fallback": "⭐"},
    "star_glow": {"id": "6010156854955480259", "fallback": "🌟"},
    "sparkle": {"id": "6010338729640596556", "fallback": "✨"},
    "diamond": {"id": "6086778246882399112", "fallback": "💎"},
    "money": {"id": "6089104607328342288", "fallback": "💰"},
    "money_bag": {"id": "6086730718774300509", "fallback": "💰"},
    "dollar": {"id": "6089140105233044310", "fallback": "💵"},
    "bolt": {"id": "5791970059597386804", "fallback": "⚡"},
    "zap": {"id": "6087079590377820415", "fallback": "⚡"},
    "like": {"id": "6089313931149448495", "fallback": "👍"},
    "clap": {"id": "6093744967304352336", "fallback": "👏"},
    "smile": {"id": "6093864814071780526", "fallback": "😀"},
    "laugh": {"id": "5782741660936966676", "fallback": "😂"},
    "wink": {"id": "6089024570612781324", "fallback": "😉"},
    "heart_eyes": {"id": "6010179687001625256", "fallback": "😍"},
    "cool": {"id": "6032853480782172520", "fallback": "😎"},
    "devil": {"id": "6035242444671421879", "fallback": "👿"},
    "cry": {"id": "5783024321324651865", "fallback": "😭"},
    "flex": {"id": "6147464060305676048", "fallback": "😎"},
    "sigma": {"id": "6235620067942341623", "fallback": "🥃"},
    "don": {"id": "6235717714023814969", "fallback": "🍂"},
    "skills": {"id": "6235593671073339928", "fallback": "💀"},
    "heart_fire": {"id": "6147617184479711380", "fallback": "❤️‍🔥"},
    "eye": {"id": "6035338338406242050", "fallback": "👁️"},
}

def get_emoji_html(name):
    name = name.lower().strip()
    if name in PREMIUM_EMOJIS:
        return f'<tg-emoji emoji-id="{PREMIUM_EMOJIS[name]["id"]}">{PREMIUM_EMOJIS[name]["fallback"]}</tg-emoji>'
    return ""

def get_random_emoji():
    return get_emoji_html(random.choice(list(PREMIUM_EMOJIS.keys())))

def random_emoji_borders(text):
    lines = text.split('\n')
    result = []
    for line in lines:
        if line.strip():
            e1, e2 = get_random_emoji(), get_random_emoji()
            result.append(f"{e1} {line} {e2}")
        else:
            result.append(line)
    return '\n'.join(result)

# ======================== DATA MANAGEMENT ========================
def load_json(filepath, default=None):
    if default is None:
        default = {} if 'user' in filepath else []
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except:
            pass
    return default

def save_json(filepath, data):
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

users = load_json(USERS_FILE, {})
banned = load_json(BANNED_FILE, [])
deals = load_json(DEALS_FILE, {})

def register_user(user_id, username, first_name):
    uid = str(user_id)
    if uid not in users:
        users[uid] = {"id": user_id, "username": username, "name": first_name, "joined": str(datetime.now())}
        save_json(USERS_FILE, users)

def is_owner(user_id):
    return user_id == OWNER_ID

def is_admin(user_id):
    return user_id in ADMIN_IDS or user_id == OWNER_ID

def is_banned(user_id):
    return str(user_id) in banned

def create_deal(data):
    did = str(uuid4())[:8].upper()
    data["deal_id"] = did
    data["status"] = "active"
    data["created_at"] = str(datetime.now())
    deals[did] = data
    save_json(DEALS_FILE, deals)
    return did

def get_deal(did):
    return deals.get(did.upper())

def cancel_deal(did):
    did = did.upper()
    if did in deals:
        deals[did]["status"] = "cancelled"
        save_json(DEALS_FILE, deals)
        return True
    return False

# ======================== FORM PARSER ========================
def parse_deal_form(text):
    data = {}
    is_form = False
    if re.search(r'escrow.*deal.*form', text, re.IGNORECASE): is_form = True
    elif re.search(r'deal.*amount', text, re.IGNORECASE) and re.search(r'buyer|seller', text, re.IGNORECASE): is_form = True
    
    if not is_form: return None
    
    pats = {
        "amount": [r'(?:amount|𝐀𝐌𝐎𝐔𝐍𝐓)[\s:：]*([^\n]+)'],
        "buyer": [r'(?:buyer[s]?|𝐁𝐔𝐘𝐄𝐑)[\s:：]*([^\n]+)'],
        "seller": [r'(?:seller|𝐒𝐄𝐋𝐋𝐄𝐑)[\s:：]*([^\n]+)'],
        "detail": [r'(?:detail|𝐃𝐄𝐓𝐀𝐈𝐋)[\s:：]*([^\n]+)'],
        "condition": [r'(?:condition|𝐂𝐎𝐍𝐃𝐈𝐓𝐈𝐎𝐍)[\s:：]*([^\n]+)'],
        "escrow_till": [r'(?:till|𝐓𝐈𝐋𝐋)[\s:：]*([^\n]+)'],
        "rls_upi": [r'(?:upi|𝐔𝐏𝐈)[\s:：]*([^\n]+)'],
        "rg": [r'(?:rg|𝐑𝐆)[\s:：]*([^\n]+)']
    }
    
    for key, plist in pats.items():
        for p in plist:
            m = re.search(p, text, re.IGNORECASE | re.MULTILINE)
            if m: data[key] = m.group(1).strip(); break
    
    if re.search(r'non.*refundable', text, re.IGNORECASE): data["fee_non_refundable"] = True
    return data if data else None

# ======================== DEAL CARD ========================
def build_deal_card(data, deal_id):
    amt = data.get("amount", "𝐍/𝐀")
    buyer = data.get("buyer", "𝐍/𝐀")
    seller = data.get("seller", "𝐍/𝐀")
    detail = data.get("detail", "𝐍/𝐀")
    cond = data.get("condition", "𝐍/𝐀")
    till = data.get("escrow_till", "𝐍/𝐀")
    upi = data.get("rls_upi", "")
    fee = data.get("fee_non_refundable", False)
    rg = data.get("rg", "")
    now = datetime.now().strftime("%I:%M %p | %d %b %Y")
    
    card = f"""👑 {to_fancy('KALYUG ESCROW DEAL FORM')} 👑

{to_fancy('━━━━━━━━━━━━━━━━━━━━')}
{get_emoji_html('verified')} {to_fancy('Deal ID')}: <code>{deal_id}</code>
{get_emoji_html('heart_blue')} {to_fancy('Status')}: {to_fancy('Active')}
{to_fancy('━━━━━━━━━━━━━━━━━━━━')}

💰 {to_fancy('Amount')}: <b>{amt}</b>
👤 {to_fancy('Buyer')}: {buyer}
👤 {to_fancy('Seller')}: {seller}
📋 {to_fancy('Detail')}: {detail}
✅ {to_fancy('Condition')}: {cond}
⏳ {to_fancy('Escrow Till')}: {till}
"""
    if upi: card += f'\n💳 {to_fancy("RLS UPI")}: ||{upi}||\n'
    if fee: card += f'\n⚠️ {to_fancy("ESCROW FEE NON-REFUNDABLE")}\n'
    if rg: card += f'\n📞 {to_fancy("RG")}: {rg}\n'
    
    card += f"""
{to_fancy('━━━━━━━━━━━━━━━━━━━━')}
🕐 {now}
{get_emoji_html('heart_fire')} {to_fancy('Join')}: {CHANNEL_LINK} {get_emoji_html('heart_fire')}"""
    return card

# ======================== COMMANDS ========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if is_banned(user.id): return await update.message.reply_text(f"❌ {to_fancy('Banned')}")
    register_user(user.id, user.username or "-", user.first_name)
    text = f"""👑 {to_fancy('KALYUG ESCROW BOT')} 👑
{to_fancy('━━━━━━━━━━━━━━━━━━━━')}
👋 {to_fancy('Hey')} <b>{user.first_name}</b>!
{get_emoji_html('star_glow')} {to_fancy('Escrow Deal + Dice + Coin Bot')}
{to_fancy('━━━━━━━━━━━━━━━━━━━━')}
🎲 /dice {to_fancy('- Roll dice')}
🪙 /flipcoin {to_fancy('- Flip coin')}
📋 /owner {to_fancy('- Owner panel')}
{to_fancy('━━━━━━━━━━━━━━━━━━━━')}
{get_emoji_html('heart_fire')} {CHANNEL_LINK}"""
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(f"📢 {to_fancy('Join')} {CHANNEL_LINK}", url=f"https://t.me/{CHANNEL_LINK.replace('@','')}")]])
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=keyboard)

async def dice_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if is_banned(uid): return await update.message.reply_text(f"❌ {to_fancy('Banned')}")
    try:
        m = await context.bot.get_chat_member(CHANNEL_LINK, uid)
        if m.status not in ["member", "administrator", "creator"]:
            kb = InlineKeyboardMarkup([[InlineKeyboardButton(f"📢 {to_fancy('Join')} {CHANNEL_LINK}", url=f"https://t.me/{CHANNEL_LINK.replace('@','')}")]])
            return await update.message.reply_text(f"⚠️ {to_fancy('Please join')} {CHANNEL_LINK}", reply_markup=kb)
    except: pass
    result = random.randint(1, 6)
    ds = ["⚀","⚁","⚂","⚃","⚄","⚅"]
    context.bot_data["dice_last"] = result
    text = f"""✨ {to_fancy('DICE ROLLED')} ✨
{to_fancy('━━━━━━━━━━━━━━')}
🎯 {to_fancy('Result')}: <b>{to_fancy(str(result))}</b> {ds[result-1]}
╔══════════╗
║   {ds[result-1]}   ║
║  <b>{to_fancy(str(result))}</b>  ║
╚══════════╝
{to_fancy('Rolled by')}: {update.effective_user.first_name}
{get_emoji_html('heart_fire')} {CHANNEL_LINK}"""
    kb = InlineKeyboardMarkup([[InlineKeyboardButton(f"📢 {CHANNEL_LINK}", url=f"https://t.me/{CHANNEL_LINK.replace('@','')}")]])
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=kb)

async def flipcoin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if is_banned(uid): return await update.message.reply_text(f"❌ {to_fancy('Banned')}")
    try:
        m = await context.bot.get_chat_member(CHANNEL_LINK, uid)
        if m.status not in ["member", "administrator", "creator"]:
            kb = InlineKeyboardMarkup([[InlineKeyboardButton(f"📢 {to_fancy('Join')} {CHANNEL_LINK}", url=f"https://t.me/{CHANNEL_LINK.replace('@','')}")]])
            return await update.message.reply_text(f"⚠️ {to_fancy('Please join')} {CHANNEL_LINK}", reply_markup=kb)
    except: pass
    result = random.choice(["HEAD","TAIL"])
    ce = "🦅" if result == "HEAD" else "🪙"
    context.bot_data["coin_last"] = result
    text = f"""💎 {to_fancy('COIN FLIPPED')} 💎
{to_fancy('━━━━━━━━━━━━━━')}
🪙 {to_fancy('Result')}: <b>{to_fancy(result)}</b> {ce}
╔══════════════╗
║   {ce}       ║
║  <b>{to_fancy(result)}</b>  ║
╚══════════════╝
{to_fancy('Flipped by')}: {update.effective_user.first_name}
{get_emoji_html('heart_fire')} {CHANNEL_LINK}"""
    kb = InlineKeyboardMarkup([[InlineKeyboardButton(f"📢 {CHANNEL_LINK}", url=f"https://t.me/{CHANNEL_LINK.replace('@','')}")]])
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=kb)

async def showdice_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id): return await update.message.reply_text(f"❌ {to_fancy('Owner only')}")
    last = context.bot_data.get("dice_last")
    if last is None: return await update.message.reply_text(f"⚠️ {to_fancy('No dice yet')}")
    await update.message.reply_text(f"🔮 {to_fancy('Dice result')}: <b>{to_fancy(str(last))}</b>", parse_mode="HTML")

async def showcoin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id): return await update.message.reply_text(f"❌ {to_fancy('Owner only')}")
    last = context.bot_data.get("coin_last")
    if last is None: return await update.message.reply_text(f"⚠️ {to_fancy('No coin yet')}")
    await update.message.reply_text(f"🔮 {to_fancy('Coin result')}: <b>{to_fancy(last)}</b>", parse_mode="HTML")

async def owner_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id): return await update.message.reply_text(f"❌ {to_fancy('Owner only')}")
    text = f"""👑 {to_fancy('OWNER PANEL')} 👑
{to_fancy('━━━━━━━━━━━━━━━━━━━━')}
📊 {to_fancy('Users')}: {len(users)}
🚫 {to_fancy('Banned')}: {len(banned)}
📦 {to_fancy('Deals')}: {len(deals)}
📦 {to_fancy('Emojis')}: {len(PREMIUM_EMOJIS)}
{to_fancy('━━━━━━━━━━━━━━━━━━━━')}
🔮 /showdice {to_fancy('- See dice result')}
🔮 /showcoin {to_fancy('- See coin result')}
👥 /users {to_fancy('- List users')}
🚫 /ban ID
✅ /unban ID
📦 /deals {to_fancy('- List deals')}
📦 /deal ID {to_fancy('- View deal')}
👑 @iflexvenom"""
    await update.message.reply_text(text, parse_mode="HTML")

async def list_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id): return await update.message.reply_text(f"❌ {to_fancy('Owner only')}")
    if not users: return await update.message.reply_text(f"📭 {to_fancy('No users')}")
    pts = [f"🆔 <code>{u}</code> | @{d.get('username','-')} | {'🚫' if u in banned else '✅'}" for u,d in users.items()]
    for ch in [pts[i:i+20] for i in range(0, len(pts), 20)]:
        await update.message.reply_text(f"👥 {to_fancy('Users')} ({len(users)})\n{to_fancy('━━━━━━━━━━━━━━━━━━━━')}\n" + '\n'.join(ch), parse_mode="HTML")

async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id): return await update.message.reply_text(f"❌ {to_fancy('Owner only')}")
    if not context.args: return await update.message.reply_text(f"📝 {to_fancy('Usage')}: /ban ID")
    uid = context.args[0]
    if uid == str(OWNER_ID): return await update.message.reply_text(f"❌ {to_fancy('Cannot ban owner')}")
    if uid not in banned: banned.append(uid); save_json(BANNED_FILE, banned); await update.message.reply_text(f"✅ <code>{uid}</code> {to_fancy('banned')}", parse_mode="HTML")
    else: await update.message.reply_text(f"⚠️ {to_fancy('Already banned')}")

async def unban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id): return await update.message.reply_text(f"❌ {to_fancy('Owner only')}")
    if not context.args: return await update.message.reply_text(f"📝 {to_fancy('Usage')}: /unban ID")
    uid = context.args[0]
    if uid in banned: banned.remove(uid); save_json(BANNED_FILE, banned); await update.message.reply_text(f"✅ <code>{uid}</code> {to_fancy('unbanned')}", parse_mode="HTML")
    else: await update.message.reply_text(f"⚠️ {to_fancy('Not banned')}")

async def list_deals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id): return await update.message.reply_text(f"❌ {to_fancy('Owner only')}")
    if not deals: return await update.message.reply_text(f"📭 {to_fancy('No deals')}")
    pts = [f"🆔 <code>{d}</code> | 💰 {v.get('amount','N/A')} | 👤 {v.get('buyer','N/A')} | 📌 {v.get('status','active')}" for d,v in deals.items()]
    for ch in [pts[i:i+15] for i in range(0, len(pts), 15)]:
        await update.message.reply_text(f"📋 {to_fancy('Deals')} ({len(deals)})\n{to_fancy('━━━━━━━━━━━━━━━━━━━━')}\n" + '\n'.join(ch), parse_mode="HTML")

async def view_deal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id): return await update.message.reply_text(f"❌ {to_fancy('Owner only')}")
    if not context.args: return await update.message.reply_text(f"📝 {to_fancy('Usage')}: /deal ID")
    d = get_deal(context.args[0])
    if d: await update.message.reply_text(build_deal_card(d, d["deal_id"]), parse_mode="HTML")
    else: await update.message.reply_text(f"❌ {to_fancy('Deal not found')}")

# ======================== DEAL FORM HANDLER ========================
async def handle_deal_form(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg or not msg.text: return
    
    data = parse_deal_form(msg.text)
    if not data: return
    
    did = create_deal(data)
    card = build_deal_card(data, did)
    
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"📋 {to_fancy('Copy ID')}", callback_data=f"copy_{did}"),
         InlineKeyboardButton(f"👁️ {to_fancy('View')}", callback_data=f"view_{did}")],
        [InlineKeyboardButton(f"❌ {to_fancy('Cancel')}", callback_data=f"cancel_{did}")],
        [InlineKeyboardButton(f"📢 {CHANNEL_LINK}", url=f"https://t.me/{CHANNEL_LINK.replace('@','')}")]
    ])
    
    await msg.reply_text(card, parse_mode="HTML", reply_markup=kb)
    
    adm_msg = f"""✅ <b>{to_fancy('NEW DEAL')}</b> ✅
🆔 <code>{did}</code>
👤 {msg.from_user.first_name}
💰 {data.get('amount','N/A')}
👤 {data.get('buyer','N/A')}
👤 {data.get('seller','N/A')}"""
    adm_kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"❌ {to_fancy('Cancel')}", callback_data=f"cancel_{did}")],
        [InlineKeyboardButton(f"📢 {CHANNEL_LINK}", url=f"https://t.me/{CHANNEL_LINK.replace('@','')}")]
    ])
    for a in ADMIN_IDS:
        try: await context.bot.send_message(a, adm_msg, parse_mode="HTML", reply_markup=adm_kb)
        except: pass
    if OWNER_ID not in ADMIN_IDS:
        try: await context.bot.send_message(OWNER_ID, adm_msg, parse_mode="HTML", reply_markup=adm_kb)
        except: pass

# ======================== CALLBACK ========================
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    d = q.data
    if d.startswith("copy_"): await q.message.reply_text(f"📋 <b>{to_fancy('Deal ID')}</b>: <code>{d.replace('copy_','')}</code>", parse_mode="HTML")
    elif d.startswith("view_"):
        dl = get_deal(d.replace("view_",""))
        if dl: await q.message.reply_text(build_deal_card(dl, dl["deal_id"]), parse_mode="HTML")
        else: await q.message.reply_text(f"❌ {to_fancy('Deal not found')}")
    elif d.startswith("cancel_"):
        if not is_admin(update.effective_user.id): return await q.message.reply_text(f"❌ {to_fancy('Admins only')}")
        if cancel_deal(d.replace("cancel_","")): await q.message.reply_text(f"✅ {to_fancy('Deal cancelled')}", parse_mode="HTML")
        else: await q.message.reply_text(f"❌ {to_fancy('Not found')}")

# ======================== MAIN ========================
def main():
    t = threading.Thread(target=run_flask, daemon=True)
    t.start()
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("dice", dice_command))
    app.add_handler(CommandHandler("flipcoin", flipcoin_command))
    app.add_handler(CommandHandler("showdice", showdice_command))
    app.add_handler(CommandHandler("showcoin", showcoin_command))
    app.add_handler(CommandHandler("owner", owner_panel))
    app.add_handler(CommandHandler("users", list_users))
    app.add_handler(CommandHandler("ban", ban_user))
    app.add_handler(CommandHandler("unban", unban_user))
    app.add_handler(CommandHandler("deals", list_deals))
    app.add_handler(CommandHandler("deal", view_deal))
    
    app.add_handler(MessageHandler(filters.TEXT & filters.GROUP, handle_deal_form))
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, handle_callback))
    app.add_handler(CallbackQueryHandler(handle_callback))
    
    print(f"🤖 KALYUG ESCROW BOT STARTED | Owner: {OWNER_ID} | Emojis: {len(PREMIUM_EMOJIS)}")
    app.run_polling(allowed_updates=["message", "callback_query"])

if __name__ == "__main__":
    main()
