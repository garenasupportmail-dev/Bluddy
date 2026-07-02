import re
import os
import json
import random
from uuid import uuid4
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# ====== CONFIG ======
BOT_TOKEN = "8885172416:AAFRtSo5uGlTSZBBQgU62Xal8XPgu571tjg"
OWNER_ID = 7977493987
ADMIN_IDS = [OWNER_ID]
CHANNEL = "@KALYUGESCROWSERVICE"

# ====== STYLISH TEXT ======
BOLD = "𝐀𝐁𝐂𝐃𝐄𝐅𝐆𝐇𝐈𝐉𝐊𝐋𝐌𝐍𝐎𝐏𝐐𝐑𝐒𝐓𝐔𝐕𝐖𝐗𝐘𝐙𝐚𝐛𝐜𝐝𝐞𝐟𝐠𝐡𝐢𝐣𝐤𝐥𝐦𝐧𝐨𝐩𝐪𝐫𝐬𝐭𝐮𝐯𝐰𝐱𝐲𝐳𝟎𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗"
NORM = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
FM = {n: b for n, b in zip(NORM, BOLD)}

def F(t):
    return ''.join(FM.get(c, c) for c in t)

# ====== PREMIUM EMOJIS (Telegram custom IDs) ======
# Agar tera account Premium hai toh ye real premium emoji dikhenge
# Agar nahi hai toh fallback normal emoji dikhega
EMOJIS = {
    "verified": "6246537187614005254✅",
    "fire": "4956222745814762495🔥",
    "heart": "5783157259152397008❤️",
    "heart_blue": "5780496071645991525💙",
    "crown": "5794422335599546668👑",
    "star": "6244496562752331516⭐",
    "diamond": "6086778246882399112💎",
    "money": "6089104607328342288💰",
    "bolt": "5791970059597386804⚡",
    "like": "6089313931149448495👍",
    "smile": "6093864814071780526😀",
    "laugh": "5782741660936966676😂",
    "cool": "6032853480782172520😎",
    "devil": "6035242444671421879👿",
    "sigma": "6235620067942341623🥃",
    "don": "6235717714023814969🍂",
    "skills": "6235593671073339928💀",
    "heart_fire": "6147617184479711380❤️‍🔥",
    "eye": "6035338338406242050👁️",
    "clap": "6093744967304352336👏",
    "wink": "6089024570612781324😉",
    "cry": "5783024321324651865😭",
    "star_glow": "6010156854955480259🌟",
}

# Yeh premium emoji ka HTML tag banayega
def E(name):
    if name in EMOJIS:
        data = EMOJIS[name]
        eid = data[:-1]  # last char fallback hai
        fb = data[-1]
        return f'<tg-emoji emoji-id="{eid}">{fb}</tg-emoji>'
    return ""

def R():
    return E(random.choice(list(EMOJIS.keys())))

def BORD(t):
    return '\n'.join(f"{R()} {l} {R()}" if l.strip() else l for l in t.split('\n'))

# ====== DATA ======
USERS = {}
BANNED = []
DEALS = {}

if os.path.exists("u.json"):
    try: USERS = json.load(open("u.json"))
    except: pass
if os.path.exists("b.json"):
    try: BANNED = json.load(open("b.json"))
    except: pass
if os.path.exists("d.json"):
    try: DEALS = json.load(open("d.json"))
    except: pass

def SV():
    json.dump(USERS, open("u.json","w"), indent=2)
    json.dump(BANNED, open("b.json","w"), indent=2)
    json.dump(DEALS, open("d.json","w"), indent=2)

def REG(uid, u, n):
    s = str(uid)
    if s not in USERS:
        USERS[s] = {"u": u, "n": n, "t": str(datetime.now())}
        SV()

def OWN(uid): return uid == OWNER_ID
def ADM(uid): return uid in ADMIN_IDS or uid == OWNER_ID
def BAN(uid): return str(uid) in BANNED

# ====== DEAL FORM PARSE ======
def PARSE(t):
    d = {}
    if not re.search(r'deal.*form|escrow|amount.*buyer', t, re.I): return None
    for k, p in [("amount",r'(?:amount|𝐀𝐌𝐎𝐔𝐍𝐓|amount\s*:)\s*[:：]?\s*([^\n]+)'),
                  ("buyer",r'(?:buyer[s]?|𝐁𝐔𝐘𝐄𝐑)\s*[:：]?\s*([^\n]+)'),
                  ("seller",r'(?:seller|𝐒𝐄𝐋𝐋𝐄𝐑)\s*[:：]?\s*([^\n]+)'),
                  ("detail",r'(?:detail|𝐃𝐄𝐓𝐀𝐈𝐋)\s*[:：]?\s*([^\n]+)'),
                  ("condition",r'(?:condition|𝐂𝐎𝐍𝐃𝐈𝐓𝐈𝐎𝐍)\s*[:：]?\s*([^\n]+)'),
                  ("till",r'(?:till|𝐓𝐈𝐋𝐋)\s*[:：]?\s*([^\n]+)'),
                  ("upi",r'(?:upi|𝐔𝐏𝐈)\s*[:：]?\s*([^\n]+)')]:
        m = re.search(p, t, re.I|re.M)
        if m: d[k] = m.group(1).strip()
    if re.search(r'non.*refund', t, re.I): d["fee"] = True
    return d if d else None

# ====== DEAL CARD ======
def CARD(data, did):
    now = datetime.now().strftime("%I:%M %p | %d %b %Y")
    c = f"""👑 {F("KALYUG ESCROW DEAL FORM")} 👑

{F('━━━━━━━━━━━━━━━━━━━━')}
{E('verified')} {F('Deal ID')}: <code>{did}</code>
{E('heart_blue')} {F('Status')}: {F('Active')}
{F('━━━━━━━━━━━━━━━━━━━━')}

{E('money')} {F('Amount')}: <b>{data.get('amount','N/A')}</b>
👤 {F('Buyer')}: {data.get('buyer','N/A')}
👤 {F('Seller')}: {data.get('seller','N/A')}
📋 {F('Detail')}: {data.get('detail','N/A')}
✅ {F('Condition')}: {data.get('condition','N/A')}
⏳ {F('Escrow Till')}: {data.get('till','N/A')}
"""
    if data.get('upi'): c += f'\n💳 {F("RLS UPI")}: ||{data["upi"]}||\n'
    if data.get('fee'): c += f'\n⚠️ {F("ESCROW FEE NON-REFUNDABLE")}\n'
    c += f"""
{F('━━━━━━━━━━━━━━━━━━━━')}
🕐 {now}
{E('heart_fire')} {F('Join')}: {CHANNEL} {E('heart_fire')}"""
    return c

def NEW_DEAL(data):
    did = str(uuid4())[:8].upper()
    data["id"] = did
    data["status"] = "active"
    DEALS[did] = data
    SV()
    return did

def GET_D(did):
    return DEALS.get(did.upper())

def CANCEL_D(did):
    did = did.upper()
    if did in DEALS:
        DEALS[did]["status"] = "cancelled"
        SV()
        return True
    return False

# ====== BOT COMMANDS ======
async def start(upd, ctx):
    u = upd.effective_user
    if BAN(u.id): return await upd.message.reply_text(f"❌ {F('Banned')}")
    REG(u.id, u.username or "-", u.first_name)
    txt = f"""👑 {F('KALYUG ESCROW BOT')} 👑

{F('━━━━━━━━━━━━━━━━━━━━')}
👋 {F('Hey')} <b>{u.first_name}</b>!
{E('star_glow')} {F('Escrow Deal + Dice + Coin Bot')}

{F('━━━━━━━━━━━━━━━━━━━━')}
🎲 /dice {F('- Roll dice')}
🪙 /flipcoin {F('- Flip coin')}
👑 /owner {F('- Owner panel')}

{F('━━━━━━━━━━━━━━━━━━━━')}
{E('heart_fire')} {CHANNEL} {E('heart_fire')}"""
    kb = InlineKeyboardMarkup([[InlineKeyboardButton(f"📢 {F('Join')} {CHANNEL}", url=f"https://t.me/{CHANNEL.replace('@','')}")]])
    await upd.message.reply_text(txt, parse_mode="HTML", reply_markup=kb)

async def dice(upd, ctx):
    uid = upd.effective_user.id
    if BAN(uid): return await upd.message.reply_text(f"❌ {F('Banned')}")
    try:
        m = await ctx.bot.get_chat_member(CHANNEL, uid)
        if m.status not in ["member","administrator","creator"]:
            kb = InlineKeyboardMarkup([[InlineKeyboardButton(f"📢 {F('Join')} {CHANNEL}", url=f"https://t.me/{CHANNEL.replace('@','')}")]])
            return await upd.message.reply_text(f"⚠️ {F('Please join')} {CHANNEL}", reply_markup=kb)
    except: pass
    
    r = random.randint(1,6)
    ds = ["⚀","⚁","⚂","⚃","⚄","⚅"]
    ctx.bot_data["dice"] = r
    txt = f"""✨ {F('DICE ROLLED')} ✨
{F('━━━━━━━━━━━━━━')}
🎯 {F('Result')}: <b>{F(str(r))}</b> {ds[r-1]}
╔══════════╗
║   {ds[r-1]}   ║
║  <b>{F(str(r))}</b>  ║
╚══════════╝
{F('Rolled by')}: {upd.effective_user.first_name}
{E('heart_fire')} {CHANNEL}"""
    kb = InlineKeyboardMarkup([[InlineKeyboardButton(f"📢 {CHANNEL}", url=f"https://t.me/{CHANNEL.replace('@','')}")]])
    await upd.message.reply_text(txt, parse_mode="HTML", reply_markup=kb)

async def coin(upd, ctx):
    uid = upd.effective_user.id
    if BAN(uid): return await upd.message.reply_text(f"❌ {F('Banned')}")
    try:
        m = await ctx.bot.get_chat_member(CHANNEL, uid)
        if m.status not in ["member","administrator","creator"]:
            kb = InlineKeyboardMarkup([[InlineKeyboardButton(f"📢 {F('Join')} {CHANNEL}", url=f"https://t.me/{CHANNEL.replace('@','')}")]])
            return await upd.message.reply_text(f"⚠️ {F('Please join')} {CHANNEL}", reply_markup=kb)
    except: pass
    
    r = random.choice(["HEAD","TAIL"])
    ce = "🦅" if r == "HEAD" else "🪙"
    ctx.bot_data["coin"] = r
    txt = f"""💎 {F('COIN FLIPPED')} 💎
{F('━━━━━━━━━━━━━━')}
🪙 {F('Result')}: <b>{F(r)}</b> {ce}
╔══════════════╗
║   {ce}       ║
║  <b>{F(r)}</b>  ║
╚══════════════╝
{F('Flipped by')}: {upd.effective_user.first_name}
{E('heart_fire')} {CHANNEL}"""
    kb = InlineKeyboardMarkup([[InlineKeyboardButton(f"📢 {CHANNEL}", url=f"https://t.me/{CHANNEL.replace('@','')}")]])
    await upd.message.reply_text(txt, parse_mode="HTML", reply_markup=kb)

async def showdice(upd, ctx):
    if not OWN(upd.effective_user.id): return await upd.message.reply_text(f"❌ {F('Owner only')}")
    r = ctx.bot_data.get("dice")
    if r is None: return await upd.message.reply_text(f"⚠️ {F('No dice yet')}")
    await upd.message.reply_text(f"🔮 {F('Dice')}: <b>{F(str(r))}</b>", parse_mode="HTML")

async def showcoin(upd, ctx):
    if not OWN(upd.effective_user.id): return await upd.message.reply_text(f"❌ {F('Owner only')}")
    r = ctx.bot_data.get("coin")
    if r is None: return await upd.message.reply_text(f"⚠️ {F('No coin yet')}")
    await upd.message.reply_text(f"🔮 {F('Coin')}: <b>{F(r)}</b>", parse_mode="HTML")

async def owner(upd, ctx):
    if not OWN(upd.effective_user.id): return await upd.message.reply_text(f"❌ {F('Owner only')}")
    txt = f"""👑 {F('OWNER PANEL')} 👑
{F('━━━━━━━━━━━━━━━━━━━━')}
📊 {F('Users')}: {len(USERS)}
🚫 {F('Banned')}: {len(BANNED)}
📦 {F('Deals')}: {len(DEALS)}
{F('━━━━━━━━━━━━━━━━━━━━')}
🔮 /showdice {F('- See dice')}
🔮 /showcoin {F('- See coin')}
👥 /users {F('- List users')}
🚫 /ban ID
✅ /unban ID
📦 /deals {F('- List deals')}
📦 /deal ID {F('- View deal')}
👑 @iflexvenom"""
    await upd.message.reply_text(txt, parse_mode="HTML")

async def users(upd, ctx):
    if not OWN(upd.effective_user.id): return await upd.message.reply_text(f"❌ {F('Owner only')}")
    if not USERS: return await upd.message.reply_text(f"📭 {F('No users')}")
    pts = [f"🆔 <code>{u}</code> | @{d.get('u','-')} | {'🚫' if u in BANNED else '✅'}" for u,d in USERS.items()]
    for ch in [pts[i:i+20] for i in range(0, len(pts), 20)]:
        await upd.message.reply_text(f"👥 {F('Users')} ({len(USERS)})\n{F('━━━━━━━━━━━━━━━━━━━━')}\n" + '\n'.join(ch), parse_mode="HTML")

async def ban(upd, ctx):
    if not OWN(upd.effective_user.id): return await upd.message.reply_text(f"❌ {F('Owner only')}")
    if not ctx.args: return await upd.message.reply_text(f"📝 {F('Usage')}: /ban ID")
    uid = ctx.args[0]
    if uid == str(OWNER_ID): return await upd.message.reply_text(f"❌ {F('Cannot ban owner')}")
    if uid not in BANNED:
        BANNED.append(uid); SV()
        await upd.message.reply_text(f"✅ <code>{uid}</code> {F('banned')}", parse_mode="HTML")
    else:
        await upd.message.reply_text(f"⚠️ {F('Already banned')}")

async def unban(upd, ctx):
    if not OWN(upd.effective_user.id): return await upd.message.reply_text(f"❌ {F('Owner only')}")
    if not ctx.args: return await upd.message.reply_text(f"📝 {F('Usage')}: /unban ID")
    uid = ctx.args[0]
    if uid in BANNED:
        BANNED.remove(uid); SV()
        await upd.message.reply_text(f"✅ <code>{uid}</code> {F('unbanned')}", parse_mode="HTML")
    else:
        await upd.message.reply_text(f"⚠️ {F('Not banned')}")

async def deals(upd, ctx):
    if not OWN(upd.effective_user.id): return await upd.message.reply_text(f"❌ {F('Owner only')}")
    if not DEALS: return await upd.message.reply_text(f"📭 {F('No deals')}")
    pts = [f"🆔 <code>{d}</code> | 💰 {v.get('amount','N/A')} | 👤 {v.get('buyer','N/A')} | 📌 {v.get('status','active')}" for d,v in DEALS.items()]
    for ch in [pts[i:i+15] for i in range(0, len(pts), 15)]:
        await upd.message.reply_text(f"📋 {F('Deals')} ({len(DEALS)})\n{F('━━━━━━━━━━━━━━━━━━━━')}\n" + '\n'.join(ch), parse_mode="HTML")

async def view_deal(upd, ctx):
    if not OWN(upd.effective_user.id): return await upd.message.reply_text(f"❌ {F('Owner only')}")
    if not ctx.args: return await upd.message.reply_text(f"📝 {F('Usage')}: /deal ID")
    d = GET_D(ctx.args[0])
    if d: await upd.message.reply_text(CARD(d, d["id"]), parse_mode="HTML")
    else: await upd.message.reply_text(f"❌ {F('Deal not found')}")

# ====== DEAL FORM DETECTOR ======
async def form_handler(upd, ctx):
    msg = upd.message
    if not msg or not msg.text: return
    
    data = PARSE(msg.text)
    if not data: return
    
    did = NEW_DEAL(data)
    card = CARD(data, did)
    
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"📋 {F('Copy ID')}", callback_data=f"cp_{did}"),
         InlineKeyboardButton(f"👁️ {F('View')}", callback_data=f"vw_{did}")],
        [InlineKeyboardButton(f"❌ {F('Cancel')}", callback_data=f"cn_{did}")],
        [InlineKeyboardButton(f"📢 {CHANNEL}", url=f"https://t.me/{CHANNEL.replace('@','')}")]
    ])
    
    await msg.reply_text(card, parse_mode="HTML", reply_markup=kb)
    
    am = f"""✅ <b>{F('NEW DEAL')}</b> ✅
🆔 <code>{did}</code>
👤 {msg.from_user.first_name}
💰 {data.get('amount','N/A')}
👤 {data.get('buyer','N/A')}
👤 {data.get('seller','N/A')}"""
    ak = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"❌ {F('Cancel')}", callback_data=f"cn_{did}")],
        [InlineKeyboardButton(f"📢 {CHANNEL}", url=f"https://t.me/{CHANNEL.replace('@','')}")]
    ])
    for a in ADMIN_IDS:
        try: await ctx.bot.send_message(a, am, parse_mode="HTML", reply_markup=ak)
        except: pass

# ====== CALLBACK ======
async def cb(upd, ctx):
    q = upd.callback_query
    await q.answer()
    d = q.data
    if d.startswith("cp_"):
        await q.message.reply_text(f"📋 <b>{F('Deal ID')}</b>: <code>{d[3:]}</code>", parse_mode="HTML")
    elif d.startswith("vw_"):
        dl = GET_D(d[3:])
        if dl: await q.message.reply_text(CARD(dl, dl["id"]), parse_mode="HTML")
        else: await q.message.reply_text(f"❌ {F('Deal not found')}")
    elif d.startswith("cn_"):
        if not ADM(upd.effective_user.id): return await q.message.reply_text(f"❌ {F('Admins only')}")
        if CANCEL_D(d[3:]): await q.message.reply_text(f"✅ {F('Deal cancelled')}", parse_mode="HTML")
        else: await q.message.reply_text(f"❌ {F('Not found')}")

# ====== MAIN ======
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("dice", dice))
    app.add_handler(CommandHandler("flipcoin", coin))
    app.add_handler(CommandHandler("showdice", showdice))
    app.add_handler(CommandHandler("showcoin", showcoin))
    app.add_handler(CommandHandler("owner", owner))
    app.add_handler(CommandHandler("users", users))
    app.add_handler(CommandHandler("ban", ban))
    app.add_handler(CommandHandler("unban", unban))
    app.add_handler(CommandHandler("deals", deals))
    app.add_handler(CommandHandler("deal", view_deal))
    
    app.add_handler(MessageHandler(filters.TEXT & filters.GROUP, form_handler))
    app.add_handler(CallbackQueryHandler(cb))
    
    print(f"✅ BOT STARTED! Owner: {OWNER_ID}")
    app.run_polling()

if __name__ == "__main__":
    main()
