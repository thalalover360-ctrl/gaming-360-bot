import os
import random
import sqlite3
import telebot
from telebot import types

# 1. BOT CONFIGURATION
BOT_TOKEN = os.getenv("BOT_TOKEN", "8963859901:AAGT3dYv2NraTFV69ZBQ8f5jEcqhcuIWcis")
bot = telebot.TeleBot(BOT_TOKEN)

# 2. DATABASE SETUP
DB_NAME = "arcade_master.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            score INTEGER DEFAULT 0,
            games_played INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def add_or_update_user(user_id, username, first_name):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (user_id, username, first_name)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            username=excluded.username,
            first_name=excluded.first_name
    """, (user_id, username, first_name))
    conn.commit()
    conn.close()

def update_score(user_id, points):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users 
        SET score = score + ?, games_played = games_played + 1 
        WHERE user_id = ?
    """, (points, user_id))
    conn.commit()
    conn.close()

def get_user_stats(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT score, games_played FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row if row else (0, 0)

init_db()

# 3. MAIN MENU UI
def get_main_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🎯 1. Guess Game (Movies, Sports, Anime)", callback_data="game_guess"),
        types.InlineKeyboardButton("🧠 2. Maths & Brain Quiz (Hard Level)", callback_data="game_quiz"),
        types.InlineKeyboardButton("🔤 3. Word Games (Guess, Scramble)", callback_data="game_word"),
        types.InlineKeyboardButton("❌⭕ 4. Tic Tac Toe (AI & PvP)", callback_data="game_tictactoe"),
        types.InlineKeyboardButton("🃏 5. Memory Game (4x4 Matching)", callback_data="game_memory"),
        types.InlineKeyboardButton("🎱 6. Bingo 5x5 (DM Realtime Sync)", callback_data="game_bingo"),
        types.InlineKeyboardButton("💣 7. Mines & Dragon (Survival Duel)", callback_data="game_mines"),
        types.InlineKeyboardButton("📊 My Stats & Scorecard", callback_data="view_stats")
    )
    return markup

@bot.message_handler(commands=['start', 'menu'])
def send_welcome(message):
    add_or_update_user(message.from_user.id, message.from_user.username, message.from_user.first_name)
    bot.send_message(
        message.chat.id,
        f"👋 *Welcome {message.from_user.first_name} to 7-in-1 Arcade Hub!*\n\nNiche se koi bhi game choose karo:",
        parse_mode="Markdown",
        reply_markup=get_main_menu()
    )

# 4. GUESS DATA
QUESTIONS_DATA = {
    "movie": {
        "easy": [
            {"hint": "🎬 Dialog: 'Mogambo khush hua!'", "ans": "Mr. India", "options": ["Mr. India", "Sholay", "Don", "Krrish"]},
            {"hint": "🎬 'Kitne aadmi the?' iconic dialogue kis movie ka hai?", "ans": "Sholay", "options": ["Deewar", "Sholay", "Zanjeer", "Lagaan"]},
            {"hint": "🎬 Aamir Khan ki movie jisme 3 engineering students ki kahani hai.", "ans": "3 Idiots", "options": ["PK", "Dangal", "3 Idiots", "Taare Zameen Par"]}
        ],
        "med": [
            {"hint": "🎬 Rajkummar Rao aur Shraddha Kapoor ki horror-comedy movie.", "ans": "Stree", "options": ["Bhediya", "Roohi", "Stree", "Bhool Bhulaiyaa"]},
            {"hint": "🎬 1983 Cricket World Cup victory par bani Ranveer Singh ki movie.", "ans": "83", "options": ["MS Dhoni", "83", "Jersey", "Lagaan"]},
            {"hint": "🎬 'Babu Moshai, zindagi badi honi chahiye, lambi nahi.'", "ans": "Anand", "options": ["Anand", "Kati Patang", "Aradhana", "Amar Prem"]}
        ],
        "hard": [
            {"hint": "🎬 Tumbbad movie ke main rakshas ka kya naam tha?", "ans": "Hastar", "options": ["Hastar", "Brahmarakshas", "Betaal", "Yaksha"]},
            {"hint": "🎬 Gangs of Wasseypur me Faizal Khan ka role kisne play kiya tha?", "ans": "Nawazuddin Siddiqui", "options": ["Manoj Bajpayee", "Pankaj Tripathi", "Nawazuddin Siddiqui", "Jaideep Ahlawat"]},
            {"hint": "🎬 Christopher Nolan ki time inversion par based movie kaunsi hai?", "ans": "Tenet", "options": ["Inception", "Interstellar", "Tenet", "Memento"]}
        ]
    },
    "sports": {
        "easy": [
            {"hint": "🏏 'Master Blaster' aur 'God of Cricket' kise kaha jata hai?", "ans": "Sachin Tendulkar", "options": ["Sachin Tendulkar", "Virat Kohli", "MS Dhoni", "Rohit Sharma"]},
            {"hint": "🏏 2011 ICC Cricket World Cup ke final me winning six kisne mara tha?", "ans": "MS Dhoni", "options": ["Gautam Gambhir", "Yuvraj Singh", "MS Dhoni", "Suresh Raina"]},
            {"hint": "🏏 'Hitman' ke naam se kaunsa Indian batsman famous hai?", "ans": "Rohit Sharma", "options": ["KL Rahul", "Rohit Sharma", "Shikhar Dhawan", "Hardik Pandya"]}
        ],
        "med": [
            {"hint": "🏏 2007 T20 World Cup me 1 over me 6 sixes kisne mare the?", "ans": "Yuvraj Singh", "options": ["Virender Sehwag", "Yuvraj Singh", "Chris Gayle", "Shahid Afridi"]},
            {"hint": "🏏 IPL ke pehle season (2008) ki winner team kaunsi thi?", "ans": "Rajasthan Royals", "options": ["CSK", "MI", "Rajasthan Royals", "KKR"]},
            {"hint": "🏏 Test cricket me sabse zyada wickets (800) lene wale bowler kaun hain?", "ans": "Muttiah Muralitharan", "options": ["Shane Warne", "Anil Kumble", "Muttiah Muralitharan", "James Anderson"]}
        ],
        "hard": [
            {"hint": "🏏 1999 me Pakistan ke khilaf ek Test inning me 10 wickets kisne liye the?", "ans": "Anil Kumble", "options": ["Kapil Dev", "Anil Kumble", "Harbhajan Singh", "Zaheer Khan"]},
            {"hint": "🏏 World Cup me pehli double century kisne banayi thi?", "ans": "Chris Gayle", "options": ["Martin Guptill", "Rohit Sharma", "Chris Gayle", "AB de Villiers"]},
            {"hint": "🏏 Virat Kohli ne T20 World Cup 2022 me 82* runs kis team ke khilaf banaye the?", "ans": "Pakistan", "options": ["Australia", "England", "Pakistan", "South Africa"]}
        ]
    },
    "anime": {
        "easy": [
            {"hint": "🍥 'Dattebayo!' bolne wala Orange kapde pehanne wala ninja kaun hai?", "ans": "Naruto Uzumaki", "options": ["Sasuke Uchiha", "Naruto Uzumaki", "Kakashi", "Boruto"]},
            {"hint": "🐱 Nobita ki madad karne wala 22nd century ka robot cat?", "ans": "Doraemon", "options": ["Ninja Hattori", "Shinchan", "Doraemon", "Perman"]},
            {"hint": "⚡ 'Pika Pika!' bolne wala Ash Ketchum ka main Pokemon?", "ans": "Pikachu", "options": ["Charizard", "Pikachu", "Bulbasaur", "Squirtle"]}
        ],
        "med": [
            {"hint": "🏴‍☠️ King of the Pirates banne ke liye Straw Hat pehanne wala captain?", "ans": "Monkey D. Luffy", "options": ["Zoro", "Monkey D. Luffy", "Sanji", "Shanks"]},
            {"hint": "📓 Ek notebook jisme naam likhne se insaan mar jata hai?", "ans": "Death Note", "options": ["Code Geass", "Monster", "Death Note", "Attack on Titan"]},
            {"hint": "🥋 Ultra Instinct form kis anime character ki hai?", "ans": "Goku", "options": ["Vegeta", "Goku", "Gohan", "Broly"]}
        ],
        "hard": [
            {"hint": "⚔️ Attack on Titan me Eren Jaeger ke pass start me kaunsa Titan tha?", "ans": "Attack Titan", "options": ["Colossal Titan", "Armored Titan", "Attack Titan", "Beast Titan"]},
            {"hint": "👁️ Sasuke ki aankh me Mangekyo Sharingan ke baad kaunsi eye aati hai?", "ans": "Rinnegan", "options": ["Byakugan", "Rinnegan", "Tenseigan", "Jougan"]},
            {"hint": "🗡️ Demon Slayer me Tanjiro Kamado ki pehli breathing style kaunsi thi?", "ans": "Water Breathing", "options": ["Sun Breathing", "Water Breathing", "Flame Breathing", "Wind Breathing"]}
        ]
    }
}

active_guess_sessions = {}

def get_guess_category_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🎬 1. Movies & Bollywood", callback_data="g_cat_movie"),
        types.InlineKeyboardButton("🏏 2. Sports & Cricket", callback_data="g_cat_sports"),
        types.InlineKeyboardButton("🍥 3. Anime & Cartoons", callback_data="g_cat_anime"),
        types.InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")
    )
    return markup

def get_guess_diff_menu(category):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🟢 Easy (+10 pts)", callback_data=f"g_diff_{category}_easy"),
        types.InlineKeyboardButton("🟡 Medium (+20 pts)", callback_data=f"g_diff_{category}_med"),
        types.InlineKeyboardButton("🔴 Hard (+30 pts)", callback_data=f"g_diff_{category}_hard"),
        types.InlineKeyboardButton("🔙 Back to Categories", callback_data="game_guess")
    )
    return markup

# 5. TIC TAC TOE
ttt_games = {}

def create_ttt_board(game_id):
    game = ttt_games.get(game_id)
    if not game:
        return None
    board = game["board"]
    markup = types.InlineKeyboardMarkup(row_width=3)
    buttons = []
    for i in range(9):
        val = board[i]
        text = "❌" if val == "X" else ("⭕" if val == "O" else "⬜")
        cb = f"ttt_move_{game_id}_{i}" if val == " " and not game["game_over"] else "none"
        buttons.append(types.InlineKeyboardButton(text, callback_data=cb))
    markup.add(buttons[0], buttons[1], buttons[2])
    markup.add(buttons[3], buttons[4], buttons[5])
    markup.add(buttons[6], buttons[7], buttons[8])
    if game["game_over"]:
        markup.add(types.InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu"))
    else:
        markup.add(types.InlineKeyboardButton("🚪 Forfeit", callback_data="main_menu"))
    return markup

def check_ttt_winner(b):
    wins = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]
    for x,y,z in wins:
        if b[x] != " " and b[x] == b[y] == b[z]:
            return b[x]
    return "Draw" if " " not in b else None

def get_ai_move(b):
    for i in range(9):
        if b[i] == " ":
            b[i] = "O"
            if check_ttt_winner(b) == "O":
                b[i] = " "; return i
            b[i] = " "
    for i in range(9):
        if b[i] == " ":
            b[i] = "X"
            if check_ttt_winner(b) == "X":
                b[i] = " "; return i
            b[i] = " "
    if b[4] == " ": return 4
    empty = [i for i, v in enumerate(b) if v == " "]
    return random.choice(empty) if empty else None

def get_ttt_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🤖 Play vs Bot (AI)", callback_data="ttt_start_ai"),
        types.InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")
    )
    return markup
# ==================== SLOT 2: QUIZ, WORDS, MINES, BINGO & ROUTING ==================== #

# --- 6. QUIZ DATA ---
QUIZ_DATA = {
    "maths": [
        {"q": "🔢 If log₂(x) + log₂(x - 2) = 3, find the real value of x:", "options": ["4", "2", "-2", "8"], "ans": "4", "exp": "log₂(x(x - 2)) = 3 ⟹ x² - 2x = 8 ⟹ x = 4."},
        {"q": "🔢 Find the value of: sin²(10°) + sin²(20°) + ... + sin²(90°)", "options": ["5", "4.5", "5.5", "4"], "ans": "5", "exp": "Pairs sum to 1 + sin²(90) = 4 + 1 = 5."},
        {"q": "🔢 If the 3rd term of a G.P. is 4, product of first 5 terms is:", "options": ["4⁵ = 1024", "4³ = 64", "4⁴ = 256", "512"], "ans": "4⁵ = 1024", "exp": "Product = a⁵ = 4⁵ = 1024."},
        {"q": "🔢 Limit: lim(x→0) [sin(5x) / tan(2x)] = ?", "options": ["5/2", "2/5", "1", "0"], "ans": "5/2", "exp": "Standard limits evaluate to 5/2."}
    ],
    "brain": [
        {"q": "🧠 Series: 2, 6, 12, 20, 30, 42, ?", "options": ["56", "54", "60", "52"], "ans": "56", "exp": "Pattern: n(n+1) ⟹ 7×8 = 56."},
        {"q": "🧠 A doctor gives 3 pills to take every 30 mins. How long do they last?", "options": ["60 mins", "90 mins", "30 mins", "120 mins"], "ans": "60 mins", "exp": "Pills taken at 0, 30, and 60 minutes."},
        {"q": "🧠 If 5 cats catch 5 mice in 5 mins, how many cats catch 100 mice in 100 mins?", "options": ["5", "100", "20", "50"], "ans": "5", "exp": "Rate is 1 cat = 1 mouse / 5 min. 5 cats catch 100 in 100 mins."}
    ]
}

active_quiz_sessions = {}

def get_quiz_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("📐 1. Hard Maths", callback_data="qz_m_maths"),
        types.InlineKeyboardButton("🧩 2. Brain Riddles", callback_data="qz_m_brain"),
        types.InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")
    )
    return markup

# --- 7. WORD GAMES ---
WORD_DATABASE = [
    {"word": "PYTHON", "hint": "A popular high-level programming language"},
    {"word": "GALAXY", "hint": "A massive system of stars, gas, and dust"},
    {"word": "CRICKET", "hint": "A game with bat, ball, and wickets"},
    {"word": "OXYGEN", "hint": "Essential gas for human breathing"},
    {"word": "GRAVITY", "hint": "Force attracting bodies toward earth"}
]

# --- 8. MEMORY GAME ---
MEMORY_EMOJIS = ["🦁", "👑", "⚡", "🍕", "🚀", "💎", "🔥", "⚽"]
memory_games = {}

def render_memory_grid(gid):
    g = memory_games.get(gid)
    if not g: return None
    markup = types.InlineKeyboardMarkup(row_width=4)
    buttons = []
    for i in range(16):
        text = g["cards"][i] if i in g["matched"] or i in g["revealed"] else "❓"
        cb = f"mem_flip_{gid}_{i}" if not g["game_over"] and i not in g["matched"] and i not in g["revealed"] else "none"
        buttons.append(types.InlineKeyboardButton(text, callback_data=cb))
    for r in range(0, 16, 4):
        markup.add(buttons[r], buttons[r+1], buttons[r+2], buttons[r+3])
    markup.add(types.InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu"))
    return markup

# --- 9. MINES GAME ---
mines_games = {}

def render_mines_board(gid):
    g = mines_games.get(gid)
    if not g: return None
    markup = types.InlineKeyboardMarkup(row_width=5)
    buttons = []
    for i in range(25):
        text = g["board"][i] if i in g["revealed"] or g["game_over"] else "❓"
        cb = f"mn_click_{gid}_{i}" if not g["game_over"] and i not in g["revealed"] else "none"
        buttons.append(types.InlineKeyboardButton(text, callback_data=cb))
    for r in range(0, 25, 5):
        markup.add(buttons[r], buttons[r+1], buttons[r+2], buttons[r+3], buttons[r+4])
    if g["game_over"]:
        markup.add(types.InlineKeyboardButton("🔄 Play Again", callback_data="game_mines"), types.InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu"))
    else:
        markup.add(types.InlineKeyboardButton("💰 Cashout", callback_data=f"mn_cash_{gid}"), types.InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu"))
    return markup

# --- 10. BINGO ENGINE ---
bingo_games = {}
bingo_waiting_room = {}

def generate_bingo_board():
    nums = list(range(1, 26))
    random.shuffle(nums)
    return nums

def check_bingo_lines(board, marked):
    lines = 0
    for r in range(5):
        if all((r * 5 + c) in marked for c in range(5)): lines += 1
    for c in range(5):
        if all((r * 5 + c) in marked for r in range(5)): lines += 1
    if all((i * 6) in marked for i in range(5)): lines += 1
    if all(((i + 1) * 4) in marked for i in range(5)): lines += 1
    return min(lines, 5)

def render_bingo_board(game_id, user_id):
    game = bingo_games.get(game_id)
    if not game: return None
    board = game["players"][user_id]["board"]
    marked = game["marked"]
    markup = types.InlineKeyboardMarkup(row_width=5)
    buttons = []
    for num in board:
        btn_text = "❌" if num in marked else str(num)
        cb = f"bg_cut_{game_id}_{num}" if game["turn"] == user_id and num not in marked and not game["game_over"] else "none"
        buttons.append(types.InlineKeyboardButton(btn_text, callback_data=cb))
    for i in range(0, 25, 5):
        markup.add(buttons[i], buttons[i+1], buttons[i+2], buttons[i+3], buttons[i+4])
    markup.add(types.InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu"))
    return markup

def update_bingo_dms(game_id, note=""):
    game = bingo_games.get(game_id)
    if not game: return
    p1, p2 = game["player_ids"]
    letters = ["B", "I", "N", "G", "O"]

    for p in [p1, p2]:
        opp = p2 if p == p1 else p1
        my_board = game["players"][p]["board"]
        marked_idx = [i for i, v in enumerate(my_board) if v in game["marked"]]
        lines = check_bingo_lines(my_board, marked_idx)
        status_txt = " ".join([f"🔥*{letters[i]}*" if i < lines else f"⚪{letters[i]}" for i in range(5)])

        turn_txt = "👉 *Aapki Chaal Hai!*" if game["turn"] == p and not game["game_over"] else f"⏳ *{game['players'][opp]['name']} ki baari...*"
        text = f"🎱 *BINGO 5x5 MATCH*\n🎯 Progress: {status_txt} ({lines}/5 Lines)\n\n{note}\n{turn_txt}"
        if game["game_over"]:
            text = f"🏆 *BINGO WINNER:* {game['players'][game['winner']]['name']} jeet gaya!"

        try:
            bot.edit_message_text(text, chat_id=p, message_id=game["players"][p]["msg_id"], parse_mode="Markdown", reply_markup=render_bingo_board(game_id, p))
        except Exception:
            pass

@bot.message_handler(commands=['bingo'])
def cmd_bingo_group(message):
    if message.chat.type in ['group', 'supergroup']:
        game_code = f"bg_{message.chat.id}_{message.message_id}"
        bingo_waiting_room[game_code] = {"p1_id": message.from_user.id, "p1_name": message.from_user.first_name, "group_id": message.chat.id}
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🎮 Join Bingo Challenge", callback_data=f"join_bg_{game_code}"))
        bot.reply_to(message, f"🎱 *BINGO 5x5 CHALLENGE!*\nHost: *{message.from_user.first_name}*\nNiche click karke join karo:", parse_mode="Markdown", reply_markup=markup)
    else:
        bot.reply_to(message, "Ye command group me dosto ke sath khelne ke liye use karo!")

# --- 11. MASTER CALLBACK HANDLER ---
@bot.callback_query_handler(func=lambda call: True)
def on_callback(call):
    uid, data, cid, mid = call.from_user.id, call.data, call.message.chat.id, call.message.message_id

    if data == "main_menu":
        bot.edit_message_text("🎮 *Main Game Menu:*", chat_id=cid, message_id=mid, parse_mode="Markdown", reply_markup=get_main_menu())

    elif data == "view_stats":
        s, p = get_user_stats(uid)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu"))
        bot.edit_message_text(f"📊 *Profile:*\n👤 Name: {call.from_user.first_name}\n🏆 Score: `{s}` pts\n🎮 Played: `{p}`", chat_id=cid, message_id=mid, parse_mode="Markdown", reply_markup=markup)

    # Guess Game
    elif data == "game_guess":
        bot.edit_message_text("🎯 *GUESS GAME* - Category chun lo:", chat_id=cid, message_id=mid, parse_mode="Markdown", reply_markup=get_guess_category_menu())

    elif data.startswith("g_cat_"):
        cat = data.replace("g_cat_", "")
        bot.edit_message_text(f"🎯 *Level Chun Lo:*", chat_id=cid, message_id=mid, reply_markup=get_guess_diff_menu(cat))

    elif data.startswith("g_diff_"):
        _, _, cat, diff = data.split("_")
        q = random.choice(QUESTIONS_DATA[cat][diff])
        active_guess_sessions[uid] = {"ans": q["ans"], "pts": 10 if diff == "easy" else (20 if diff == "med" else 30), "cat": cat, "diff": diff}
        opts = list(q["options"])
        random.shuffle(opts)
        markup = types.InlineKeyboardMarkup(row_width=2)
        for o in opts: markup.add(types.InlineKeyboardButton(o, callback_data=f"g_a_{o}"))
        markup.add(types.InlineKeyboardButton("🔙 Back", callback_data=f"g_cat_{cat}"))
        bot.edit_message_text(f"🎯 *GUESS:* {q['hint']}", chat_id=cid, message_id=mid, parse_mode="Markdown", reply_markup=markup)

    elif data.startswith("g_a_"):
        ans = data.replace("g_a_", "")
        sess = active_guess_sessions.get(uid)
        if not sess: return
        correct = sess["ans"]
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔁 Next", callback_data=f"g_diff_{sess['cat']}_{sess['diff']}"), types.InlineKeyboardButton("🏠 Menu", callback_data="main_menu"))
        if ans == correct:
            update_score(uid, sess["pts"])
            bot.edit_message_text(f"🎉 *Sahi Jawab!* (+{sess['pts']} pts)", chat_id=cid, message_id=mid, parse_mode="Markdown", reply_markup=markup)
        else:
            bot.edit_message_text(f"❌ *Galat!* Sahi answer tha: *{correct}*", chat_id=cid, message_id=mid, parse_mode="Markdown", reply_markup=markup)

    # Quiz Game
    elif data == "game_quiz":
        bot.edit_message_text("🧠 *MATHS & BRAIN QUIZ:*", chat_id=cid, message_id=mid, parse_mode="Markdown", reply_markup=get_quiz_menu())

    elif data.startswith("qz_m_"):
        mode = data.replace("qz_m_", "")
        item = random.choice(QUIZ_DATA[mode])
        active_quiz_sessions[uid] = {"ans": item["ans"], "exp": item["exp"], "mode": mode}
        opts = list(item["options"])
        random.shuffle(opts)
        markup = types.InlineKeyboardMarkup(row_width=2)
        for o in opts: markup.add(types.InlineKeyboardButton(o, callback_data=f"qz_a_{o}"))
        markup.add(types.InlineKeyboardButton("🔙 Back", callback_data="game_quiz"))
        bot.edit_message_text(f"{item['q']}", chat_id=cid, message_id=mid, parse_mode="Markdown", reply_markup=markup)

    elif data.startswith("qz_a_"):
        ans = data.replace("qz_a_", "")
        sess = active_quiz_sessions.get(uid)
        if not sess: return
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔁 Next", callback_data=f"qz_m_{sess['mode']}"), types.InlineKeyboardButton("🏠 Menu", callback_data="main_menu"))
        if ans == sess["ans"]:
            update_score(uid, 25)
            bot.edit_message_text(f"🎉 *Sahi Jawab!* (+25 pts)\n\n💡 {sess['exp']}", chat_id=cid, message_id=mid, parse_mode="Markdown", reply_markup=markup)
        else:
            bot.edit_message_text(f"❌ *Galat!* Sahi answer: *{sess['ans']}*\n\n💡 {sess['exp']}", chat_id=cid, message_id=mid, parse_mode="Markdown", reply_markup=markup)

    # Word Game
    elif data == "game_word":
        item = random.choice(WORD_DATABASE)
        word, scrambled = item["word"], list(item["word"])
        while "".join(scrambled) == word: random.shuffle(scrambled)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("👀 Reveal", callback_data=f"wrd_r_{word}"), types.InlineKeyboardButton("🔁 Next", callback_data="game_word"), types.InlineKeyboardButton("🏠 Menu", callback_data="main_menu"))
        bot.edit_message_text(f"🔤 *Word Scramble:*\n\nWord: *`{' '.join(scrambled)}`*\n💡 Clue: _{item['hint']}_", chat_id=cid, message_id=mid, parse_mode="Markdown", reply_markup=markup)

    elif data.startswith("wrd_r_"):
        w = data.replace("wrd_r_", "")
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔁 Next Word", callback_data="game_word"), types.InlineKeyboardButton("🏠 Menu", callback_data="main_menu"))
        bot.edit_message_text(f"💡 Sahi word tha: *{w}*", chat_id=cid, message_id=mid, parse_mode="Markdown", reply_markup=markup)

    # Tic Tac Toe
    elif data == "game_tictactoe":
        bot.edit_message_text("❌⭕ *Tic Tac Toe:*", chat_id=cid, message_id=mid, parse_mode="Markdown", reply_markup=get_ttt_menu())

    elif data == "ttt_start_ai":
        gid = f"ttt_{uid}_{random.randint(100,999)}"
        ttt_games[gid] = {"board": [" "] * 9, "turn": "X", "game_over": False}
        bot.edit_message_text("❌⭕ *Tic Tac Toe vs Bot*\nAap: ❌ | Bot: ⭕", chat_id=cid, message_id=mid, parse_mode="Markdown", reply_markup=create_ttt_board(gid))

    elif data.startswith("ttt_move_"):
        parts = data.split("_")
        gid, idx = f"ttt_{parts[2]}_{parts[3]}", int(parts[4])
        g = ttt_games.get(gid)
        if not g or g["game_over"] or g["board"][idx] != " ": return

        g["board"][idx] = "X"
        win = check_ttt_winner(g["board"])
        if win:
            g["game_over"] = True
            if win == "X": update_score(uid, 15)
            bot.edit_message_text("🎉 *Aap Jeet Gaye!* (+15 pts)" if win == "X" else "🤝 *Draw!*", chat_id=cid, message_id=mid, parse_mode="Markdown", reply_markup=create_ttt_board(gid))
            return

        ai = get_ai_move(g["board"])
        if ai is not None:
            g["board"][ai] = "O"
            win = check_ttt_winner(g["board"])
            if win:
                g["game_over"] = True
                bot.edit_message_text("🤖 *Bot Jeet Gaya!*" if win == "O" else "🤝 *Draw!*", chat_id=cid, message_id=mid, parse_mode="Markdown", reply_markup=create_ttt_board(gid))
                return

        bot.edit_message_text("❌⭕ *Aapki Chaal (❌):*", chat_id=cid, message_id=mid, parse_mode="Markdown", reply_markup=create_ttt_board(gid))

    # Memory Game
    elif data == "game_memory":
        gid = f"mem_{uid}_{random.randint(100,999)}"
        cards = MEMORY_EMOJIS * 2
        random.shuffle(cards)
        memory_games[gid] = {"cards": cards, "revealed": [], "matched": [], "game_over": False}
        bot.edit_message_text("🃏 *Memory Game:* Pairs match karo:", chat_id=cid, message_id=mid, parse_mode="Markdown", reply_markup=render_memory_grid(gid))

    elif data.startswith("mem_flip_"):
        parts = data.split("_")
        gid, idx = f"mem_{parts[2]}_{parts[3]}", int(parts[4])
        g = memory_games.get(gid)
        if not g or idx in g["revealed"] or idx in g["matched"] or g["game_over"]: return

        g["revealed"].append(idx)
        if len(g["revealed"]) == 2:
            i1, i2 = g["revealed"]
            if g["cards"][i1] == g["cards"][i2]:
                g["matched"].extend([i1, i2])
                g["revealed"] = []
                if len(g["matched"]) == 16:
                    g["game_over"] = True
                    update_score(uid, 30)
                    bot.edit_message_text("🏆 *Shabash! Saare pairs match ho gaye!* (+30 pts)", chat_id=cid, message_id=mid, parse_mode="Markdown", reply_markup=render_memory_grid(gid))
                    return
            else:
                bot.edit_message_text("❌ Match nahi hua!", chat_id=cid, message_id=mid, reply_markup=render_memory_grid(gid))
                g["revealed"] = []
                return
        bot.edit_message_text("🃏 Pairs dhoondo:", chat_id=cid, message_id=mid, reply_markup=render_memory_grid(gid))

    # Mines Game
    elif data == "game_mines":
        gid = f"mn_{uid}_{random.randint(100,999)}"
        bd = ["🐉"] * 5 + ["💎"] * 20
        random.shuffle(bd)
        mines_games[gid] = {"board": bd, "revealed": [], "score": 0, "game_over": False}
        bot.edit_message_text("💣 *Mines Survival:* Diamond 💎 nikalo, Dragon 🐉 se bacho:", chat_id=cid, message_id=mid, parse_mode="Markdown", reply_markup=render_mines_board(gid))

    elif data.startswith("mn_click_"):
        parts = data.split("_")
        gid, idx = f"mn_{parts[2]}_{parts[3]}", int(parts[4])
        g = mines_games.get(gid)
        if not g or g["game_over"] or idx in g["revealed"]: return

        g["revealed"].append(idx)
        if g["board"][idx] == "🐉":
            g["game_over"] = True
            bot.edit_message_text("💥 *BOOM! Dragon ne pakad liya! Game Over!* 🐉", chat_id=cid, message_id=mid, parse_mode="Markdown", reply_markup=render_mines_board(gid))
        else:
            g["score"] += 15
            bot.edit_message_text(f"💎 *Diamond Mila!* Current Points: `+{g['score']}` pts", chat_id=cid, message_id=mid, parse_mode="Markdown", reply_markup=render_mines_board(gid))

    elif data.startswith("mn_cash_"):
        gid = data.replace("mn_cash_", "")
        g = mines_games.get(gid)
        if not g or g["game_over"]: return
        g["game_over"] = True
        update_score(uid, g["score"])
        bot.edit_message_text(f"💰 *Secured!* Aapne `+{g['score']}` pts collect kiye!", chat_id=cid, message_id=mid, parse_mode="Markdown", reply_markup=render_mines_board(gid))

    # Bingo Game
    elif data == "game_bingo":
        bot.edit_message_text("🎱 *Bingo Multiplayer:*\nGroup me bot ko add karo aur wahan `/bingo` likh kar friend ko challenge karo!", chat_id=cid, message_id=mid, parse_mode="Markdown", reply_markup=get_main_menu())

    elif data.startswith("join_bg_"):
        code = data.replace("join_bg_", "")
        lobby = bingo_waiting_room.get(code)
        if not lobby or lobby["p1_id"] == uid: return

        p1_id, p2_id = lobby["p1_id"], uid
        bingo_games[code] = {
            "player_ids": [p1_id, p2_id],
            "players": {p1_id: {"name": lobby["p1_name"], "board": generate_bingo_board(), "msg_id": None}, p2_id: {"name": call.from_user.first_name, "board": generate_bingo_board(), "msg_id": None}},
            "turn": p1_id, "marked": [], "game_over": False, "winner": None
        }

        try:
            m1 = bot.send_message(p1_id, "🎱 Bingo Match Starting...", reply_markup=render_bingo_board(code, p1_id))
            bingo_games[code]["players"][p1_id]["msg_id"] = m1.message_id
            m2 = bot.send_message(p2_id, "🎱 Bingo Match Starting...", reply_markup=render_bingo_board(code, p2_id))
            bingo_games[code]["players"][p2_id]["msg_id"] = m2.message_id
            update_bingo_dms(code, "🚀 Match Shuru!")
            bot.edit_message_text("🎮 *Match start!* Dono players apne DM me check karein.", chat_id=lobby["group_id"], message_id=mid, parse_mode="Markdown")
        except Exception:
            bot.send_message(lobby["group_id"], "⚠️ Dono players pehle bot ko DM me `/start` karein!")

    elif data.startswith("bg_cut_"):
        parts = data.split("_")
        code, num = f"bg_{parts[2]}_{parts[3]}", int(parts[4])
        g = bingo_games.get(code)
        if not g or g["turn"] != uid or g["game_over"]: return

        g["marked"].append(num)
        p1_id, p2_id = g["player_ids"]
        g["turn"] = p2_id if uid == p1_id else p1_id

        for p in [p1_id, p2_id]:
            bd = g["players"][p]["board"]
            m_idx = [i for i, v in enumerate(bd) if v in g["marked"]]
            if check_bingo_lines(bd, m_idx) >= 5:
                g["game_over"] = True
                g["winner"] = p
                update_score(p, 50)
                break
        update_bingo_dms(code, f"✂️ Number `{num}` cut hua!")

    elif data == "none":
        bot.answer_callback_query(call.id, "")

# --- 12. POLLING RUNNER ---
if __name__ == "__main__":
    print("🚀 7-in-1 Arcade Bot is running smoothly...")
    bot.infinity_polling(skip_pending=True)
    
