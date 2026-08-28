import os
import random
import sqlite3
import telebot
from telebot import types

# ==================== PART 1: CORE SETUP, DATABASE & INTERFACE ==================== #

BOT_TOKEN = os.getenv("BOT_TOKEN", "8963859901:AAGT3dYv2NraTFV69ZBQ8f5jEcqhcuIWcis")
bot = telebot.TeleBot(BOT_TOKEN)

DB_NAME = "games_hub.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            score INTEGER DEFAULT 0,
            games_played INTEGER DEFAULT 0,
            active_game TEXT DEFAULT NULL
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

# --- MAIN MENU UI ---
def get_main_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton("1. 🎯 Guess Game", callback_data="game_guess")
    btn2 = types.InlineKeyboardButton("2. 🧠 Maths & Brain Quiz", callback_data="game_quiz")
    btn3 = types.InlineKeyboardButton("3. 🔤 Word Game", callback_data="game_word")
    btn4 = types.InlineKeyboardButton("4. ❌⭕ Tic Tac Toe", callback_data="game_tictactoe")
    btn5 = types.InlineKeyboardButton("5. 🃏 Memory Game", callback_data="game_memory")
    btn6 = types.InlineKeyboardButton("6. 🎱 Bingo", callback_data="game_bingo")
    btn7 = types.InlineKeyboardButton("7. 💣 Bomb (Mines)", callback_data="game_mines")
    btn_stats = types.InlineKeyboardButton("📊 My Stats & Score", callback_data="view_stats")
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn_stats)
    return markup

@bot.message_handler(commands=['start', 'menu'])
def send_welcome(message):
    add_or_update_user(message.from_user.id, message.from_user.username, message.from_user.first_name)
    welcome_text = (
        f"👋 *Welcome {message.from_user.first_name} to the 7-in-1 Arcade Hub!*\n\n"
        "Niche diye gaye menu se game choose karo:"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=get_main_menu())
    # ==================== PART 2: GUESS GAME ==================== #

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
            {"hint": "🎬 Tumbbad movie ke main rakshas (deity) ka kya naam tha?", "ans": "Hastar", "options": ["Hastar", "Brahmarakshas", "Betaal", "Yaksha"]},
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
        types.InlineKeyboardButton("🏏 2. Sports (Cricket Special)", callback_data="g_cat_sports"),
        types.InlineKeyboardButton("🍥 3. Anime & Cartoons", callback_data="g_cat_anime"),
        types.InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")
    )
    return markup

def get_guess_diff_menu(cat):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🟢 Easy (+10 pts)", callback_data=f"g_diff_{cat}_easy"),
        types.InlineKeyboardButton("🟡 Medium (+20 pts)", callback_data=f"g_diff_{cat}_med"),
        types.InlineKeyboardButton("🔴 Hard (+30 pts)", callback_data=f"g_diff_{cat}_hard"),
        types.InlineKeyboardButton("🔙 Choose Another Category", callback_data="game_guess")
    )
    return markup
    # ==================== PART 3: TIC TAC TOE (AI & 2-PLAYER PVP) ==================== #

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
        callback = f"ttt_move_{game_id}_{i}" if val == " " and not game["game_over"] else "ttt_none"
        buttons.append(types.InlineKeyboardButton(text, callback_data=callback))
    
    markup.add(buttons[0], buttons[1], buttons[2])
    markup.add(buttons[3], buttons[4], buttons[5])
    markup.add(buttons[6], buttons[7], buttons[8])
    
    if game["game_over"]:
        markup.add(
            types.InlineKeyboardButton("🔄 Rematch", callback_data=f"ttt_rematch_{game_id}"),
            types.InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")
        )
    else:
        markup.add(types.InlineKeyboardButton("🚪 Forfeit / Quit", callback_data="main_menu"))
    return markup

def check_ttt_winner(board):
    win_conditions = [
        (0, 1, 2), (3, 4, 5), (6, 7, 8),
        (0, 3, 6), (1, 4, 7), (2, 5, 8),
        (0, 4, 8), (2, 4, 6)
    ]
    for a, b, c in win_conditions:
        if board[a] != " " and board[a] == board[b] == board[c]:
            return board[a]
    if " " not in board:
        return "Draw"
    return None

def get_ai_move(board):
    for i in range(9):
        if board[i] == " ":
            board[i] = "O"
            if check_ttt_winner(board) == "O":
                board[i] = " "
                return i
            board[i] = " "

    for i in range(9):
        if board[i] == " ":
            board[i] = "X"
            if check_ttt_winner(board) == "X":
                board[i] = " "
                return i
            board[i] = " "

    if board[4] == " ":
        return 4
    
    empty_spots = [i for i, val in enumerate(board) if val == " "]
    return random.choice(empty_spots) if empty_spots else None

def get_ttt_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🤖 Play vs AI (Bot)", callback_data="ttt_start_ai"),
        types.InlineKeyboardButton("👥 Play with Friend (2P / Group)", callback_data="ttt_start_pvp"),
        types.InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")
    )
    return markup
        # ==================== PART 4: 5x5 MULTIPLAYER BINGO (GROUP + DM SYNC) ==================== #

bingo_games = {}
bingo_waiting_room = {}

def generate_bingo_board():
    nums = list(range(1, 26))
    random.shuffle(nums)
    return nums

def check_bingo_lines(board, marked_indices):
    lines = 0
    # Rows check
    for r in range(5):
        if all((r * 5 + c) in marked_indices for c in range(5)):
            lines += 1
    # Columns check
    for c in range(5):
        if all((r * 5 + c) in marked_indices for r in range(5)):
            lines += 1
    # Diagonal 1
    if all((i * 6) in marked_indices for i in range(5)):
        lines += 1
    # Diagonal 2
    if all(((i + 1) * 4) in marked_indices for i in range(5)):
        lines += 1
    return min(lines, 5)

def render_bingo_board(game_id, user_id):
    game = bingo_games.get(game_id)
    if not game:
        return None
    
    player_data = game["players"][user_id]
    board = player_data["board"]
    marked = game["marked_numbers"]
    
    markup = types.InlineKeyboardMarkup(row_width=5)
    buttons = []
    
    for idx, num in enumerate(board):
        if num in marked:
            btn_text = "❌"
            callback = "bingo_none"
        else:
            btn_text = str(num)
            callback = f"bg_cut_{game_id}_{num}" if game["turn"] == user_id and not game["game_over"] else "bingo_none"
        buttons.append(types.InlineKeyboardButton(btn_text, callback_data=callback))
    
    for i in range(0, 25, 5):
        markup.add(buttons[i], buttons[i+1], buttons[i+2], buttons[i+3], buttons[i+4])
    
    if game["game_over"]:
        markup.add(types.InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu"))
    else:
        markup.add(types.InlineKeyboardButton("🚪 Leave Game", callback_data="main_menu"))
    return markup

def get_bingo_letters(lines_count):
    letters = ["B", "I", "N", "G", "O"]
    res = []
    for i in range(5):
        if i < lines_count:
            res.append(f"🔥*{letters[i]}*")
        else:
            res.append(f"⚪{letters[i]}")
    return " ".join(res)

def update_bingo_dms(bot_instance, game_id, last_action_text=""):
    game = bingo_games.get(game_id)
    if not game:
        return

    p1_id, p2_id = game["player_ids"]
    turn_id = game["turn"]

    for p_id in [p1_id, p2_id]:
        opp_id = p2_id if p_id == p1_id else p1_id
        p_name = game["players"][p_id]["name"]
        opp_name = game["players"][opp_id]["name"]
        
        my_board = game["players"][p_id]["board"]
        my_marked_indices = [idx for idx, val in enumerate(my_board) if val in game["marked_numbers"]]
        my_lines = check_bingo_lines(my_board, my_marked_indices)
        
        bingo_status = get_bingo_letters(my_lines)
        turn_status = "👉 *Aapki Chaal hai!*" if turn_id == p_id and not game["game_over"] else f"⏳ *{opp_name} ki baari hai...*"

        text = (
            f"🎱 *BINGO 5x5 MATCH*\n"
            f"👤 Player: `{p_name}` vs `{opp_name}`\n"
            f"🎯 Status: {bingo_status} ({my_lines}/5 Lines)\n\n"
            f"{last_action_text}\n"
            f"{turn_status}\n\n"
            f"📌 Grid me se number dabakar strike karo:"
        )

        if game["game_over"]:
            if game["winner"] == "Draw":
                text = f"🤝 *Game Draw ho gaya!*\n\nDono ne ek sath BINGO complete kiya!"
            elif game["winner"] == p_id:
                text = f"🏆 *BINGO!! CONGRATULATIONS {p_name}!* 🎉\nAapne 5 lines bana kar match jeet liya!"
            else:
                text = f"💔 *Match Over!*\n{opp_name} ne pehle BINGO bana liya!"

        try:
            bot_instance.edit_message_text(
                text,
                chat_id=p_id,
                message_id=game["players"][p_id]["msg_id"],
                parse_mode="Markdown",
                reply_markup=render_bingo_board(game_id, p_id)
            )
        except Exception:
            pass

@bot.message_handler(commands=['bingo'])
def start_group_bingo_lobby(message):
    if message.chat.type in ['group', 'supergroup']:
        game_code = f"bg_{message.chat.id}_{message.message_id}"
        bingo_waiting_room[game_code] = {
            "p1_id": message.from_user.id,
            "p1_name": message.from_user.first_name,
            "group_id": message.chat.id
        }
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🎮 Join Bingo Challenge", callback_data=f"join_bg_{game_code}"))
        
        bot.reply_to(
            message,
            f"🎱 *BINGO 5x5 CHALLENGE!*\n\n"
            f"👤 Host: *{message.from_user.first_name}*\n"
            f"Koi bhi friend niche button daba kar join kare!",
            parse_mode="Markdown",
            reply_markup=markup
        )
    else:
        bot.reply_to(message, "Ye command group me use karo dosto ke sath khelne ke liye!")
        # ==================== PART 5: MATHS & BRAIN QUIZ ==================== #

QUIZ_DATA = {
    "maths": [
        {
            "q": "🔢 If log₂(x) + log₂(x - 2) = 3, find the real value of x:",
            "options": ["4", "2", "-2", "8"],
            "ans": "4",
            "exp": "log₂(x(x - 2)) = 3 ⟹ x² - 2x = 8 ⟹ x² - 2x - 8 = 0 ⟹ (x-4)(x+2)=0. Since x > 2, x = 4."
        },
        {
            "q": "🔢 For what value of k does the equation x² - (k - 2)x + (k² - 4) = 0 have equal roots?",
            "options": ["k = 2, -6/3", "k = -2, 10/3", "k = 2, -2", "k = 0, 4"],
            "ans": "k = -2, 10/3",
            "exp": "Discriminant D = 0 ⟹ (k - 2)² - 4(k² - 4) = 0 ⟹ -3k² - 4k + 20 = 0 ⟹ (3k - 10)(k + 2) = 0."
        },
        {
            "q": "🔢 Find the value of: sin²(10°) + sin²(20°) + ... + sin²(80°) + sin²(90°)",
            "options": ["5", "4.5", "5.5", "4"],
            "ans": "5",
            "exp": "Pairs: (sin²10+sin²80)=1, (sin²20+sin²70)=1, (sin²30+sin²60)=1, (sin²40+sin²50)=1, sin²90=1. Total = 1*4 + 1 = 5."
        },
        {
            "q": "🔢 If the 3rd term of a G.P. is 4, what is the product of its first 5 terms?",
            "options": ["4⁵ = 1024", "4³ = 64", "4⁴ = 256", "512"],
            "ans": "4⁵ = 1024",
            "exp": "Terms: a/r², a/r, a, ar, ar². Product = a⁵. Given a = 4, so Product = 4⁵ = 1024."
        },
        {
            "q": "🔢 How many distinct 4-digit numbers can be formed using {0, 1, 2, 3, 4, 5} without repetition?",
            "options": ["300", "360", "240", "120"],
            "ans": "300",
            "exp": "First digit (non-zero): 5 choices. Remaining 3 digits: 5 × 4 × 3 = 60 choices. Total = 5 × 60 = 300."
        },
        {
            "q": "🔢 What is the limit: lim(x→0) [sin(5x) / tan(2x)] ?",
            "options": ["5/2", "2/5", "1", "0"],
            "ans": "5/2",
            "exp": "[sin(5x)/(5x)] * [(2x)/tan(2x)] * (5/2) = 1 * 1 * (5/2) = 5/2."
        },
        {
            "q": "🔢 If Set A has 4 elements, what is the number of non-empty proper subsets of A?",
            "options": ["14", "15", "16", "13"],
            "ans": "14",
            "exp": "Total subsets = 2⁴ = 16. Subtract empty set (1) and self (1) ⟹ 16 - 2 = 14."
        },
        {
            "q": "🔢 The sum of roots of 3x² - kx + 6 = 0 is 4. Find the value of k.",
            "options": ["12", "6", "-12", "4"],
            "ans": "12",
            "exp": "Sum of roots = -(-k)/3 = k/3 = 4 ⟹ k = 12."
        }
    ],
    "brain": [
        {
            "q": "🧠 Complete the series: 2, 6, 12, 20, 30, 42, ?",
            "options": ["56", "54", "60", "52"],
            "ans": "56",
            "exp": "Pattern: 1×2, 2×3, 3×4, 4×5, 5×6, 6×7, 7×8 = 56."
        },
        {
            "q": "🧠 A doctor gives you 3 pills and tells you to take one every 30 minutes. How long will the pills last?",
            "options": ["60 minutes", "90 minutes", "30 minutes", "120 minutes"],
            "ans": "60 minutes",
            "exp": "Pill 1 at 0 min, Pill 2 at 30 min, Pill 3 at 60 min. Total duration = 60 minutes."
        },
        {
            "q": "🧠 Look at this pattern: 8 + 2 = 16106, 5 + 4 = 2091, 9 + 6 = 54153. What is 7 + 3 = ?",
            "options": ["21104", "21103", "10214", "2174"],
            "ans": "21104",
            "exp": "Structure: (a×b)(a+b)(a-b) ⟹ 7×3=21, 7+3=10, 7-3=4 ⟹ 21104."
        },
        {
            "q": "🧠 If 5 cats can catch 5 mice in 5 minutes, how many cats are needed to catch 100 mice in 100 minutes?",
            "options": ["5", "100", "20", "50"],
            "ans": "5",
            "exp": "1 cat catches 1 mouse in 5 minutes. So in 100 minutes, 1 cat catches 20 mice. 5 cats will catch 100 mice."
        },
        {
            "q": "🧠 Pointing to a photograph, a man said: 'I have no brother or sister, but that man's father is my father's son.' Who was in the photo?",
            "options": ["His Son", "His Father", "Himself", "His Grandson"],
            "ans": "His Son",
            "exp": "'My father's son' with no siblings = Himself. So 'that man's father is himself' ⟹ Photo is of his son."
        },
        {
            "q": "🧠 In a code, CRICKET is written as FULFNHW. How is MATCH written in that code?",
            "options": ["PDWFK", "PDVFK", "OCWFK", "PDWEL"],
            "ans": "PDWFK",
            "exp": "Each letter shifted +3 positions: M+3=P, A+3=D, T+3=W, C+3=F, H+3=K."
        }
    ]
}

active_quiz_sessions = {}

def get_quiz_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("📐 1. Class 10/11 Hard Maths", callback_data="qz_start_maths"),
        types.InlineKeyboardButton("🧩 2. Logical Brain Riddles & Patterns", callback_data="qz_start_brain"),
        types.InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")
    )
    return markup
# ==================== PART 6: WORD GAMES (GUESS, SCRAMBLE & PVP CHAIN DUEL) ==================== #

WORD_DATABASE = [
    {"word": "PYTHON", "hint": "A popular high-level programming language"},
    {"word": "GALAXY", "hint": "A huge collection of gas, dust, and billions of stars"},
    {"word": "CRICKET", "hint": "A sport played with bat, ball, and wickets"},
    {"word": "OXYGEN", "hint": "A vital gas necessary for human respiration"},
    {"word": "ALGORITHM", "hint": "A step-by-step procedure for solving a problem"},
    {"word": "SHADOW", "hint": "Dark area produced when an object blocks light"},
    {"word": "MATRIX", "hint": "A rectangular array of numbers arranged in rows and columns"},
    {"word": "VECTOR", "hint": "A quantity having both magnitude and direction"},
    {"word": "PRISM", "hint": "A transparent glass that disperses light into spectrum"},
    {"word": "GRAVITY", "hint": "The force that attracts a body toward the center of the earth"}
]

# Sessions storage
active_word_guess = {}
active_scramble = {}
active_chain_duels = {}

def get_word_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🔍 1. Guess Word (Clue Quiz)", callback_data="wrd_mode_guess"),
        types.InlineKeyboardButton("🔀 2. Scramble Unjumble", callback_data="wrd_mode_scramble"),
        types.InlineKeyboardButton("⚔️ 3. Word Chain Duel (PvP Battle)", callback_data="wrd_mode_duel_info"),
        types.InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")
    )
    return markup

def start_guess_word_session(user_id):
    item = random.choice(WORD_DATABASE)
    word = item["word"]
    hint = item["hint"]
    masked = " ".join(["_" for _ in word])
    
    # Store session
    active_word_guess[user_id] = {
        "word": word,
        "hint": hint,
        "revealed": set(),
        "attempts_left": 5
    }
    return word, hint, masked

def start_scramble_session(user_id):
    item = random.choice(WORD_DATABASE)
    word = item["word"]
    scrambled = list(word)
    while "".join(scrambled) == word:
        random.shuffle(scrambled)
    
    scrambled_str = " ".join(scrambled)
    active_scramble[user_id] = {
        "word": word,
        "hint": item["hint"]
    }
    return word, scrambled_str, item["hint"]

# PvP Word Chain Duel Initializer
def init_word_chain_duel(game_id, p1_id, p1_name, p2_id, p2_name, chat_id):
    active_chain_duels[game_id] = {
        "chat_id": chat_id,
        "p1_id": p1_id,
        "p1_name": p1_name,
        "p2_id": p2_id,
        "p2_name": p2_name,
        "turn": p1_id,
        "round": 1,
        "min_length": 2,
        "time_limit": 40,
        "used_words": set(),
        "last_char": random.choice("ABCDEFGHIJKLMNOPRSTW"),
        "game_over": False
    }
    return active_chain_duels[game_id]
    # ==================== PART 7: MEMORY GAME (4x4 MULTIPLAYER CARD FLIP) ==================== #

MEMORY_EMOJIS = ["🦁", "👑", "⚡", "🍕", "🚀", "💎", "🔥", "⚽"]
memory_games = {}

def create_memory_board():
    cards = MEMORY_EMOJIS * 2
    random.shuffle(cards)
    return cards

def render_memory_grid(game_id):
    game = memory_games.get(game_id)
    if not game:
        return None
    
    cards = game["cards"]
    revealed = game["revealed"]
    matched = game["matched"]
    
    markup = types.InlineKeyboardMarkup(row_width=4)
    buttons = []
    
    for i in range(16):
        if i in matched or i in revealed:
            btn_text = cards[i]
            cb_data = "mem_none"
        else:
            btn_text = "❓"
            cb_data = f"mem_flip_{game_id}_{i}" if not game["game_over"] and not game["locked"] else "mem_none"
        
        buttons.append(types.InlineKeyboardButton(btn_text, callback_data=cb_data))
    
    for row in range(0, 16, 4):
        markup.add(buttons[row], buttons[row+1], buttons[row+2], buttons[row+3])
        
    if game["game_over"]:
        markup.add(types.InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu"))
    else:
        markup.add(types.InlineKeyboardButton("🚪 Forfeit Game", callback_data="main_menu"))
        
    return markup

def get_memory_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🤖 Play Single Player (Practice)", callback_data="mem_start_solo"),
        types.InlineKeyboardButton("👥 Play with Friend (Group Duel)", callback_data="mem_start_pvp_info"),
        types.InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")
    )
    return markup
    # ==================== PART 8: MINES & DRAGON (GROUP PVP SURVIVAL) ==================== #

mines_games = {}

def create_mines_board():
    # 5 Dragons (Bombs) aur 20 Diamonds (Gems)
    board = ["🐉"] * 5 + ["💎"] * 20
    random.shuffle(board)
    return board

def render_mines_board(game_id):
    game = mines_games.get(game_id)
    if not game:
        return None
    
    board = game["board"]
    revealed = game["revealed"]
    
    markup = types.InlineKeyboardMarkup(row_width=5)
    buttons = []
    
    for i in range(25):
        if i in revealed:
            btn_text = board[i]
            cb_data = "mine_none"
        else:
            btn_text = "❓"
            # Agar game over nahi hai tabhi click ho sakta hai
            cb_data = f"mine_click_{game_id}_{i}" if not game["game_over"] else "mine_none"
            
        buttons.append(types.InlineKeyboardButton(btn_text, callback_data=cb_data))
    
    # 5x5 Grid setup
    for row in range(0, 25, 5):
        markup.add(buttons[row], buttons[row+1], buttons[row+2], buttons[row+3], buttons[row+4])
        
    if game["game_over"]:
        markup.add(
            types.InlineKeyboardButton("🔄 Play Again", callback_data=f"mine_rematch_{game_id}"),
            types.InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")
        )
    else:
        markup.add(types.InlineKeyboardButton("🚪 Surrender & Quit", callback_data="main_menu"))
        
    return markup

def get_mines_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("💰 Play Solo (Multiplier Mode)", callback_data="mine_start_solo"),
        types.InlineKeyboardButton("⚔️ Play with Friend (Survival Duel)", callback_data="mine_start_pvp_info"),
        types.InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")
    )
    return markup
    # ==================== PART 9: MASTER CALLBACK HANDLER & RUNNER ==================== #

@bot.callback_query_handler(func=lambda call: True)
def handle_all_callbacks(call):
    user_id = call.from_user.id
    data = call.data
    chat_id = call.message.chat.id
    msg_id = call.message.message_id

    # --- 1. MAIN MENU & STATS ---
    if data == "main_menu":
        bot.edit_message_text(
            "🎮 *Main Game Menu:*\nApna game choose karo aur khelna shuru karo:",
            chat_id=chat_id,
            message_id=msg_id,
            parse_mode="Markdown",
            reply_markup=get_main_menu()
        )

    elif data == "view_stats":
        score, played = get_user_stats(user_id)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu"))
        bot.edit_message_text(
            f"📊 *Player Profile*\n\n"
            f"👤 Name: {call.from_user.first_name}\n"
            f"🏆 Total Score: `{score}` pts\n"
            f"🎮 Games Played: `{played}`",
            chat_id=chat_id,
            message_id=msg_id,
            parse_mode="Markdown",
            reply_markup=markup
        )

    # --- 2. GAME 1: GUESS GAME ---
    elif data == "game_guess":
        bot.edit_message_text(
            "🎯 *GUESS GAME*\n\nApni category choose karo:",
            chat_id=chat_id,
            message_id=msg_id,
            parse_mode="Markdown",
            reply_markup=get_guess_category_menu()
        )

    elif data.startswith("g_cat_"):
        cat = data.split("_")[2]
        bot.edit_message_text(
            f"🎯 *Selected:* `{cat.capitalize()}`\nAb difficulty level chun lo:",
            chat_id=chat_id,
            message_id=msg_id,
            parse_mode="Markdown",
            reply_markup=get_guess_diff_menu(cat)
        )

    elif data.startswith("g_diff_"):
        parts = data.split("_")
        cat, diff = parts[2], parts[3]
        pool = QUESTIONS_DATA[cat][diff]
        q_data = random.choice(pool)
        
        active_guess_sessions[user_id] = {
            "cat": cat,
            "diff": diff,
            "ans": q_data["ans"],
            "pts": 10 if diff == "easy" else (20 if diff == "med" else 30)
        }

        options = list(q_data["options"])
        random.shuffle(options)
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn_list = [types.InlineKeyboardButton(opt, callback_data=f"g_ans_{opt}") for opt in options]
        markup.add(*btn_list)
        markup.add(types.InlineKeyboardButton("🔙 Exit", callback_data="game_guess"))

        text = f"🎯 *GUESS GAME* [{cat.upper()} - {diff.upper()}]\n\n❓ {q_data['hint']}\n\n👉 Sahi answer select karo:"
        bot.edit_message_text(text, chat_id=chat_id, message_id=msg_id, parse_mode="Markdown", reply_markup=markup)

    elif data.startswith("g_ans_"):
        selected_ans = data.replace("g_ans_", "")
        session = active_guess_sessions.get(user_id)
        if not session:
            bot.answer_callback_query(call.id, "Session expire ho gaya!")
            return

        correct_ans = session["ans"]
        pts, cat, diff = session["pts"], session["cat"], session["diff"]

        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("🔁 Next Question", callback_data=f"g_diff_{cat}_{diff}"),
            types.InlineKeyboardButton("📂 Change Category", callback_data="game_guess"),
            types.InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")
        )

        if selected_ans == correct_ans:
            update_score(user_id, pts)
            res_text = f"🎉 *SHABASH! Sahi Jawab!* ✅\n\nAnswer: *{correct_ans}*\nScore: `+{pts} pts` 🏆"
        else:
            res_text = f"❌ *Galat Jawab!*\n\nTumne chuna: `{selected_ans}`\nSahi Jawab: *{correct_ans}*"

        bot.edit_message_text(res_text, chat_id=chat_id, message_id=msg_id, parse_mode="Markdown", reply_markup=markup)

    # --- 3. GAME 2: MATHS & BRAIN QUIZ ---
    elif data == "game_quiz":
        bot.edit_message_text(
            "🧠 *MATHS & BRAIN QUIZ*\n\nApna mode chun lo:",
            chat_id=chat_id,
            message_id=msg_id,
            parse_mode="Markdown",
            reply_markup=get_quiz_menu()
        )

    elif data.startswith("qz_start_"):
        mode = data.replace("qz_start_", "")
        q_item = random.choice(QUIZ_DATA[mode])
        
        active_quiz_sessions[user_id] = {
            "mode": mode,
            "ans": q_item["ans"],
            "exp": q_item["exp"]
        }

        opts = list(q_item["options"])
        random.shuffle(opts)
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn_list = [types.InlineKeyboardButton(o, callback_data=f"qz_ans_{o}") for o in opts]
        markup.add(*btn_list)
        markup.add(types.InlineKeyboardButton("🔙 Exit Quiz", callback_data="game_quiz"))

        bot.edit_message_text(
            f"{q_item['q']}\n\n👉 Sahi option choose karo:",
            chat_id=chat_id,
            message_id=msg_id,
            parse_mode="Markdown",
            reply_markup=markup
        )

    elif data.startswith("qz_ans_"):
        selected_ans = data.replace("qz_ans_", "")
        session = active_quiz_sessions.get(user_id)
        if not session:
            bot.answer_callback_query(call.id, "Session expire ho gaya!")
            return

        correct = session["ans"]
        exp = session["exp"]
        mode = session["mode"]

        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("🔁 Next Question", callback_data=f"qz_start_{mode}"),
            types.InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")
        )

        if selected_ans == correct:
            update_score(user_id, 25)
            res_text = f"🎉 *PERFECT! Sahi Jawab!* ✅\n\n💡 *Solution:*\n{exp}\n\nPoints: `+25 pts` 🏆"
        else:
            res_text = f"❌ *Galat Answer!*\n\nSahi Answer: *{correct}*\n\n💡 *Explanation:*\n{exp}"

        bot.edit_message_text(res_text, chat_id=chat_id, message_id=msg_id, parse_mode="Markdown", reply_markup=markup)

    # --- 4. GAME 3: WORD GAME ---
    elif data == "game_word":
        bot.edit_message_text(
            "🔤 *WORD GAME ARENA*\n\nMode select karo:",
            chat_id=chat_id,
            message_id=msg_id,
            parse_mode="Markdown",
            reply_markup=get_word_menu()
        )

    elif data == "wrd_mode_scramble":
        word, scrambled, hint = start_scramble_session(user_id)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("👀 Reveal Answer", callback_data=f"wrd_rev_{word}"))
        markup.add(types.InlineKeyboardButton("🔁 Next Word", callback_data="wrd_mode_scramble"))
        markup.add(types.InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu"))

        bot.edit_message_text(
            f"🔀 *WORD SCRAMBLE*\n\n"
            f"Is word ko unjumble karo:\n\n"
            f"🔤 *`{scrambled}`*\n"
            f"💡 Clue: _{hint}_",
            chat_id=chat_id,
            message_id=msg_id,
            parse_mode="Markdown",
            reply_markup=markup
        )

    elif data.startswith("wrd_rev_"):
        word = data.replace("wrd_rev_", "")
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔁 Next Word", callback_data="wrd_mode_scramble"))
        markup.add(types.InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu"))
        bot.edit_message_text(f"💡 Sahi word tha: *{word}*", chat_id=chat_id, message_id=msg_id, parse_mode="Markdown", reply_markup=markup)

    elif data in ["wrd_mode_guess", "wrd_mode_duel_info"]:
        bot.answer_callback_query(call.id, "Group chat me /word duel try karein!")

    # --- 5. GAME 4: TIC TAC TOE ---
    elif data == "game_tictactoe":
        bot.edit_message_text(
            "❌⭕ *TIC TAC TOE*\n\nMode select karo:",
            chat_id=chat_id,
            message_id=msg_id,
            parse_mode="Markdown",
            reply_markup=get_ttt_menu()
        )

    elif data == "ttt_start_ai":
        game_id = f"ttt_{user_id}_{random.randint(1000, 9999)}"
        ttt_games[game_id] = {
            "p1_id": user_id,
            "board": [" "] * 9,
            "turn": "X",
            "game_over": False
        }
        bot.edit_message_text(
            "❌⭕ *Tic Tac Toe vs AI (Bot)*\n\nAap: ❌ | Bot: ⭕\nAapki pehli chaal hai:",
            chat_id=chat_id,
            message_id=msg_id,
            parse_mode="Markdown",
            reply_markup=create_ttt_board(game_id)
        )

    elif data.startswith("ttt_move_"):
        parts = data.split("_")
        game_id = f"{parts[2]}_{parts[3]}_{parts[4]}"
        move_idx = int(parts[5])
        game = ttt_games.get(game_id)

        if not game or game["game_over"]:
            return

        # Player Move (X)
        game["board"][move_idx] = "X"
        winner = check_ttt_winner(game["board"])

        if winner:
            game["game_over"] = True
            text = "🎉 *Aap Jeet Gaye!* 🏆 (+15 pts)" if winner == "X" else "🤝 *Game Draw ho gaya!*"
            if winner == "X":
                update_score(user_id, 15)
        else:
            # Bot Move (O)
            ai_idx = get_ai_move(game["board"])
            if ai_idx is not None:
                game["board"][ai_idx] = "O"
                winner = check_ttt_winner(game["board"])
                if winner:
                    game["game_over"] = True
                    text = "🤖 *Bot Jeet Gaya!* Agli baar try karo!" if winner == "O" else "🤝 *Game Draw ho gaya!*"
                else:
                    text = "❌⭕ *Aapki Chaal hai (❌):*"
            else:
                game["game_over"] = True
                text = "🤝 *Game Draw ho gaya!*"

        bot.edit_message_text(text, chat_id=chat_id, message_id=msg_id, parse_mode="Markdown", reply_markup=create_ttt_board(game_id))

    # --- 6. GAME 5: MEMORY GAME ---
    elif data == "game_memory":
        bot.edit_message_text(
            "🃏 *MEMORY GAME*\n\nApna mode chun lo:",
            chat_id=chat_id,
            message_id=msg_id,
            parse_mode="Markdown",
            reply_markup=get_memory_menu()
        )

    elif data == "mem_start_solo":
        game_id = f"mem_{user_id}_{random.randint(1000, 9999)}"
        memory_games[game_id] = {
            "cards": create_memory_board(),
            "revealed": [],
            "matched": [],
            "game_over": False,
            "locked": False
        }
        bot.edit_message_text(
            "🃏 *Memory Challenge (Solo)*\n\nMatching emoji pairs dhoondo (Total 8 pairs):",
            chat_id=chat_id,
            message_id=msg_id,
            parse_mode="Markdown",
            reply_markup=render_memory_grid(game_id)
        )

    elif data.startswith("mem_flip_"):
        parts = data.split("_")
        game_id = f"{parts[2]}_{parts[3]}_{parts[4]}"
        card_idx = int(parts[5])
        game = memory_games.get(game_id)

        if not game or card_idx in game["revealed"] or card_idx in game["matched"]:
            return

        game["revealed"].append(card_idx)

        if len(game["revealed"]) == 2:
            idx1, idx2 = game["revealed"]
            if game["cards"][idx1] == game["cards"][idx2]:
                game["matched"].extend([idx1, idx2])
                game["revealed"] = []
                if len(game["matched"]) == 16:
                    game["game_over"] = True
                    update_score(user_id, 30)
                    bot.edit_message_text(
                        "🎉 *CONGRATULATIONS!* 🏆\nSare 8 pairs match kar diye! (+30 pts)",
                        chat_id=chat_id,
                        message_id=msg_id,
                        parse_mode="Markdown",
                        reply_markup=render_memory_grid(game_id)
                    )
                    return
            else:
                bot.edit_message_text(
                    "❌ Match nahi hua! Dobara dhyan se dekho:",
                    chat_id=chat_id,
                    message_id=msg_id,
                    reply_markup=render_memory_grid(game_id)
                )
                game["revealed"] = []
                return

        bot.edit_message_text(
            "🃏 Matching pairs dhoondo:",
            chat_id=chat_id,
            message_id=msg_id,
            reply_markup=render_memory_grid(game_id)
        )

    # --- 7. GAME 6: BINGO MULTIPLAYER LOBBY ---
    elif data == "game_bingo":
        bot.edit_message_text(
            "🎱 *BINGO 5x5 MULTIPLAYER*\n\n"
            "Dosto ke saath khelne ke liye bot ko kisi group me add karo aur wahan `/bingo` likho!",
            chat_id=chat_id,
            message_id=msg_id,
            parse_mode="Markdown",
            reply_markup=get_main_menu()
        )

    elif data.startswith("join_bg_"):
        game_code = data.replace("join_bg_", "")
        lobby = bingo_waiting_room.get(game_code)
        if not lobby:
            bot.answer_callback_query(call.id, "Game lobby expired!")
            return
        if lobby["p1_id"] == user_id:
            bot.answer_callback_query(call.id, "Host khud ke match ko join nahi kar sakta!", show_alert=True)
            return

        # Initialize Bingo Match
        p1_id, p2_id = lobby["p1_id"], user_id
        p1_name, p2_name = lobby["p1_name"], call.from_user.first_name
        
        bingo_games[game_code] = {
            "player_ids": [p1_id, p2_id],
            "players": {
                p1_id: {"name": p1_name, "board": generate_bingo_board(), "msg_id": None},
                p2_id: {"name": p2_name, "board": generate_bingo_board(), "msg_id": None}
            },
            "turn": p1_id,
            "marked_numbers": [],
            "game_over": False,
            "winner": None
        }

        # Send DM Boards
        try:
            m1 = bot.send_message(p1_id, "🎱 Bingo match shuru ho raha hai...", reply_markup=render_bingo_board(game_code, p1_id))
            bingo_games[game_code]["players"][p1_id]["msg_id"] = m1.message_id
            m2 = bot.send_message(p2_id, "🎱 Bingo match shuru ho raha hai...", reply_markup=render_bingo_board(game_code, p2_id))
            bingo_games[game_code]["players"][p2_id]["msg_id"] = m2.message_id
            
            update_bingo_dms(bot, game_code, f"🚀 Match Shuru! {p1_name} vs {p2_name}")
            bot.edit_message_text(f"🎮 Bingo match shuru ho gaya! Dono players ({p1_name} & {p2_name}) apne DM me check karein.", chat_id=lobby["group_id"], message_id=msg_id)
        except Exception:
            bot.send_message(lobby["group_id"], "⚠️ Dono players pehle bot ke DM me `/start` karein taaki board bheja ja sake!")

    elif data.startswith("bg_cut_"):
        parts = data.split("_")
        game_code = f"bg_{parts[2]}_{parts[3]}"
        num = int(parts[4])
        game = bingo_games.get(game_code)

        if not game or game["turn"] != user_id or game["game_over"]:
            return

        game["marked_numbers"].append(num)
        p1_id, p2_id = game["player_ids"]
        next_turn = p2_id if user_id == p1_id else p1_id
        game["turn"] = next_turn

        # Check Winner
        for p_id in [p1_id, p2_id]:
            board = game["players"][p_id]["board"]
            marked_idx = [idx for idx, val in enumerate(board) if val in game["marked_numbers"]]
            if check_bingo_lines(board, marked_idx) >= 5:
                game["game_over"] = True
                game["winner"] = p_id
                update_score(p_id, 50)
                break

        caller_name = game["players"][user_id]["name"]
        update_bingo_dms(bot, game_code, f"✂️ *{caller_name} ne number `{num}` cut kiya!*")

    # --- 8. GAME 7: MINES & DRAGON ---
    elif data == "game_mines":
        bot.edit_message_text(
            "💣 *MINES & DRAGONS*\n\nMode select karo:",
            chat_id=chat_id,
            message_id=msg_id,
            parse_mode="Markdown",
            reply_markup=get_mines_menu()
        )

    elif data == "mine_start_solo":
        game_id = f"mn_{user_id}_{random.randint(1000, 9999)}"
        mines_games[game_id] = {
            "board": create_mines_board(),
            "revealed": [],
            "score": 0,
            "game_over": False
        }
        bot.edit_message_text(
            "💣 *Mines Survival (Solo)*\n\nDiamond 💎 dhoondo, Dragon 🐉 se bacho (Total 5 Dragons chhupe hain):",
            chat_id=chat_id,
            message_id=msg_id,
            parse_mode="Markdown",
            reply_markup=render_mines_board(game_id)
        )

    elif data.startswith("mine_click_"):
        parts = data.split("_")
        game_id = f"{parts[2]}_{parts[3]}_{parts[4]}"
        cell_idx = int(parts[5])
        game = mines_games.get(game_id)

        if not game or game["game_over"] or cell_idx in game["revealed"]:
            return

        game["revealed"].append(cell_idx)
        val = game["board"][cell_idx]

        if val == "🐉":
            game["game_over"] = True
            text = "💥 *BOOM! Dragon/Bomb aa gaya!* Game Over! 🐉🔥"
        else:
            game["score"] += 10
            update_score(user_id, 10)
            text = f"✨ *Diamond Mila!* 💎 Points: `{game['score']} pts`\nAgla box choose karo ya menu se quit karo:"

        bot.edit_message_text(text, chat_id=chat_id, message_id=msg_id, parse_mode="Markdown", reply_markup=render_mines_board(game_id))

    elif data.endswith("_none"):
        bot.answer_callback_query(call.id, "")

# --- BOT POLLING START ---
if __name__ == "__main__":
    print("🚀 7-in-1 Arcade Bot is running smoothly...")
    bot.infinity_polling(skip_pending=True)
        
