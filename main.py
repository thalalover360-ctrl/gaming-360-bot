import os, random, string, threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.end_headers(); self.wfile.write(b"Live")
    def log_message(self, *a): return

threading.Thread(target=lambda: HTTPServer(("0.0.0.0", int(os.environ.get("PORT", 8080))), H).serve_forever(), daemon=True).start()

TOKEN = "8963859901:AAGT3dYv2NraTFV69ZBQ8f5jEcqhcuIWcis"
bot = telebot.TeleBot(TOKEN)

rooms, games, ttt_games, word_games, memory_games, rps_games, bomb_games = {}, {}, {}, {}, {}, {}, {}

WORDS = [
    {"w": "PYTHON", "h": "Programming Language"},
    {"w": "RONALDO", "h": "CR7 Footballer"},
    {"w": "MESSI", "h": "LM10 Footballer"},
    {"w": "CRICKET", "h": "Bat & Ball Sport"},
    {"w": "GALAXY", "h": "System of Stars"},
    {"w": "ROBOT", "h": "Smart Machine"}
]

@bot.message_handler(commands=['start', 'games', 'menu'])
def menu(m):
    txt = m.text.split()
    if len(txt) > 1 and txt[1].startswith("j_"):
        join_dm(m.from_user, m.chat.id, txt[1].replace("j_", ""))
        return
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("🎮 Board Battles (TTT / Bingo / RPS)", callback_data="s_board"),
        InlineKeyboardButton("💣 Bomb Defusal (Minesweeper)", callback_data=f"bmb_{m.chat.id}"),
        InlineKeyboardButton("🔤 Word Games (Scramble / Guess)", callback_data="s_word"),
        InlineKeyboardButton("🃏 Memory Match (Emoji Flip)", callback_data=f"mem_{m.chat.id}"),
        InlineKeyboardButton("⚡ Maths Speed Battle", callback_data=f"qm_{m.chat.id}")
    )
    bot.send_message(m.chat.id, "🔥 **Gaming 360 Arena!** 🔥\nChoose game:", reply_markup=kb, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda c: c.data.startswith('s_'))
def handle_sec(c):
    cid, s = c.message.chat.id, c.data.split('_')[1]
    if s == "board":
        kb = InlineKeyboardMarkup(row_width=1).add(
            InlineKeyboardButton("🤖 Tic Tac Toe (vs AI)", callback_data=f"ta_{cid}"),
            InlineKeyboardButton("👥 Tic Tac Toe (1v1 DM Code)", callback_data=f"tc_{cid}"),
            InlineKeyboardButton("🎲 Bingo 5x5 (Live DM)", callback_data=f"b_{cid}"),
            InlineKeyboardButton("✂️ Rock Paper Scissors (1v1)", callback_data=f"rps_{cid}"),
            InlineKeyboardButton("⬅️ Back", callback_data="s_back")
        )
        bot.edit_message_text("🎮 **Board Battles Arena:**", cid, c.message.message_id, reply_markup=kb)
    elif s == "word":
        kb = InlineKeyboardMarkup(row_width=1).add(
            InlineKeyboardButton("🔀 Word Scramble", callback_data=f"ws_{cid}"),
            InlineKeyboardButton("💡 Word Guess", callback_data=f"wg_{cid}"),
            InlineKeyboardButton("⬅️ Back", callback_data="s_back")
        )
        bot.edit_message_text("🔤 **Word Games:**", cid, c.message.message_id, reply_markup=kb)
    elif s == "back":
        menu(c.message)

# ==================== BOMB DEFUSAL ====================
@bot.callback_query_handler(func=lambda c: c.data.startswith('bmb_'))
def bomb_start(c):
    cid = int(c.data.split('_')[1])
    bomb_games[cid] = {'b': random.randint(0, 8), 'op': set()}
    kb = InlineKeyboardMarkup(row_width=3)
    kb.add(*[InlineKeyboardButton("📦", callback_data=f"bmv_{cid}_{i}") for i in range(9)])
    bot.send_message(cid, "💣 **Bomb Defusal!**\nSafe boxes (💎) open karo, Bomb 💣 se bacho!", reply_markup=kb)

@bot.callback_query_handler(func=lambda c: c.data.startswith('bmv_'))
def bomb_click(c):
    _, cid, idx = c.data.split('_')
    cid, idx = int(cid), int(idx)
    g = bomb_games.get(cid)
    if not g or idx in g['op']: return

    u = c.from_user.first_name
    if idx == g['b']:
        kb = InlineKeyboardMarkup(row_width=3)
        kb.add(*[InlineKeyboardButton("💥" if i==idx else ("💎" if i in g['op'] else "📦"), callback_data="none") for i in range(9)])
        bot.edit_message_text(f"💥 **BOOM! {u} ne bomb phod diya!** 💀", cid, c.message.message_id, reply_markup=kb)
        del bomb_games[cid]
    else:
        g['op'].add(idx)
        if len(g['op']) == 8:
            bot.edit_message_text("🏆 **PERFECT DEFUSAL! Saare safe boxes mil gaye!** 🎉", cid, c.message.message_id)
            del bomb_games[cid]
            return
        kb = InlineKeyboardMarkup(row_width=3)
        kb.add(*[InlineKeyboardButton("💎" if i in g['op'] else "📦", callback_data="none" if i in g['op'] else f"bmv_{cid}_{i}") for i in range(9)])
        bot.edit_message_reply_markup(cid, c.message.message_id, reply_markup=kb)

# ==================== ROCK PAPER SCISSORS ====================
@bot.callback_query_handler(func=lambda c: c.data.startswith('rps_'))
def rps_h(c):
    cid = int(c.data.split('_')[1])
    rps_games[cid] = {'p1': c.from_user, 'p2': None, 'c1': None, 'c2': None}
    kb = InlineKeyboardMarkup().add(InlineKeyboardButton("⚔️ Join Battle", callback_data=f"rj_{cid}"))
    bot.send_message(cid, f"✂️ **RPS Battle!**\nHost: {c.from_user.first_name}\nDoosra player Join kare!", reply_markup=kb)

@bot.callback_query_handler(func=lambda c: c.data.startswith('rj_'))
def rps_j(c):
    cid = int(c.data.split('_')[1])
    g, u = rps_games.get(cid), c.from_user
    if not g or g['p1'].id == u.id: return
    g['p2'] = u
    kb = InlineKeyboardMarkup(row_width=3).add(
        InlineKeyboardButton("🪨 Rock", callback_data=f"rc_{cid}_R"),
        InlineKeyboardButton("📄 Paper", callback_data=f"rc_{cid}_P"),
        InlineKeyboardButton("✂️ Scissors", callback_data=f"rc_{cid}_S")
    )
    bot.send_message(cid, f"🔥 **{g['p1'].first_name} vs {g['p2'].first_name}**\nApna move select karo:", reply_markup=kb)

@bot.callback_query_handler(func=lambda c: c.data.startswith('rc_'))
def rps_c(c):
    _, cid, ch = c.data.split('_')
    cid, g, uid = int(cid), rps_games.get(int(cid)), c.from_user.id
    if not g or not g['p2']: return

    if uid == g['p1'].id and not g['c1']: g['c1'] = ch
    elif uid == g['p2'].id and not g['c2']: g['c2'] = ch
    else: return

    if g['c1'] and g['c2']:
        m_map = {'R': '🪨 Rock', 'P': '📄 Paper', 'S': '✂️ Scissors'}
        p1n, p2n, c1, c2 = g['p1'].first_name, g['p2'].first_name, g['c1'], g['c2']
        if c1 == c2: res = "🤝 **Match Draw!**"
        elif (c1=='R' and c2=='S') or (c1=='P' and c2=='R') or (c1=='S' and c2=='P'): res = f"🏆 **{p1n} Jeet Gaya!**"
        else: res = f"🏆 **{p2n} Jeet Gaya!**"
        bot.send_message(cid, f"⚔️ {p1n}: {m_map[c1]}\n⚔️ {p2n}: {m_map[c2]}\n\n{res}", parse_mode="Markdown")
        del rps_games[cid]

# ==================== MEMORY MATCH ====================
MEM_ICONS = ['🍎', '🚀', '⚽', '💎', '🔥', '🦁']
def get_mem_kb(cid):
    g = memory_games[cid]
    kb = InlineKeyboardMarkup(row_width=4)
    btns = []
    for i in range(12):
        if i in g['mat']: btns.append(InlineKeyboardButton("✅", callback_data="none"))
        elif i in g['flp']: btns.append(InlineKeyboardButton(g['cds'][i], callback_data="none"))
        else: btns.append(InlineKeyboardButton("❓", callback_data=f"mm_{cid}_{i}"))
    kb.add(*btns); return kb

@bot.callback_query_handler(func=lambda c: c.data.startswith('mem_'))
def mem_init(c):
    cid = int(c.data.split('_')[1])
    cds = MEM_ICONS * 2
    random.shuffle(cds)
    memory_games[cid] = {'cds': cds, 'mat': set(), 'flp': [], 'mvs': 0, 'u': c.from_user.first_name}
    bot.send_message(cid, f"🃏 **Memory Match ({c.from_user.first_name})**\n2 same cards match karo:", reply_markup=get_mem_kb(cid))

@bot.callback_query_handler(func=lambda c: c.data.startswith('mm_'))
def mem_flip(c):
    _, cid, idx = c.data.split('_')
    cid, idx, g = int(cid), int(idx), memory_games.get(int(cid))
    if not g or idx in g['mat'] or idx in g['flp']: return

    g['flp'].append(idx)
    if len(g['flp']) == 1:
        bot.edit_message_reply_markup(cid, c.message.message_id, reply_markup=get_mem_kb(cid))
    elif len(g['flp']) == 2:
        g['mvs'] += 1
        i1, i2 = g['flp']
        if g['cds'][i1] == g['cds'][i2]:
            g['mat'].add(i1); g['mat'].add(i2); g['flp'] = []
            if len(g['mat']) == 12:
                bot.edit_message_text(f"🎉 **{g['u']} Jeet Gaya in {g['mvs']} moves!** 🏆", cid, c.message.message_id)
                del memory_games[cid]; return
            bot.edit_message_reply_markup(cid, c.message.message_id, reply_markup=get_mem_kb(cid))
        else:
            bot.edit_message_reply_markup(cid, c.message.message_id, reply_markup=get_mem_kb(cid))
            def hide():
                g['flp'] = []
                try: bot.edit_message_reply_markup(cid, c.message.message_id, reply_markup=get_mem_kb(cid))
                except: pass
            threading.Timer(1.2, hide).start()
        # ==================== WORD & MATHS ====================
@bot.callback_query_handler(func=lambda c: c.data.startswith('ws_'))
def w_scramble(c):
    cid = int(c.data.split('_')[1])
    it = random.choice(WORDS)
    w = it['w']
    j = list(w)
    while ''.join(j) == w: random.shuffle(j)
    word_games[cid] = {'w': w}
    bot.send_message(cid, f"🔀 **Word Scramble!**\nLetters: **`{' '.join(j)}`**\nHint: _{it['h']}_\n👉 Chat me sahi word likho!", parse_mode="Markdown")

@bot.callback_query_handler(func=lambda c: c.data.startswith('wg_'))
def w_guess(c):
    cid = int(c.data.split('_')[1])
    it = random.choice(WORDS)
    w = it['w']
    m = w[0] + " _ " * (len(w)-2) + w[-1]
    word_games[cid] = {'w': w}
    bot.send_message(cid, f"💡 **Word Guess!**\nWord: **`{m}`**\nHint: _{it['h']}_\n👉 Chat me pura word likho!", parse_mode="Markdown")

@bot.callback_query_handler(func=lambda c: c.data.startswith('qm_'))
def q_math(c):
    cid = int(c.data.split('_')[1])
    n1, n2, op = random.randint(10, 50), random.randint(2, 10), random.choice(['+', '-', '*'])
    ans = eval(f"{n1} {op} {n2}")
    opts = list({ans, ans+2, ans-2, ans+5})
    random.shuffle(opts)
    kb = InlineKeyboardMarkup(row_width=2)
    for o in opts: kb.add(InlineKeyboardButton(str(o), callback_data=f"ma_{o}_{ans}"))
    bot.send_message(cid, f"⚡ **{n1} {op} {n2} = ?**", reply_markup=kb)

@bot.callback_query_handler(func=lambda c: c.data.startswith('ma_'))
def ma_ans(c):
    _, s, a = c.data.split('_')
    if s == a:
        bot.send_message(c.message.chat.id, f"🎉 Sahi Jawab **{c.from_user.first_name}**! Answer: `{a}`")
        bot.delete_message(c.message.chat.id, c.message.message_id)
    else: bot.answer_callback_query(c.id, "❌ Galat!")

# ==================== TIC TAC TOE ====================
def chk_ttt(b):
    for x,y,z in [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]:
        if b[x] == b[y] == b[z] and b[x] != " ": return b[x]
    return "Tie" if " " not in b else None

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
    kb = InlineKeyboardMarkup(row_width=3).add(*[InlineKeyboardButton("▫️", callback_data=f"tm_{cid}_{i}") for i in range(9)])
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
    kb = InlineKeyboardMarkup(row_width=3).add(*[InlineKeyboardButton(g['b'][i] if g['b'][i] != " " else "▫️", callback_data=f"tm_{cid}_{i}") for i in range(9)])
    if w:
        txt = "🤝 Draw!" if w == "Tie" else ("🏆 You Won!" if w == 'X' else "🤖 AI Won!")
        bot.edit_message_text(txt, cid, c.message.message_id, reply_markup=kb)
        del ttt_games[cid]
    else: bot.edit_message_text("Turn: You (X)", cid, c.message.message_id, reply_markup=kb)

@bot.callback_query_handler(func=lambda c: c.data.startswith('tc_'))
def ttt_c_room(c):
    cd = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    rooms[cd] = {'h': c.from_user, 'g': None, 'b': [" "]*9, 't': 'X', 'hm': None, 'gm': None}
    url = f"https://t.me/share/url?url=https://t.me/Gaming_360_bot?start=j_{cd}&text=Play%20TTT%20Code:%20{cd}"
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

# ==================== BINGO (3-LINE WIN & LIVE DM) ====================
def gen_b():
    nums = list(range(1, 26)); random.shuffle(nums)
    return [nums[i:i+5] for i in range(0, 25, 5)]

def chk_b(m):
    c = sum(1 for r in range(5) if all(m[r][col] for col in range(5))) + sum(1 for col in range(5) if all(m[r][col] for r in range(5)))
    if all(m[i][i] for i in range(5)): c += 1
    if all(m[i][4-i] for i in range(5)): c += 1
    return c

def render_b(b, m):
    return "\n".join([" | ".join("❌ " if m[r][c] else f"{b[r][c]:02d}" for c in range(5)) for r in range(5)])

@bot.callback_query_handler(func=lambda c: c.data.startswith('b_'))
def b_lobby(c):
    cid = int(c.data.split('_')[1])
    games[cid] = {'p': {}, 'st': 'l', 'cl': set(), 'ord': [], 'idx': 0}
    kb = InlineKeyboardMarkup(row_width=2).add(
        InlineKeyboardButton("🎮 Join", callback_data=f"bj_{cid}"),
        InlineKeyboardButton("🤖 Add AI", callback_data=f"ba_{cid}"),
        InlineKeyboardButton("🚀 Start", callback_data=f"bs_{cid}")
    )
    bot.send_message(cid, "🎲 **Bingo Lobby Active!**\n🎯 Target: First to **3 Lines** Wins!", reply_markup=kb)

@bot.callback_query_handler(func=lambda c: c.data.startswith('bj_'))
def b_join(c):
    cid = int(c.data.split('_')[1])
    g, u = games.get(cid), c.from_user
    if g and g['st'] == 'l' and u.id not in g['p']:
        g['p'][u.id] = {'n': u.first_name, 'b': gen_b(), 'm': [[False]*5 for _ in range(5)], 'ai': False, 'msg_id': None}
        bot.send_message(cid, f"✅ **{u.first_name}** added to Bingo!")
    bot.answer_callback_query(c.id, "Joined!")

@bot.callback_query_handler(func=lambda c: c.data.startswith('ba_'))
def b_ai(c):
    cid = int(c.data.split('_')[1])
    g = games.get(cid)
    if g and g['st'] == 'l' and 999 not in g['p']:
        g['p'][999] = {'n': '🤖 AI Bot', 'b': gen_b(), 'm': [[False]*5 for _ in range(5)], 'ai': True, 'msg_id': None}
        bot.send_message(cid, "🤖 **AI Bot** added to Bingo!")
    bot.answer_callback_query(c.id, "AI Added!")

@bot.callback_query_handler(func=lambda c: c.data.startswith('bs_'))
def b_start(c):
    cid = int(c.data.split('_')[1])
    g = games.get(cid)
    if not g or len(g['p']) < 2:
        bot.answer_callback_query(c.id, "Kam se kam 2 players chahiye!")
        return
    g['st'], g['ord'] = 'play', list(g['p'].keys())
    for pid, d in g['p'].items():
        if not d['ai']:
            try:
                msg = bot.send_message(pid, f"📋 **Aapka Bingo Board (Live):**\n`{render_b(d['b'], d['m'])}`\n\n🎯 Target: 3 Lines", parse_mode="Markdown")
                d['msg_id'] = msg.message_id
            except: pass
    p1 = g['ord'][0]
    bot.send_message(cid, f"🔥 **Bingo Shuru!**\n👉 Pehli Baari: **{g['p'][p1]['n']}** (Chat me 1-25 number likho)")
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
    score_report, winner = [], None

    for pid, d in g['p'].items():
        for r in range(5):
            for col in range(5):
                if d['b'][r][col] == num: d['m'][r][col] = True
        lines = chk_b(d['m'])
        score_report.append(f"• **{d['n']}**: {'🟢'*lines}{'⚪'*(3-min(3, lines))} ({lines}/3)")
        if not d['ai'] and d['msg_id']:
            try:
                bot.edit_message_text(f"📋 **Live Board:**\n`{render_b(d['b'], d['m'])}`\n📢 Cut: **{num}**\n📊 Lines: {lines}/3", chat_id=pid, message_id=d['msg_id'], parse_mode="Markdown")
            except: pass
        if lines >= 3 and not winner: winner = d['n']

    if winner:
        bot.send_message(cid, f"🏆 **BINGO! {winner} JEET GAYA!** 🎉\n\n" + "\n".join(score_report), parse_mode="Markdown")
        del games[cid]; return

    g['idx'] = (g['idx'] + 1) % len(g['ord'])
    nxt = g['ord'][g['idx']]
    bot.send_message(cid, f"📢 Cut: **{num}**\n\n📊 Scoreboard:\n" + "\n".join(score_report) + f"\n\n👉 Turn: **{g['p'][nxt]['n']}**", parse_mode="Markdown")
    if g['p'][nxt]['ai']: threading.Timer(2.0, proc_b_ai, args=[cid]).start()

# ==================== TEXT INPUT HANDLER ====================
@bot.message_handler(func=lambda m: m.text)
def handle_texts(m):
    cid, txt = m.chat.id, m.text.strip().upper()
    if cid in word_games and txt == word_games[cid]['w']:
        bot.reply_to(m, f"🎉 **KAMAAL! {m.from_user.first_name} ne sahi jawab diya!**\nWord: **`{txt}`**", parse_mode="Markdown")
        del word_games[cid]; return

    if m.text.isdigit():
        g = games.get(cid)
        if g and g['st'] == 'play' and m.from_user.id == g['ord'][g['idx']]:
            n = int(m.text)
            if 1 <= n <= 25 and n not in g['cl']: proc_b_num(cid, n)

bot.infinity_polling()
    
