import os
from threading import Thread
from flask import Flask
import telebot
from telebot import types

# --- 🌐 1. Render ፖርት ማታለያ የዌብ ሰርቨር ኮድ ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    # Render የሚሰጠውን ፖርት ያነባል
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# ሰርቨሩን በስተጀርባ ያስነሳል
keep_alive()


# --- 🛠 2. ያንተ የቦት መረጃዎች (የተስተካከለ) ---
API_TOKEN = '8693308102:AAFS-b4om4C8r6IgCD6GQ__Jo7yKHheOUT4'
ADMIN_ID = 1477437632

bot = telebot.TeleBot(API_TOKEN)

# --- 🗄 ጊዜያዊ የዳታቤዝ መዝገብ ---
user_data = {}
active_tasks = []

# --- 3. Start Command & Reply Keyboard ---
@bot.message_handler(commands=['start'])
def start_message(message):
    user_id = message.from_user.id
    text_args = message.text.split()
    
    if user_id not in user_data:
        user_data[user_id] = {'balance': 0.0, 'completed_tasks': [], 'referred_by': None, 'referrals': 0}
        
        # የሪፈራል ሲስተም
        if len(text_args) > 1:
            try:
                referrer_id = int(text_args[1])
                if referrer_id in user_data and referrer_id != user_id:
                    user_data[user_id]['referred_by'] = referrer_id
                    user_data[referrer_id]['balance'] += 0.50
                    user_data[referrer_id]['referrals'] += 1
                    bot.send_message(referrer_id, "🎉 አዲስ ሰው በሊንክህ ገብቷል! 0.50 ETB ተጨምሮልሃል።")
            except:
                pass

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    btn1 = types.KeyboardButton("💼 ስራዎችን ስራ (Earn)")
    btn2 = types.KeyboardButton("👥 ሰዎችን ጋብዝ (Referral)")
    btn3 = types.KeyboardButton("💰 የኔ ሂሳብ (Balance)")
    btn4 = types.KeyboardButton("💳 ገንዘብ ማውጫ (Withdraw)")
    
    markup.row(btn1, btn2)
    markup.row(btn3, btn4)
    
    if user_id == ADMIN_ID:
        btn_admin = types.KeyboardButton("🛠 የአድሚን ገጽ (Admin Panel)")
        markup.row(btn_admin)
        
    welcome_text = f"ሰላም {message.from_user.first_name}! ወደ Ethio JumpTask ቦት በሰላም መጣህ። ከታች ያሉትን በተኖች በመጫን ስራ መጀመር ትችላለህ።"
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

# --- 4. Main Menu Handlers ---
@bot.message_handler(func=lambda message: True)
def handle_menu(message):
    user_id = message.from_user.id
    if user_id not in user_data:
        user_data[user_id] = {'balance': 0.0, 'completed_tasks': [], 'referred_by': None, 'referrals': 0}

    if message.text == "💼 ስራዎችን ስራ (Earn)":
        if not active_tasks:
            bot.send_message(message.chat.id, "❌ ለአሁን አዲስ የተጫነ ማስታወቂያ ወይም ስራ የለም! ቆይተው ይሞክሩ።")
            return
            
        markup = types.InlineKeyboardMarkup()
        has_new_task = False
        for task in active_tasks:
            if task['id'] not in user_data[user_id]['completed_tasks']:
                btn = types.InlineKeyboardButton(f"🎯 {task['name']} ({task['reward']} ETB)", callback_data=f"view_{task['id']}")
                markup.add(btn)
                has_new_task = True
                
        if has_new_task:
            bot.send_message(message.chat.id, "የሚከተሉትን ስራዎች በመስራት እውነተኛ ብር ያግኙ፡", reply_markup=markup)
        else:
            bot.send_message(message.chat.id, "🎉 ሁሉንም ስራዎች ሰርተህ ጨርሰሃል! አዳዲስ ስራዎች ሲኖሩ እናሳውቃለን።")

    elif message.text == "👥 ሰዎችን ጋብዝ (Referral)":
        bot_info = bot.get_me()
        referral_link = f"https://t.me{bot_info.username}?start={user_id}"
        msg = f"👥 **የመጋበዣ ፕሮግራም**\n\nየእርስዎን ሊንክ ለጓደኞችዎ ያጋሩ! አንድ ሰው በሊንክዎ ሲገባ **0.50 ETB** ያገኛሉ።\n\n🔗 የእርስዎ ሊንክ፡\n{referral_link}"
        bot.send_message(message.chat.id, msg)

    elif message.text == "💰 የኔ ሂሳብ (Balance)":
        data = user_data[user_id]
        bot.send_message(message.chat.id, f"📊 **የአካውንትዎ መረጃ**\n\n💵 ያለዎት ብር: {data['balance']:.2f} ETB\n🎁 የጋበዙት ሰው ብዛት: {data['referrals']} ሰው")

    elif message.text == "💳 ገንዘብ ማውጫ (Withdraw)":
        data = user_data[user_id]
        if data['balance'] >= 25.0:
            bot.send_message(message.chat.id, "💰 ማውጣት የሚፈልጉትን የብር መጠን እና የቴሌብር ወይም ሲቢኢ ብር ስልክ ቁጥርዎን አንድ ላይ ጽፈው ይላኩ።\n\n*ምሳሌ፦ 50 ብር፣ 0911223344 ቴሌብር*")
            bot.register_next_step_handler(message, process_withdraw)
        else:
            bot.send_message(message.chat.id, "❌ **ይቅርታ!** ገንዘብ ለማውጣት ቢያንስ **25.00 ETB** ሊኖርዎት ይገባል።")

    elif message.text == "🛠 የአድሚን ገጽ (Admin Panel)" and user_id == ADMIN_ID:
        markup = types.InlineKeyboardMarkup()
        btn_add = types.InlineKeyboardButton("➕ አዲስ ስራ ጨምር", callback_data="admin_add_task")
        btn_stats = types.InlineKeyboardButton("📊 አጠቃላይ ዩዘርስ", callback_data="admin_stats")
        markup.add(btn_add, btn_stats)
        bot.send_message(message.chat.id, "እንኳን ወደ አድሚን ማዘዣ ጣቢያ መጡ። ምን ማድረግ ይፈልጋሉ?", reply_markup=markup)

# --- 5. Callback Handlers ---
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    user_id = call.from_user.id
    
    if call.data.startswith("view_"):
        task_id = int(call.data.split("_")[1])
        task = next((t for t in active_tasks if t['id'] == task_id), None)
        if task:
            markup = types.InlineKeyboardMarkup()
            btn_link = types.InlineKeyboardButton("🔗 ሊንኩን ክፈት / ስራውን ስራ", url=task['link'])
            btn_verify = types.InlineKeyboardButton("✅ ስራውን ጨርሻለሁ አረጋግጥ", callback_data=f"verify_{task_id}")
            markup.add(btn_link)
            markup.add(btn_verify)
            bot.send_message(call.message.chat.id, f"📋 **የስራ መመሪያ፦**\n\n{task['desc']}\n\n💰 ሽልማት: {task['reward']} ETB", reply_markup=markup)

    elif call.data.startswith("verify_"):
        task_id = int(call.data.split("_")[1])
        task = next((t for t in active_tasks if t['id'] == task_id), None)
        if task:
            if task_id not in user_data[user_id]['completed_tasks']:
                user_data[user_id]['balance'] += task['reward']
                user_data[user_id]['completed_tasks'].append(task_id)
                bot.answer_callback_query(call.id, f"🎉 ደስ የሚል ዜና! {task['reward']} ETB ወደ አካውንትዎ ተጨምሯል።", show_alert=True)
                bot.delete_message(call.message.chat.id, call.message.message_id)
            else:
                bot.send_message(call.message.chat.id, "❌ ይህንን ስራ ቀደም ብለው ሰርተውታል።")

    elif call.data == "admin_add_task" and user_id == ADMIN_ID:
        bot.send_message(call.message.chat.id, "እባክዎ አዲሱን ስራ በዚህ ፎርማት ይጻፉልኝ (በኮማ በመለየት)፦\n\n**የስራው ስም, ሊንክ, የክፍያ መጠን, መመሪያ**\n\n*ምሳሌ፦ ቴሌግራም ጆይን, https://t.meExample, 0.40, ይህንን ቻናል ተቀላቀሉ*")
        bot.register_next_step_handler(call.message, save_new_task)

    elif call.data == "admin_stats" and user_id == ADMIN_ID:
        total_users = len(user_data)
        bot.send_message(call.message.chat.id, f"📈 **የቦቱ ወቅታዊ መረጃ**\n\n👥 ጠቅላላ የተመዘገቡ ተጠቃሚዎች: {total_users}\n🎯 በቦቱ ላይ ያሉ ንቁ ስራዎች: {len(active_tasks)}")

# --- 6. Save Task & Withdraw Logic ---
def save_new_task(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        parts = message.text.split(",")
        name = parts[0].strip()
        link = parts[1].strip()
        reward = float(parts[2].strip())
        desc = parts[3].strip()
        
        task_id = len(active_tasks) + 1
        active_tasks.append({'id': task_id, 'name': name, 'link': link, 'reward': reward, 'desc': desc})
        bot.send_message(message.chat.id, "✅ አዲሱ ስራ በተሳካ ሁኔታ ተጭኗል!")
    except:
        bot.send_message(message.chat.id, "❌ ስህተት ተፈጥሯል። እባክዎ አጻጻፉን አስተካክለው ድጋሚ ይሞክሩ።")

def process_withdraw(message):
    user_id = message.from_user.id
    request_details = message.text
    admin_msg = f"🔔 **አዲስ የገንዘብ ማውጫ ጥያቄ ደርሷል!**\n\n👤 ተጠቃሚ ID: `{user_id}`\n👤 ስም: {message.from_user.first_name}\n💳 ዝርዝር መረጃ: {request_details}"
    bot.send_message(ADMIN_ID, admin_msg)
    user_data[user_id]['balance'] = 0.0
    bot.send_message(message.chat.id, "✅ የገንዘብ ማውጫ ጥያቄዎ ለአስተዳዳሪው ደርሷል።")

# --- ቦቱን ማስነሻ ---
print("🚀 ቦቱ እና የዌብ ሰርቨሩ በሰላም ስራ ጀምረዋል...")
bot.infinity_polling()
