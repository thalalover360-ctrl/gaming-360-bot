import os
import random
import string
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Render Web Port Binding
class H(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Live")
    def log_message(self, *a): return

threading.Thread(target=lambda: HTTPServer(("0.0.0.0", int(os.environ.get("PORT", 8080))), H).serve_forever(), daemon=True).start()

TOKEN = "8963859901:AAGT3dYv2NraTFV69ZBQ8f5jEcqhcuIWcis"
bot = telebot.TeleBot(TOKEN)

rooms, games, ttt_games = {}, {}, {}

CBSE = {
    "10": [
        {"q": "📚 [Class 10 Light]\nRay through Centre of Curvature retraces path because:", "opts": ["i = 0°", "r = 90°", "Plane mirror", "TIR"], "ans": "i = 0°"},
        {"q": "📚 [Class 10 Electricity]\nR1 & R2 in parallel (R1 > R2). Which takes MORE power?", "opts": ["R2", "R1", "Both equal", "Depends on V"], "ans": "R2"},
        {"q": "📚 [Class 10 Chemistry]\nLime water milkiness disappears with excess CO2 due to:", "opts": ["Ca(HCO3)2", "CaCO3", "CaO", "Ca(OH)2"], "ans": "Ca(HCO3)2"}
    ],
    "11": [
        {"q": "📚 [Class 11 Physics]\nMomentum increases by 50%. % increase in KE is:", "opts": ["125%", "50%", "100%", "225%"], "ans": "125%"},
        {"q": "📚 [Class 11 Chemistry]\nFor spontaneous process in isolated system, ΔS is:", "opts": ["> 0", "< 0", "= 0", "Variable"], "ans": "> 0"}
    ],
    "12": [
        {"q": "📚 [Class 12 Physics]\nElectric dipole in uniform electric field feels:", "opts": ["Torque only (F=0)", "Both F & Torque", "Force only", "None"], "ans": "Torque only (F=0)"},
        {"q": "📚 [Class 12 Maths]\nMatrix order 3, |A| = 4. What is |adj(A)|?", "opts": ["16", "4", "64", "1/4"], "ans": "16"}
    ],
    "mind": [
        {"q": "🧠 Sookhte waqt geeli kaun si cheez hoti hai?", "opts": ["Towel", "Soap", "Paper", "Cloth"], "ans": "Towel"},
        {"q": "🧠 Bina chhuye kya tod sakte ho?", "opts": ["Promise", "Glass", "Heart", "Trust"], "ans": "Promise"}
    ]
}

@bot.message_handler(commands=['start', 'games', 'menu'])
def menu(m):
    txt = m.text.split()
    if len(txt) > 1 and txt[1].startswith("j_"):
        join_dm(m.from_user, m.chat.id, txt[1].replace("j_", ""))
        return
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("🎮 Play Games (TTT / Bingo)", callback_data="s_g"),
        InlineKeyboardButton("🧠 Brain & Maths Speed", callback_data="s_l"),
        InlineKeyboardButton("📚 CBSE Study Quiz (10, 11, 12)", callback_data="s_q")
    )
    bot.send_message(m.chat.id, "🔥 **Gaming 360 Arena!**\nCategory chuno:", reply_markup=kb, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda c: c.data.startswith('s_'))
def handle_s(c):
    cid, s = c.message.chat.id, c.data.split('_')[1]
    if s == "g":
        kb = InlineKeyboardMarkup(row_width=1).add(
            InlineKeyboardButton("🤖 TTT vs AI", callback_data=f"ta_{cid}"),
            InlineKeyboardButton("👥 TTT 1v1 Room Code (DM Match)", callback_data=f"tc_{cid}"),
            InlineKeyboardButton("🎲 Bingo 5x5", callback_data=f"b_{cid}")
        )
        bot.edit_message_text("🎮 **Play Games:**", cid, c.message.message_id, reply_markup=kb)
    elif s == "l":
        kb = InlineKeyboardMarkup(row_width=1).add(
            InlineKeyboardButton("⚡ Maths Speed Battle", callback_data=f"qm_{cid}"),
            InlineKeyboardButton("🧩 Riddles & Logic", callback_data=f"qz_mind")
        )
        bot.edit_message_text("🧠 **Brain Games:**", cid, c.message.message_id, reply_markup=kb)
    elif s == "q":
        kb = InlineKeyboardMarkup(row_width=1).add(
            InlineKeyboardButton("📘 Class 10 PYQs", callback_data="qz_10"),
            InlineKeyboardButton("📗 Class 11 PYQs", callback_data="qz_11"),
            InlineKeyboardButton("📕 Class 12 PYQs", callback_data="qz_12")
        )
        bot.edit_message_text("📚 **CBSE Quizzes:**", cid, c.message.message_id, reply_markup=kb)

# Quiz
@bot.callback_query_handler(func=lambda c: c.data.startswith('qz_'))
def qz_send(c):
    cat = c.data.split('_')[1]
    q = random.choice(CBSE[cat])
    opts = list(q['opts'])
    random.shuffle(opts)
    kb = InlineKeyboardMarkup(row_width=1)
    for o in opts:
        kb.add(InlineKeyboardButton(o, callback_data=f"qa_{cat}_{o[:8]}_{q['ans'][:8]}"))
    bot.send_message(c.message.chat.id, q['q'], reply_markup=kb)

@bot.callback_query_handler(func=lambda c: c.data.startswith('qa_'))
def qz_ans(c):
    _, cat, sel, ans = c.data.split('_')
    if sel == ans:
        kb = InlineKeyboardMarkup().add(InlineKeyboardButton("➡️ Next", callback_data=f"qz_{cat}"))
        bot.send_message(c.message.chat.id, f"🎉 Sahi Jawab **{c.from_user.first_name}**!", reply_markup=kb)
        bot.delete_message(c.message.chat.id, c.message.message_id)
    else: bot.answer_callback_query(c.id, "❌ Galat!", show_alert=True)

# Maths
@bot.callback_query_handler(func=lambda c: c.data.startswith('qm_'))
def q_math(c):
    n1, n2, op = random.randint(10, 50), random.randint(2, 10), random.choice(['+', '-', '*'])
    ans = eval(f"{n1} {op} {n2}")
    opts = list({ans, ans+2, ans-2, ans+5})
    random.shuffle(opts)
    kb = InlineKeyboardMarkup(row_width=2)
    for o in opts: kb.add(InlineKeyboardButton(str(o), callback_data=f"ma_{o}_{ans}"))
    bot.send_message(c.message.chat.id, f"⚡ **{n1} {op} {n2} = ?**", reply_markup=kb)

@bot.callback_query_handler(func=lambda c: c.data.startswith('ma_'))
def ma_ans(c):
    _, s, a = c.data.split('_')
    if s == a:
        bot.send_message(c.message.chat.id, f"🎉 Sahi! Answer: `{a}`", parse_mode="Markdown")
        bot.delete_message(c.message.chat.id, c.message.message_id)
    else: bot.answer_callback_query(c.id, "❌ Galat!")

# TTT Logic
def chk_ttt(b):
    for x,y,z in [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]:
        if b[x] == b[y] == b[z] and b[x] != " ": return b[x]
    return "Tie" if " " not in b else None

# TTT AI
@bot.callback_query_handler(func=lambda c: c.data.startswith('ta_'))
def ttt_ai_menu(c):
    cid = int(c.data.split('_')[1])
    kb = InlineKeyboardMarkup(row_width=3).add(
        InlineKeyboardButton("🟢 Easy", callback_data=f"td_{cid}_easy"),
        InlineKeyboardButton("🟡 Med", callback_data=f"td_{cid}_med"),
        InlineKeyboardButton("🔴 Hard", callback_data=f"td_{cid}_hard")
    )
    bot.send_message(cid, "🤖 AI Difficulty:", reply_markup=kb)

@bot.callback_query_handler(func=lambda c: c.data.startswith('td_'))
def ttt_ai_start(c):
    _, cid, diff = c.data.split('_')
    cid = int(cid)
    ttt_games[cid] = {'p1': c.from_user, 'd': diff, 'b': [" "]*9}
    kb = InlineKeyboardMarkup(row_width=3)
    kb.add(*[InlineKeyboardButton("▫️", callback_data=f"tm_{cid}_{i}") for i in range(9)])
    bot.send_message(cid, f"🤖 Match vs AI ({diff})!\nTurn: {c.from_user.first_name} (X)", reply_markup=kb)

@bot.callback_query_handler(func=lambda c: c.data.startswith('tm_'))
def ttt_ai_move(c):
    _, cid, idx = c.data.split('_')
    cid, idx, g = int(cid), int(idx), ttt_games.get(int(cid))
    if not g or c.from_user.id != g['p1'].id or g['b'][idx] != " ": return
    g['b'][idx] = 'X'
    w = chk_ttt(g['b'])
    if not w:
        emp = [i for i, v in enumerate(g['b']) if v == " "]
        if emp:
            ai_i = random.choice(emp)
            if g['d'] == "hard":
                for i in emp:
                    g['b'][i] = 'O'
                    if chk_ttt(g['b']) == 'O': ai_i = i; g['b'][i] = ' '; break
                    g['b'][i] = ' '
            g['b'][ai_i] = 'O'
            w = chk_ttt(g['b'])
    kb = InlineKeyboardMarkup(row_width=3)
    kb.add(*[InlineKeyboardButton(g['b'][i] if g['b'][i] != " " else "▫️", callback_data=f"tm_{cid}_{i}") for i in range(9)])
    if w:
        txt = "🤝 Draw!" if w == "Tie" else ("🏆 You Won!" if w == 'X' else "🤖 AI Won!")
        bot.edit_message_text(txt, cid, c.message.message_id, reply_markup=kb)
        del ttt_games[cid]
    else: bot.edit_message_text("Turn: You (X)", cid, c.message.message_id, reply_markup=kb)

# TTT DM 1v1 Room
@bot.callback_query_handler(func=lambda c: c.data.startswith('tc_'))
def ttt_c_room(c):
    cd = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    rooms[cd] = {'h': c.from_user, 'g': None, 'b': [" "]*9, 't': 'X', 'hm': None, 'gm': None}
    url = f"https://t.me/share/url?url=https://t.me/Gaming_360_bot?start=j_{cd}&text=Aaja%20TTT%20khelte%20hain!%20Code:%20{cd}"
    kb = InlineKeyboardMarkup().add(InlineKeyboardButton("📲 Invite Friend", url=url))
    bot.send_message(c.message.chat.id, f"🎟️ **Code:** `{cd}`\nDost ko share karo!", reply_markup=kb, parse_mode="Markdown")

def join_dm(g_user, g_cid, cd):
    r = rooms.get(cd)
    if not r or r['g'] or r['h'].id == g_user.id:
        bot.send_message(g_cid, "❌ Room full ya invalid hai!")
        return
    r['g'] = g_user
    kb = InlineKeyboardMarkup(row_width=3).add(*[InlineKeyboardButton("▫️", callback_data=f"dm_{cd}_{i}") for i in range(9)])
    m1 = bot.send_message(r['h'].id, f"🔥 Start vs {g_user.first_name}!\nYour turn (X)", reply_markup=kb)
    m2 = bot.send_message(g_cid, f"🔥 Start vs {r['h'].first_name}!\nTurn: {r['h'].first_name} (X)", reply_markup=kb)
    r['hm'], r['gm'] = m1.message_id, m2.message_id

@bot.callback_query_handler(func=lambda c: c.data.startswith('dm_'))
def ttt_dm_mv(c):
    _, cd, idx = c.data.split('_')
    idx, r = int(idx), rooms.get(cd)
    if not r or not r['g']: return
    cur = r['h'] if r['t'] == 'X' else r['g']
    if c.from_user.id != cur.id or r['b'][idx] != " ": return
    r['b'][idx] = r['t']
    w = chk_ttt(r['b'])
    kb = InlineKeyboardMarkup(row_width=3).add(*[InlineKeyboardButton(r['b'][i] if r['b'][i] != " " else "▫️", callback_data=f"dm_{cd}_{i}") for i in range(9)])
    if w:
        txt = "🤝 Draw!" if w == "Tie" else f"🏆 {(r['h'].first_name if w == 'X' else r['g'].first_name)} Won!"
        try:
            bot.edit_message_text(txt, r['h'].id, r['hm'], reply_markup=kb)
            bot.edit_message_text(txt, r['g'].id, r['gm'], reply_markup=kb)
        except: pass
        del rooms[cd]
    else:
        r['t'] = 'O' if r['t'] == 'X' else 'X'
        nxt = r['h'].first_name if r['t'] == 'X' else r['g'].first_name
        try:
            bot.edit_message_text(f"Turn: **{nxt}** ({r['t']})", r['h'].id, r['hm'], reply_markup=kb, parse_mode="Markdown")
            bot.edit_message_text(f"Turn: **{nxt}** ({r['t']})", r['g'].id, r['gm'], reply_markup=kb, parse_mode="Markdown")
        except: pass

# Bingo
def gen_b():
    nums = list(range(1, 26))
    random.shuffle(nums)
    return [nums[i:i+5] for i in range(0, 25, 5)]

def chk_b(m):
    c = sum(1 for r in range(5) if all(m[r][c] for c in range(5))) + sum(1 for col in range(5) if all(m[r][col] for r in range(5)))
    if all(m[i][i] for i in range(5)): c += 1
    if all(m[i][4-i] for i in range(5)): c += 1
    return c

@bot.callback_query_handler(func=lambda c: c.data.startswith('b_'))
def b_lobby(c):
    cid = int(c.data.split('_')[1])
    games[cid] = {'p': {}, 'st': 'l', 'cl': set(), 'ord': [], 'idx': 0}
    kb = InlineKeyboardMarkup(row_width=2).add(
        InlineKeyboardButton("🎮 Join", callback_data=f"bj_{cid}"),
        InlineKeyboardButton("🤖 Add AI", callback_data=f"ba_{cid}"),
        InlineKeyboardButton("🚀 Start", callback_data=f"bs_{cid}")
    )
    bot.send_message(cid, "🎲 **Bingo Lobby!**", reply_markup=kb)

@bot.callback_query_handler(func=lambda c: c.data.startswith('bj_'))
def b_join(c):
    cid = int(c.data.split('_')[1])
    g, u = games.get(cid), c.from_user
    if g and g['st'] == 'l' and u.id not in g['p']:
        g['p'][u.id] = {'n': u.first_name, 'b': gen_b(), 'm': [[False]*5 for _ in range(5)], 'ai': False}
        bot.send_message(cid, f"✅ **{u.first_name}** added!")
    bot.answer_callback_query(c.id, "Joined!")

@bot.callback_query_handler(func=lambda c: c.data.startswith('ba_'))
def b_ai(c):
    cid = int(c.data.split('_')[1])
    g = games.get(cid)
    if g and g['st'] == 'l' and 999 not in g['p']:
        g['p'][999] = {'n': '🤖 AI Bot', 'b': gen_b(), 'm': [[False]*5 for _ in range(5)], 'ai': True}
        bot.send_message(cid, "🤖 AI Bot added!")
    bot.answer_callback_query(c.id, "AI Added!")

@bot.callback_query_handler(func=lambda c: c.data.startswith('bs_'))
def b_start(c):
    cid = int(c.data.split('_')[1])
    g = games.get(cid)
    if not g or len(g['p']) < 2:
        bot.answer_callback_query(c.id, "Min 2 players required!")
        return
    g['st'], g['ord'] = 'play', list(g['p'].keys())
    for pid, d in g['p'].items():
        if not d['ai']:
            b_txt = "\n".join(" | ".join("❌" if d['m'][r][col] else f"{d['b'][r][col]:02d}" for col in range(5)) for r in range(5))
            try: bot.send_message(pid, f"📋 Board:\n`{b_txt}`", parse_mode="Markdown")
            except: pass
    p1 = g['ord'][0]
    bot.send_message(cid, f"🔥 Bingo Started! Turn: **{g['p'][p1]['n']}** (1-25 type karo)")
    if g['p'][p1]['ai']: proc_b_ai(cid)

def proc_b_ai(cid):
    g = games.get(cid)
    if not g or g['st'] != 'play': return
    av = [n for n in range(1, 26) if n not in g['cl']]
    if av: proc_b_num(cid, random.choice(av))

def proc_b_num(cid, num):
    g = games.get(cid)
    if not g or g['st'] != 'play': return
    g['cl'].add(num)
    for pid, d in g['p'].items():
        for r in range(5):
            for col in range(5):
                if d['b'][r][col] == num: d['m'][r][col] = True
        if chk_b(d['m']) >= 5:
            bot.send_message(cid, f"🎉 **BINGO! {d['n']} JEET GAYA!**")
            del games[cid]
            return
    g['idx'] = (g['idx'] + 1) % len(g['ord'])
    nxt = g['ord'][g['idx']]
    bot.send_message(cid, f"📢 Number **{num}** cut! Next: **{g['p'][nxt]['n']}**")
    if g['p'][nxt]['ai']: threading.Timer(2.0, proc_b_ai, args=[cid]).start()

@bot.message_handler(func=lambda m: m.text and m.text.isdigit())
def b_txt_handle(m):
    g = games.get(m.chat.id)
    if not g or g['st'] != 'play' or m.from_user.id != g['ord'][g['idx']]: return
    n = int(m.text)
    if 1 <= n <= 25 and n not in g['cl']: proc_b_num(m.chat.id, n)

bot.infinity_polling()
                                 
