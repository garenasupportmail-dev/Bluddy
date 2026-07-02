import re, os, json, random, threading
from uuid import uuid4
from datetime import datetime
from flask import Flask, jsonify
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# ====== FLASK FOR RENDER ======
flask_app = Flask(__name__)

@flask_app.route('/')
@flask_app.route('/health')
def health():
    return jsonify({"status": "ok", "bot": "running"}), 200

def run_flask():
    port = int(os.environ.get('PORT', 5000))
    flask_app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

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

# ====== EMOJIS ======
EMOJIS = {
    "verified": "6246537187614005254✅", "fire": "4956222745814762495🔥",
    "heart": "5783157259152397008❤️", "heart_blue": "5780496071645991525💙",
    "crown": "5794422335599546668👑", "star": "6244496562752331516⭐",
    "diamond": "6086778246882399112💎", "money": "6089104607328342288💰",
    "bolt": "5791970059597386804⚡", "like": "6089313931149448495👍",
    "smile": "6093864814071780526😀", "laugh": "5782741660936966676😂",
    "cool": "6032853480782172520😎", "devil": "6035242444671421879👿",
    "sigma": "6235620067942341623🥃", "don": "6235717714023814969🍂",
    "skills": "6235593671073339928💀", "heart_fire": "6147617184479711380❤️‍🔥",
    "eye": "6035338338406242050👁️", "star_glow": "6010156854955480259🌟",
}

def E(name):
    if name in EMOJIS:
        d = EMOJIS[name]
        return f'<tg-emoji emoji-id="{d[:-1]}">{d[-1]}</tg-emoji>'
    return ""

def R():
    return E(random.choice(list(EMOJIS.keys())))

# ====== DATA ======
USERS = {}; BANNED = []; DEALS = {}
for f, d in [("u.json",USERS),("b.json",BANNED),("d.json",DEALS)]:
    if os.path.exists(f):
        try: 
            data = json.load(open(f))
            if isinstance(data, dict): d.update(data)
            elif isinstance(data, list): d.extend(data)
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

# ====== FORM PARSE ======
def PARSE(t):
    d = {}
    if not re.search(r'deal|escrow|amount.*buyer', t, re.I): return None
    for k, p in [("amount",r'(?:amount|𝐀𝐌𝐎𝐔𝐍𝐓)\s*[:：]?\s*([^\n]+)'),
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
    data["id"] = did; data["status"] = "active"
    DEALS[did] = data; SV()
    return did

def GET_D(did):
    return DEALS.get(did.upper())

def CANCEL_D(did):
    did = did.upper()
    if did in DEALS:
        DEALS[did]["status"] = "cancelled"; SV()
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
🎲 /dice
🪙 /flipcoin
👑 /owner
{F('━━━━━━━━━━━━━━━━━━━━')}
{E('heart_fire')} {CHANNEL}"""
    kb = InlineKeyboardMarkup([[InlineKeyboardButton(f"📢 {CHANNEL}", url=f"https://t.me/{CHANNEL.replace('@','')}")]])
    await upd.message.reply_text(txt, parse_mode="HTML", reply_markup=kb)

async def dice(upd, ctx):
    uid = upd.effective_user.id
    if BAN(uid): return await upd.message.reply_text(f"❌ {F('Banned')}")
    try:
        m = await ctx.bot.get_chat_member(CHANNEL, uid)
        if m.status not in ["member","administrator","creator"]:
            kb = InlineKeyboardMarkup([[InlineKeyboardButton(f"📢 {CHANNEL}", url=f"https://t.me/{CHANNEL.replace('@','')}")]])
            return await upd.message.reply_text(f"⚠️ {F('Please join')} {CHANNEL}", reply_markup=kb)
    except: pass
    r = random.randint(1,6)
    ds = ["⚀","⚁","⚂","⚃","⚄","⚅"]
    ctx.bot_data["dice"] = r
    txt = f"""✨ {F('DICE ROLLED')} ✨
{F('━━━━━━━━━━━━━━')}
🎯 {F('Result')}: <b>{F(str(r))}</b> {ds[r-1]}
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
            kb = InlineKeyboardMarkup([[InlineKeyboardButton(f"📢 {CHANNEL}", url=f"https://t.me/{CHANNEL.replace('@','')}")]])
            return await upd.message.reply_text(f"⚠️ {F('Please join')} {CHANNEL}", reply_markup=kb)
    except: pass
    r = random.choice(["HEAD","TAIL"])
    ce = "🦅" if r == "HEAD" else "🪙"
    ctx.bot_data["coin"] = r
    txt = f"""💎 {F('COIN FLIPPED')} 💎
{F('━━━━━━━━━━━━━━')}
🪙 {F('Result')}: <b>{F(r)}</b> {ce}
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
📊 Users: {len(USERS)} | 🚫 Banned: {len(BANNED)} | 📦 Deals: {len(DEALS)}
{F('━━━━━━━━━━━━━━━━━━━━')}
🔮 /showdice | 🔮 /showcoin
👥 /users | 🚫 /ban ID | ✅ /unban ID
📦 /deals | 📦 /deal ID
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
    if not ctx.args: return await upd.message.reply_text(f"📝 Usage: /ban ID")
    uid = ctx.args[0]
    if uid == str(OWNER_ID): return await upd.message.reply_text(f"❌ Cannot ban owner")
    if uid not in BANNED: BANNED.append(uid); SV(); await upd.message.reply_text(f"✅ <code>{uid}</code> banned", parse_mode="HTML")
    else: await upd.message.reply_text(f"⚠️ Already banned")

async def unban(upd, ctx):
    if not OWN(upd.effective_user.id): return await upd.message.reply_text(f"❌ {F('Owner only')}")
    if not ctx.args: return await upd.message.reply_text(f"📝 Usage: /unban ID")
    uid = ctx.args[0]
    if uid in BANNED: BANNED.remove(uid); SV(); await upd.message.reply_text(f"✅ <code>{uid}</code> unbanned", parse_mode="HTML")
    else: await upd.message.reply_text(f"⚠️ Not banned")

async def deals(upd, ctx):
    if not OWN(upd.effective_user.id): return await upd.message.reply_text(f"❌ {F('Owner only')}")
    if not DEALS: return await upd.message.reply_text(f"📭 No deals")
    pts = [f"🆔 <code>{d}</code> | 💰 {v.get('amount','N/A')} | 👤 {v.get('buyer','N/A')} | 📌 {v.get('status','active')}" for d,v in DEALS.items()]
    for ch in [pts[i:i+15] for i in range(0, len(pts), 15)]:
        await upd.message.reply_text(f"📋 Deals ({len(DEALS)})\n{F('━━━━━━━━━━━━━━━━━━━━')}\n" + '\n'.join(ch), parse_mode="HTML")

async def view_deal(upd, ctx):
    if not OWN(upd.effective_user.id): return await upd.message.reply_text(f"❌ {F('Owner only')}")
    if not ctx.args: return await upd.message.reply_text(f"📝 Usage: /deal ID")
    d = GET_D(ctx.args[0])
    if d: await upd.message.reply_text(CARD(d, d["id"]), parse_mode="HTML")
    else: await upd.message.reply_text(f"❌ Deal not found")

async def form_handler(upd, ctx):
    msg = upd.message
    if not msg or not msg.text: return
    data = PARSE(msg.text)
    if not data: return
    did = NEW_DEAL(data)
    card = CARD(data, did)
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"📋 Copy ID", callback_data=f"cp_{did}"),
         InlineKeyboardButton(f"👁️ View", callback_data=f"vw_{did}")],
        [InlineKeyboardButton(f"❌ Cancel", callback_data=f"cn_{did}")],
        [InlineKeyboardButton(f"📢 {CHANNEL}", url=f"https://t.me/{CHANNEL.replace('@','')}")]
    ])
    await msg.reply_text(card, parse_mode="HTML", reply_markup=kb)
    am = f"✅ NEW DEAL\n🆔 <code>{did}</code>\n👤 {msg.from_user.first_name}\n💰 {data.get('amount','N/A')}\n👤 {data.get('buyer','N/A')}"
    ak = InlineKeyboardMarkup([[InlineKeyboardButton(f"❌ Cancel", callback_data=f"cn_{did}")]])
    for a in ADMIN_IDS:
        try: await ctx.bot.send_message(a, am, parse_mode="HTML", reply_markup=ak)
        except: pass
    if OWNER_ID not in ADMIN_IDS:
        try: await ctx.bot.send_message(OWNER_ID, am, parse_mode="HTML", reply_markup=ak)
        except: pass

async def cb(upd, ctx):
    q = upd.callback_query
    await q.answer()
    d = q.data
    if d.startswith("cp_"):
        await q.message.reply_text(f"📋 <b>Deal ID</b>: <code>{d[3:]}</code>", parse_mode="HTML")
    elif d.startswith("vw_"):
        dl = GET_D(d[3:])
        if dl: await q.message.reply_text(CARD(dl, dl["id"]), parse_mode="HTML")
        else: await q.message.reply_text("❌ Deal not found")
    elif d.startswith("cn_"):
        if not ADM(upd.effective_user.id): return await q.message.reply_text("❌ Admins only")
        if CANCEL_D(d[3:]): await q.message.reply_text("✅ Deal cancelled")
        else: await q.message.reply_text("❌ Not found")

# ====== MAIN ======
def main():
    # Start Flask for Render health check
    t = threading.Thread(target=run_flask, daemon=True)
    t.start()
    
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
    app.run_polling(allowed_updates=["message", "callback_query"])

if __name__ == "__main__":
    main()
