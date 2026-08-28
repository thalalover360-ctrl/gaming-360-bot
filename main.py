import os
import random
import string
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Bot Setup
TOKEN = "8963859901:AAGT3dYv2NraTFV69ZBQ8f5jEcqhcuIWcis"
bot = telebot.TeleBot(TOKEN, threaded=True)

rooms = {}      # Code-based rooms for DM 1v1
games = {}      # Bingo games
ttt_games = {}  # TTT active sessions

MATH_OPS = ['+', '-', '*']

# ==================== DATA: STUDY & LOGICAL QUIZZES ====================

CBSE_QUESTIONS = {
    "10": [
        {
            "q": "📚 [Class 10 Science - Light]\nA ray passes through Centre of Curvature of concave mirror and retraces its path. Why?",
            "opts": ["Angle of Incidence = 0 deg", "Angle of Refraction = 90 deg", "Mirror is plane at center", "Total Internal Reflection"],
            "ans": "Angle of Incidence = 0 deg"
        },
        {
            "q": "📚 [Class 10 Science - Electricity]\nTwo resistors R1 and R2 (R1 > R2) are in parallel across V. Which consumes MORE power?",
            "opts": ["R2 consumes more", "R1 consumes more", "Both consume equal", "Depends on battery emf"],
            "ans": "R2 consumes more"
        },
        {
            "q": "📚 [Class 10 Science - Chemistry]\nWhen excess CO2 is passed through lime water, milkiness disappears due to:",
            "opts": ["Ca(HCO3)2 (Soluble)", "CaCO3 (Insoluble)", "CaO", "Ca(OH)2"],
            "ans": "Ca(HCO3)2 (Soluble)"
        },
        {
            "q": "📚 [Class 10 Maths - AP]\nSum of first n terms is Sn = 3n^2 + 5n. What is the common difference (d)?",
            "opts": ["6", "3", "5", "8"],
            "ans": "6"
        },
        {
            "q": "📚 [Class 10 Biology - Life Processes]\nWhy is breathing rate in aquatic organisms much faster than terrestrial organisms?",
            "opts": ["Dissolved O2 is low in water", "Water is denser than air", "Gills are smaller", "High metabolic rate"],
            "ans": "Dissolved O2 is low in water"
        }
    ],
    "11": [
        {
            "q": "📚 [Class 11 Physics - Mechanics]\nIf linear momentum is increased by 50%, what is the % increase in Kinetic Energy?",
            "opts": ["125%", "50%", "100%", "225%"],
            "ans": "125%"
        },
        {
            "q": "📚 [Class 11 Chemistry - Thermodynamics]\nFor an isolated system in a spontaneous process, entropy change (Delta S) is:",
            "opts": ["Always Positive (>0)", "Always Negative (<0)", "Zero (=0)", "Depends on enthalpy"],
            "ans": "Always Positive (>0)"
        },
        {
            "q": "📚 [Class 11 Maths - Sets]\nIf set A has n elements, total number of non-empty proper subsets is:",
            "opts": ["2^n - 2", "2^n - 1", "2^n", "n^2 - 1"],
            "ans": "2^n - 2"
        },
        {
            "q": "📚 [Class 11 Physics - Gravitation]\nIf Earth shrinks to half radius without mass change, duration of a day will be:",
            "opts": ["6 Hours", "12 Hours", "24 Hours", "48 Hours"],
            "ans": "6 Hours"
        }
    ],
    "12": [
        {
            "q": "📚 [Class 12 Physics - Electrostatics]\nAn electric dipole in a uniform electric field experiences:",
            "opts": ["Only Torque, Net Force = 0", "Both Force & Torque", "Only Force, No Torque", "Neither Force nor Torque"],
            "ans": "Only Torque, Net Force = 0"
        },
        {
            "q": "📚 [Class 12 Physics - Optics]\nAt Brewster angle, reflected & refracted rays are:",
            "opts": ["Perpendicular (90 deg)", "Parallel", "Anti-parallel", "At 45 deg"],
            "ans": "Perpendicular (90 deg)"
        },
        {
            "q": "📚 [Class 12 Chemistry - Kinetics]\nFor a zero-order reaction, slope of [R] vs Time (t) graph is:",
            "opts": ["-k", "+k", "-k/2.303", "k/t"],
            "ans": "-k"
        },
        {
            "q": "📚 [Class 12 Maths - Matrices]\nIf A is invertible 3x3 matrix and |A| = 4, then |adj(A)| is:",
            "opts": ["16", "4", "64", "1/4"],
            "ans": "16"
        },
        {
            "q": "📚 [Class 12 Biology - Genetics]\nIn AaBb x AaBb, what is the ratio of homozygous dominant for both (AABB)?",
            "opts": ["1/16", "9/16", "3/16", "4/16"],
            "ans": "1/16"
        }
    ],
    "mind": [
        {"q": "🧠 [Logical Riddle]\nAisi kaun si cheez hai jo sookhte waqt geeli ho jati hai?", "opts": ["Towel", "Soap", "Paper", "Cloth"], "ans": "Towel"},
        {"q": "🧠 [Brain Teaser]\nKiske paas gale hote hain par sar nahi?", "opts": ["Shirt", "Bottle", "Tree", "Snake"], "ans": "Shirt"},
        {"q": "🧠 [Tricky Math]\nAgar 3 seb hain aur tumne 2 le liye, toh tumhare paas kitne seb bache?", "opts": ["2 Seb", "1 Seb", "3 Seb", "0 Seb"], "ans": "2 Seb"},
        {"q": "🧠 [Mind Sharp]\nWo kya hai jise aap bina chhuye tod sakte ho?", "opts": ["Promise", "Glass", "Plate", "Brick"], "ans": "Promise"}
    ]
}

def generate_code(length=5):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

# ==================== MAIN CATEGORY MENU ====================

@bot.message_handler(commands=['start', 'games', 'menu'])
def show_main_menu(message):
    try:
        chat_id = message.chat.id
        text = message.text.split()
        if len(text) > 1 and text[1].startswith("join_"):
            room_code = text[1].replace("join_", "")
            join_room_by_code(message.from_user, chat_id, room_code)
            return

        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton("🎮 Play & Fun Games (TTT / Bingo)", callback_data="sec_games"),
            InlineKeyboardButton("🧠 Logical & Brain Games (Maths / Riddles)", callback_data="sec_logic"),
            InlineKeyboardButton("📚 Study Based Quiz (CBSE 10, 11, 12)", callback_data="sec_study")
        )
        bot.send_message(
            chat_id,
            "🔥 **Welcome to 360 Arena!** 🔥\n\nKripya category select karein:",
            reply_markup=markup,
            parse_mode="Markdown"
        )
    except Exception as e:
        print(f"Error in show_main_menu: {e}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('sec_'))
def handle_sections(call):
    chat_id = call.message.chat.id
    sec = call.data.split('_')[1]

    if sec == "games":
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton("❌ Tic Tac Toe ⭕", callback_data="open_ttt_opt"),
            InlineKeyboardButton("🎲 Bingo 5x5", callback_data="menu_bingo"),
            InlineKeyboardButton("⬅️ Back to Menu", callback_data="sec_back")
        )
        bot.edit_message_text("🎮 **Play & Fun Games:**\nGame select karein:", chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup)

    elif sec == "logic":
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton("⚡ Maths Speed Battle", callback_data="menu_math"),
            InlineKeyboardButton("🧩 Tricky Riddles & Puzzles", callback_data="menu_mind"),
            InlineKeyboardButton("⬅️ Back to Menu", callback_data="sec_back")
        )
        bot.edit_message_text("🧠 **Logical & Brain Games:**\nChallenge select karein:", chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup)

    elif sec == "study":
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton("📘 Class 10 (Competency PYQs)", callback_data="cbse_start_10"),
            InlineKeyboardButton("📗 Class 11 (Concepts & PYQs)", callback_data="cbse_start_11"),
            InlineKeyboardButton("📕 Class 12 (Board PYQs & Tricky)", callback_data="cbse_start_12"),
            InlineKeyboardButton("⬅️ Back to Menu", callback_data="sec_back")
        )
        bot.edit_message_text("📚 **Study Based CBSE Competency Quizzes:**\nApni Class select karein:", chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup)

    elif sec == "back":
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton("🎮 Play & Fun Games (TTT / Bingo)", callback_data="sec_games"),
            InlineKeyboardButton("🧠 Logical & Brain Games (Maths / Riddles)", callback_data="sec_logic"),
            InlineKeyboardButton("📚 Study Based Quiz (CBSE 10, 11, 12)", callback_data="sec_study")
        )
        bot.edit_message_text("🔥 **Main Menu**\nCategory select karein:", chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup)

# ==================== QUIZZES (CBSE + LOGIC) ====================

@bot.callback_query_handler(func=lambda call: call.data.startswith('cbse_start_'))
def handle_cbse_start(call):
    cls = call.data.split('_')[2]
    send_quiz_question(call.message.chat.id, cls)

@bot.callback_query_handler(func=lambda call: call.data == 'menu_mind')
def handle_mind_start(call):
    send_quiz_question(call.message.chat.id, "mind")

def send_quiz_question(chat_id, category):
    q_list = CBSE_QUESTIONS.get(category, CBSE_QUESTIONS["10"])
    q_data = random.choice(q_list)
    opts = list(q_data['opts'])
    random.shuffle(opts)
    
    markup = InlineKeyboardMarkup(row_width=1)
    for opt in opts:
        markup.add(InlineKeyboardButton(opt, callback_data=f"qzans_{category}_{opt[:15]}_{q_data['ans'][:15]}"))
    
    bot.send_message(chat_id, f"{q_data['q']}", reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith('qzans_'))
def handle_quiz_answer(call):
    _, category, selected, correct = call.data.split('_', 3)
    user_name = call.from_user.first_name
    
    if selected.strip().lower() == correct.strip().lower():
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("➡️ Next Question", callback_data=f"cbse_start_{category}"))
        bot.send_message(call.message.chat.id, f"🎉 **Sahi Jawab!**\n**{user_name}** ne correct answer diya!", reply_markup=markup, parse_mode="Markdown")
        bot.delete_message(call.message.chat.id, call.message.message_id)
    else:
        bot.answer_callback_query(call.id, "❌ Galat jawab! Sahi option socho.", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data == 'menu_math')
def start_math_quiz(call):
    chat_id = call.message.chat.id
    n1, n2 = random.randint(10, 99), random.randint(2, 20)
    op = random.choice(MATH_OPS)
    ans = eval(f"{n1} {op} {n2}")
    options = list({ans, ans + random.randint(1, 5), ans - random.randint(1, 5), ans + 10})
    random.shuffle(options)
    markup = InlineKeyboardMarkup(row_width=2)
    for opt in options:
        markup.add(InlineKeyboardButton(str(opt), callback_data=f"math_ans_{opt}_{ans}"))
    bot.send_message(chat_id, f"⚡ **Maths Speed Battle:**\n\n**{n1} {op} {n2} = ?**", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('math_ans_'))
def handle_math_ans(call):
    _, _, selected, correct = call.data.split('_', 3)
    user_name = call.from_user.first_name
    if selected.strip() == correct.strip():
        bot.send_message(call.message.chat.id, f"🎉 Sahi Jawab! **{user_name}** ne answer diya: `{correct}`", parse_mode="Markdown")
        bot.delete_message(call.message.chat.id, call.message.message_id)
    else:
        bot.answer_callback_query(call.id, "❌ Galat jawab!")

# ==================== TIC TAC TOE ====================

@bot.callback_query_handler(func=lambda call: call.data == "open_ttt_opt")
def open_ttt_menu(call):
    chat_id = call.message.chat.id
    is_private = call.message.chat.type == "private"
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("🤖 Play vs AI (Single Player)", callback_data=f"ttt_mode_ai_{chat_id}"),
        InlineKeyboardButton("👥 1v1 Room Code (Dost ke sath DM)", callback_data=f"ttt_create_room_{chat_id}")
    )
    if not is_private:
        markup.add(InlineKeyboardButton("⚔️ Play in this Group", callback_data=f"ttt_join_{chat_id}"))
    bot.edit_message_text("❌⭕ **Tic Tac Toe Mode:**", chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('ttt_create_room_'))
def create_ttt_room(call):
    user = call.from_user
    code = "TTT" + generate_code(4)
    rooms[code] = {
        'game': 'ttt',
        'host': user,
        'guest': None,
        'board': [" "]*9,
        'turn': 'X',
        'host_msg_id': None,
        'guest_msg_id': None
    }
    bot_user = "Gaming_360_bot"
    share_url = f"https://t.me/share/url?url=https://t.me/{bot_user}?start=join_{code}&text=Aaja%20Tic%20Tac%20Toe%20khelte%20hain!%20Room%20Code:%20{code}"
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📲 Dost ko Invite Bhejo", url=share_url))
    bot.send_message(call.message.chat.id, f"🎟️ **Match Room Ready!**\n\n📌 Room Code: `{code}`\n\nDost ko invite bhejo ya code share karo.", reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(commands=['join'])
def cmd_join(message):
    args = message.text.split()
    if len(args) < 2:
        bot.send_message(message.chat.id, "❌ Kripya code likhein! Example: `/join TTT1234`", parse_mode="Markdown")
        return
    code = args[1].strip().upper()
    join_room_by_code(message.from_user, message.chat.id, code)

def join_room_by_code(guest_user, guest_chat_id, code):
    room = rooms.get(code)
    if not room:
        bot.send_message(guest_chat_id, "❌ Yeh Room Code expire ya galat hai!")
        return
    if room['guest'] is not None and room['guest'].id != guest_user.id:
        bot.send_message(guest_chat_id, "❌ Yeh room full ho chuka hai!")
        return
    if room['host'].id == guest_user.id:
        bot.send_message(guest_chat_id, "⚠️ Yeh room aapne hi banaya hai! Apne dost ko invite bhejo.")
        return
    
    room['guest'] = guest_user
    host_chat_id = room['host'].id
    markup = get_dm_ttt_markup(code)
    m1 = bot.send_message(host_chat_id, f"🔥 **Match Start!**\n❌ (You): {room['host'].first_name}\n⭕: {guest_user.first_name}\nTurn: **{room['host'].first_name}**", reply_markup=markup)
    m2 = bot.send_message(guest_chat_id, f"🔥 **Match Start!**\n❌: {room['host'].first_name}\n⭕ (You): {guest_user.first_name}\nTurn: **{room['host'].first_name}**", reply_markup=markup)
    room['host_msg_id'] = m1.message_id
    room['guest_msg_id'] = m2.message_id

def get_dm_ttt_markup(code):
    r = rooms[code]
    markup = InlineKeyboardMarkup(row_width=3)
    buttons = [InlineKeyboardButton(r['board'][i] if r['board'][i] != " " else "▫️", callback_data=f"dmttt_{code}_{i}") for i in range(9)]
    markup.add(*buttons)
    return markup

@bot.callback_query_handler(func=lambda call: call.data.startswith('dmttt_'))
def handle_dm_ttt_move(call):
    _, code, idx = call.data.split('_')
    idx = int(idx)
    r = rooms.get(code)
    if not r or not r['guest']: return

    curr_player = r['host'] if r['turn'] == 'X' else r['guest']
    if call.from_user.id != curr_player.id:
        bot.answer_callback_query(call.id, "Abhi aapki turn nahi hai!")
        return

    if r['board'][idx] != " ":
        bot.answer_callback_query(call.id, "Slot bhara hua hai!")
        return

    r['board'][idx] = r['turn']
    w = check_ttt_winner(r['board'])
    markup = get_dm_ttt_markup(code)
    
    if w:
        winner_text = "🤝 **Match Draw!**" if w == "Tie" else f"🏆 **{(r['host'].first_name if w == 'X' else r['guest'].first_name)} Match Jeet Gaya! ({w})**"
        try:
            bot.edit_message_text(winner_text, chat_id=r['host'].id, message_id=r['host_msg_id'], reply_markup=markup, parse_mode="Markdown")
            bot.edit_message_text(winner_text, chat_id=r['guest'].id, message_id=r['guest_msg_id'], reply_markup=markup, parse_mode="Markdown")
        except: pass
        del rooms[code]
        return

    r['turn'] = 'O' if r['turn'] == 'X' else 'X'
    next_p = r['host'].first_name if r['turn'] == 'X' else r['guest'].first_name
    txt = f"Turn: **{next_p}** ({r['turn']})"
    try:
        bot.edit_message_text(txt, chat_id=r['host'].id, message_id=r['host_msg_id'], reply_markup=markup, parse_mode="Markdown")
        bot.edit_message_text(txt, chat_id=r['guest'].id, message_id=r['guest_msg_id'], reply_markup=markup, parse_mode="Markdown")
    except: pass

def check_ttt_winner(b):
    wins = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]
    for x, y, z in wins:
        if b[x] == b[y] == b[z] and b[x] != " ":
            return b[x]
    if " " not in b: return "Tie"
    return None

def get_ttt_markup(chat_id):
    g = ttt_games[chat_id]
    markup = InlineKeyboardMarkup(row_width=3)
    buttons = [InlineKeyboardButton(g['board'][i] if g['board'][i] != " " else "▫️", callback_data=f"ttt_mv_{chat_id}_{i}") for i in range(9)]
    markup.add(*buttons)
    return markup

@bot.callback_query_handler(func=lambda call: call.data.startswith('ttt_mode_ai_'))
def ttt_ai_diff_menu(call):
    chat_id = int(call.data.split('_')[3])
    markup = InlineKeyboardMarkup(row_width=3)
    markup.add(
        InlineKeyboardButton("🟢 Easy", callback_data=f"ttt_aidiff_{chat_id}_easy"),
        InlineKeyboardButton("🟡 Medium", callback_data=f"ttt_aidiff_{chat_id}_medium"),
        InlineKeyboardButton("🔴 Hard (Unbeatable)", callback_data=f"ttt_aidiff_{chat_id}_hard")
    )
    bot.send_message(chat_id, "🤖 **AI Difficulty Chuno:**", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('ttt_aidiff_'))
def start_ttt_ai(call):
    _, _, chat_id, diff = call.data.split('_')
    chat_id = int(chat_id)
    user = call.from_user
    ttt_games[chat_id] = {'mode': 'ai', 'p1': user, 'diff': diff, 'board': [" "]*9, 'turn': 'X'}
    bot.send_message(chat_id, f"🤖 **Match vs AI ({diff.capitalize()})!**\n❌: {user.first_name}\n⭕: AI Bot\nTumhari turn!", reply_markup=get_ttt_markup(chat_id))

def minimax(board, is_max):
    res = check_ttt_winner(board)
    if res == 'O': return 10
    if res == 'X': return -10
    if res == 'Tie': return 0
    if is_max:
        best = -1000
        for i in range(9):
            if board[i] == " ":
                board[i] = 'O'
                best = max(best, minimax(board, False))
                board[i] = " "
        return best
    else:
        best = 1000
        for i in range(9):
            if board[i] == " ":
                board[i] = 'X'
                best = min(best, minimax(board, True))
                board[i] = " "
        return best

def get_ai_move(board, diff):
    empty = [i for i, v in enumerate(board) if v == " "]
    if not empty: return None
    if diff == "easy": return random.choice(empty)
    if diff == "medium" and random.random() < 0.5: return random.choice(empty)
    best_val, best_move = -1000, empty[0]
    for i in empty:
        board[i] = 'O'
        move_val = minimax(board, False)
        board[i] = " "
        if move_val > best_val:
            best_val, best_move = move_val, i
    return best_move

@bot.callback_query_handler(func=lambda call: call.data.startswith('ttt_join_'))
def join_ttt(call):
    chat_id = int(call.data.split('_')[2])
    user = call.from_user
    if chat_id not in ttt_games:
        ttt_games[chat_id] = {'mode': 'pvp', 'p1': user, 'p2': None, 'board': [" "]*9, 'turn': 'X'}
        bot.send_message(chat_id, f"✅ **{user.first_name}** (X) ready hai! Koi aur Join dabaye.")
    elif ttt_games[chat_id].get('p2') is None and ttt_games[chat_id]['p1'].id != user.id:
        ttt_games[chat_id]['p2'] = user
        p1_name = ttt_games[chat_id]['p1'].first_name
        bot.send_message(chat_id, f"🔥 Game Start!\n❌: {p1_name}\n⭕: {user.first_name}\nBaari: {p1_name}", reply_markup=get_ttt_markup(chat_id))

@bot.callback_query_handler(func=lambda call: call.data.startswith('ttt_mv_'))
def handle_ttt_move(call):
    _, _, chat_i
