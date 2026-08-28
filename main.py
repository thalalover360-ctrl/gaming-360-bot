import random
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "8963859901:AAGT3dYv2NraTFV69ZBQ8f5jEcqhcuIWcis"
bot = telebot.TeleBot(TOKEN)

games = {}
ttt_games = {}

MATH_OPS = ['+', '-', '*']
MIND_PUZZLES = [
    {"q": "Aisi kaun si cheez hai jo sookhte waqt geeli ho jati hai?", "a": "Towel", "opts": ["Towel", "Soap", "Paper", "Cloth"]},
    {"q": "Kiske paas gale hote hain par sar nahi?", "a": "Shirt", "opts": ["Shirt", "Bottle", "Tree", "Snake"]},
    {"q": "Agar 3 seb hain aur tumne 2 le liye, toh tumhare paas kitne seb hain?", "a": "2", "opts": ["2", "1", "3", "0"]},
    {"q": "Wo kya hai jise aap todte ho bina touch kiye?", "a": "Promise", "opts": ["Promise", "Glass", "Heart", "Trust"]}
]

GEN_QUIZ = [
    {"q": "FIFA World Cup kitne saal me ek baar hota hai?", "opts": ["4 saal", "2 saal", "5 saal", "3 saal"], "ans": "4 saal"},
    {"q": "Duniya ka sabse bada ocean kaun sa hai?", "opts": ["Pacific Ocean", "Indian Ocean", "Atlantic Ocean", "Arctic Ocean"], "ans": "Pacific Ocean"},
    {"q": "Cricket match me pitch ki length kitni hoti hai?", "opts": ["22 Yards", "20 Yards", "24 Yards", "18 Yards"], "ans": "22 Yards"}
]

@bot.message_handler(commands=['start', 'games', 'menu'])
def show_menu(message):
    chat_id = message.chat.id
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("❌ Tic Tac Toe ⭕", callback_data="menu_ttt"),
        InlineKeyboardButton("🎲 Bingo (5x5)", callback_data="menu_bingo"),
        InlineKeyboardButton("⚡ Maths Battle", callback_data="menu_math"),
        InlineKeyboardButton("🧠 Mind Sharp", callback_data="menu_mind"),
        InlineKeyboardButton("🎯 General Quiz", callback_data="menu_quiz")
    )
    bot.send_message(chat_id, "🎮 **Gaming 360 Hub!** 🎮\n\nGame chuno:", reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith('menu_'))
def handle_menu_selection(call):
    chat_id = call.message.chat.id
    game_type = call.data.split('_')[1]
    
    if game_type == "ttt":
        start_ttt_lobby(chat_id)
    elif game_type == "bingo":
        start_bingo_lobby(chat_id)
    elif game_type == "math":
        start_math_quiz(chat_id)
    elif game_type == "mind":
        start_mind_puzzle(chat_id)
    elif game_type == "quiz":
        start_general_quiz(chat_id)

def get_ttt_markup(chat_id):
    g = ttt_games[chat_id]
    markup = InlineKeyboardMarkup(row_width=3)
    buttons = []
    for i in range(9):
        val = g['board'][i] if g['board'][i] != " " else "▫️"
        buttons.append(InlineKeyboardButton(val, callback_data=f"ttt_move_{chat_id}_{i}"))
    markup.add(*buttons)
    return markup

def check_ttt_winner(b):
    wins = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]
    for x, y, z in wins:
        if b[x] == b[y] == b[z] and b[x] != " ":
            return b[x]
    if " " not in b:
        return "Tie"
    return None

def start_ttt_lobby(chat_id):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🎮 Join Tic Tac Toe", callback_data=f"ttt_join_{chat_id}"))
    bot.send_message(chat_id, "❌⭕ **Tic Tac Toe 1v1 Battle!**\nPehle doosra dost 'Join' dabaye.", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('ttt_join_'))
def join_ttt(call):
    chat_id = int(call.data.split('_')[2])
    user = call.from_user
    if chat_id not in ttt_games:
        ttt_games[chat_id] = {'p1': user, 'p2': None, 'board': [" "]*9, 'turn': 'X'}
        bot.send_message(chat_id, f"✅ **{user.first_name}** (X) ready hai! Koi aur Join dabaye.")
    elif ttt_games[chat_id]['p2'] is None and ttt_games[chat_id]['p1'].id != user.id:
        ttt_games[chat_id]['p2'] = user
        p1_name = ttt_games[chat_id]['p1'].first_name
        bot.send_message(chat_id, f"🔥 Game Start!\n❌: {p1_name}\n⭕: {user.first_name}\nBaari: {p1_name}", reply_markup=get_ttt_markup(chat_id))

@bot.callback_query_handler(func=lambda call: call.data.startswith('ttt_move_'))
def handle_ttt_move(call):
    _, _, chat_id, idx = call.data.split('_')
    chat_id, idx = int(chat_id), int(idx)
    g = ttt_games.get(chat_id)
    if not g or not g['p2']:
        return

    curr_player = g['p1'] if g['turn'] == 'X' else g['p2']
    if call.from_user.id != curr_player.id:
        bot.answer_callback_query(call.id, "Aapki baari nahi hai!")
        return

    if g['board'][idx] != " ":
        bot.answer_callback_query(call.id, "Slot bhara hua hai!")
        return

    g['board'][idx] = g['turn']
    winner = check_ttt_winner(g['board'])
    if winner:
        if winner == "Tie":
            bot.edit_message_text("🤝 Match Draw!", chat_id=chat_id, message_id=call.message.message_id, reply_markup=get_ttt_markup(chat_id))
        else:
            w_name = g['p1'].first_name if winner == 'X' else g['p2'].first_name
            bot.edit_message_text(f"🏆 **{w_name} Jeet Gaya! ({winner})**", chat_id=chat_id, message_id=call.message.message_id, reply_markup=get_ttt_markup(chat_id))
        del ttt_games[chat_id]
        return

    g['turn'] = 'O' if g['turn'] == 'X' else 'X'
    next_p = g['p1'].first_name if g['turn'] == 'X' else g['p2'].first_name
    bot.edit_message_text(f"Turn: **{next_p}** ({g['turn']})", chat_id=chat_id, message_id=call.message.message_id, reply_markup=get_ttt_markup(chat_id))

def generate_bingo_board():
    nums = list(range(1, 26))
    random.shuffle(nums)
    return [nums[i:i+5] for i in range(0, 25, 5)]

def check_bingo_lines(marked):
    lines = sum(1 for r in range(5) if all(marked[r][c] for c in range(5)))
    lines += sum(1 for c in range(5) if all(marked[r][c] for c in range(5)))
    if all(marked[i][i] for i in range(5)): lines += 1
    if all(marked[i][4 - i] for i in range(5)): lines += 1
    return lines

def format_bingo(board, marked):
    return "\n".join(" | ".join("❌" if marked[r][c] else f"{board[r][c]:02d}" for c in range(5)) for r in range(5))

def start_bingo_lobby(chat_id):
    games[chat_id] = {'players': {}, 'state': 'lobby', 'called': set(), 'turn_order': [], 'turn_idx': 0}
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🎮 Join", callback_data=f"b_join_{chat_id}"), InlineKeyboardButton("🚀 Start", callback_data=f"b_start_{chat_id}"))
    bot.send_message(chat_id, "🎲 **Bingo Lobby Active!**\nJoin dabayein fir Start karein.", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('b_join_'))
def join_bingo(call):
    chat_id = int(call.data.split('_')[2])
    u = call.from_user
    g = games.get(chat_id)
    if not g or g['state'] != 'lobby': return
    if u.id not in g['players']:
        g['players'][u.id] = {'name': u.first_name, 'board': generate_bingo_board(), 'marked': [[False]*5 for _ in range(5)]}
        bot.send_message(chat_id, f"✅ **{u.first_name}** Bingo me add ho gaya!")
    bot.answer_callback_query(call.id, "Done!")

@bot.callback_query_handler(func=lambda call: call.data.startswith('b_start_'))
def start_bingo_game(call):
    chat_id = int(call.data.split('_')[2])
    g = games.get(chat_id)
    if not g or len(g['players']) < 2:
        bot.answer_callback_query(call.id, "Kam se kam 2 players chahiye!")
        return
    g['state'] = 'playing'
    g['turn_order'] = list(game['turn_order'] if 'turn_order' in (game:={}) else g['players'].keys())
    for pid, pdata in g['players'].items():
        try: bot.send_message(pid, f"📋 Board:\n`{format_bingo(pdata['board'], pdata['marked'])}`", parse_mode="Markdown")
        except: pass
    bot.send_message(chat_id, f"🔥 Bingo Shuru! Pehli baari: **{g['players'][g['turn_order'][0]]['name']}**\n(1-25 number chat me likho)")

def start_math_quiz(chat_id):
    n1, n2 = random.randint(10, 99), random.randint(2, 20)
    op = random.choice(MATH_OPS)
    ans = eval(f"{n1} {op} {n2}")
    options = list({ans, ans + random.randint(1, 5), ans - random.randint(1, 5), ans + 10})
    random.shuffle(options)
    markup = InlineKeyboardMarkup(row_width=2)
    for opt in options:
        markup.add(InlineKeyboardButton(str(opt), callback_data=f"quiz_ans_{opt}_{ans}"))
    bot.send_message(chat_id, f"⚡ **Maths Battle:**\n\n**{n1} {op} {n2} = ?**", reply_markup=markup)

def start_mind_puzzle(chat_id):
    p = random.choice(MIND_PUZZLES)
    markup = InlineKeyboardMarkup(row_width=2)
    for opt in p['opts']:
        markup.add(InlineKeyboardButton(opt, callback_data=f"quiz_ans_{opt}_{p['a']}"))
    bot.send_message(chat_id, f"🧠 **Mind Sharp Puzzle:**\n\n_{p['q']}_", reply_markup=markup, parse_mode="Markdown")

def start_general_quiz(chat_id):
    q = random.choice(GEN_QUIZ)
    markup = InlineKeyboardMarkup(row_width=2)
    for opt in q['opts']:
        markup.add(InlineKeyboardButton(opt, callback_data=f"quiz_ans_{opt}_{q['ans']}"))
    bot.send_message(chat_id, f"🎯 **Quiz:**\n\n**{q['q']}**", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('quiz_ans_'))
def handle_quiz_answer(call):
    _, _, selected, correct = call.data.split('_', 3)
    user_name = call.from_user.first_name
    if selected.strip().lower() == correct.strip().lower():
        bot.send_message(call.message.chat.id, f"🎉 Sahi Jawab! **{user_name}** ne answer diya: `{correct}`", parse_mode="Markdown")
        bot.delete_message(call.message.chat.id, call.message.message_id)
    else:
        bot.answer_callback_query(call.id, "❌ Galat jawab! Dobara koshish karo.")

@bot.message_handler(func=lambda message: message.text and message.text.isdigit())
def handle_bingo_turn(message):
    chat_id = message.chat.id
    if chat_id not in games or games[chat_id]['state'] != 'playing': return
    g = games[chat_id]
    if message.from_user.id != g['turn_order'][g['turn_idx']]: return
    num = int(message.text)
    if num < 1 or num > 25 or num in g['called']: return
    g['called'].add(num)
    for pid, pdata in g['players'].items():
        for r in range(5):
            for c in range(5):
                if pdata['board'][r][c] == num: pdata['marked'][r][c] = True
        if check_bingo_lines(pdata['marked']) >= 5:
            bot.send_message(chat_id, f"🎉 **BINGO! {pdata['name']} JEET GAYA!**")
            del games[chat_id]
            return
    g['turn_idx'] = (g['turn_idx'] + 1) % len(g['turn_order'])
    bot.send_message(chat_id, f"📢 Number **{num}** cut!\nAgli baari: **{g['players'][g['turn_order'][g['turn_idx']]]['name']}**")

bot.infinity_polling()
  
