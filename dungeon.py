import discord
import random
import asyncio
from discord.ext import commands

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

dungeon_sessions = {}

# 📜 FRAGEN & PASSENDE ANTWORTEN
dungeon_scenarios = [
    {
        "question": "Du stehst in einer dunklen Höhle... vor dir **drei Türen**. Welche wählst du?",
        "answers": ["Blutrote Tür", "Eiskalte Tür", "Grüne Moostür"]
    },
    {
        "question": "Vor dir erscheint eine alte Hexe. Was tust du?",
        "answers": ["Mit ihr reden", "Ihr einen Trank klauen", "Wegrennen"]
    },
    {
        "question": "Du hörst ein tiefes Knurren in der Dunkelheit... Was tust du?",
        "answers": ["Kämpfen", "Still stehen", "Zurücklaufen"]
    },
    {
        "question": "Eine große Falltür taucht vor dir auf. Was tust du?",
        "answers": ["Springen", "Umgehen", "Nach einem Seil suchen"]
    },
    {
        "question": "Du siehst eine Schatztruhe! Öffnen oder nicht?",
        "answers": ["Öffnen", "Ignorieren", "Nach Fallen untersuchen"]
    },
    {
        "question": "Ein Fluss blockiert deinen Weg. Was tust du?",
        "answers": ["Schwimmen", "Brücke suchen", "Ein Floß bauen"]
    },
    {
        "question": "Eine Statue beginnt zu sprechen. Wie reagierst du?",
        "answers": ["Antworten", "Ignorieren", "Angreifen"]
    },
    {
        "question": "Du findest eine alte Karte auf dem Boden. Was tust du?",
        "answers": ["Aufheben", "Liegen lassen", "Verbrennen"]
    }
]

# 🏆 ZUFÄLLIGE ENDE-SZENARIEN
dungeon_endings = [
    "**Du hast den Dungeon überlebt!** 🎉",
    "**Ein Monster tötet dich... GAME OVER!** 💀",
    "**Du findest eine geheime Tür und entkommst!** 🏆",
    "**Du fällst in eine Falle und stirbst.** 💀",
    "**Eine Schatztruhe explodiert! GAME OVER!** 💥"
]

# ✅ BEFEHL: Starte das Dungeon-Abenteuer
@bot.command()
async def dungeon(ctx):
    user_id = ctx.author.id

    if user_id in dungeon_sessions:
        await ctx.send(f"{ctx.author.mention}, du bist bereits im Dungeon! Nutze einfach `1`, `2` oder `3`.")
        return

    questions_copy = list(dungeon_scenarios)  # Erstelle eine Kopie der Fragenliste
    random.shuffle(questions_copy)  # Mische die Reihenfolge
    dungeon_sessions[user_id] = {"step": 0, "questions": questions_copy}
    
    await send_dungeon_room(ctx, user_id)

# ✅ FUNKTION: Sende ein Dungeon-Szenario mit zufälligen Antwortmöglichkeiten
async def send_dungeon_room(ctx, user_id):
    if user_id not in dungeon_sessions:
        return

    session = dungeon_sessions[user_id]
    
    if session["step"] >= 5:  # Mindestens 5 Räume
        ending = random.choice(dungeon_endings)
        embed = discord.Embed(
            title="🏆 Dungeon Escape – Dein Schicksal!",
            description=ending,
            color=discord.Color.green() if "🏆" in ending else discord.Color.red()
        )
        await ctx.send(embed=embed)
        del dungeon_sessions[user_id]  # Dungeon zurücksetzen
        return

    current_scenario = session["questions"].pop(0)  # Nächste Frage
    question_text = current_scenario["question"]
    answer_set = list(current_scenario["answers"])  # Kopie der Antwortenliste
    random.shuffle(answer_set)  # Mische Antworten zufällig

    session["choices"] = answer_set
    session["step"] += 1

    embed = discord.Embed(
        title="🏰 Dungeon Escape!",
        description=question_text + "\n\n" +
                    f"1️⃣ **{answer_set[0]}**\n"
                    f"2️⃣ **{answer_set[1]}**\n"
                    f"3️⃣ **{answer_set[2]}**",
        color=discord.Color.dark_blue()
    )
    embed.set_footer(text="Nutze 1, 2 oder 3, um deine Entscheidung zu treffen!")
    await ctx.send(embed=embed)

# ✅ EVENT: Fängt Nachrichten ab, um `1`, `2`, `3` als Wahl zu nutzen
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    user_id = message.author.id
    if user_id in dungeon_sessions and message.content in ["1", "2", "3"]:
        await handle_choice(message, int(message.content))
    
    await bot.process_commands(message)  # WICHTIG: Lässt andere Befehle weiterhin funktionieren

# ✅ FUNKTION: Verarbeitet Spielerentscheidungen
async def handle_choice(message, number):
    user_id = message.author.id
    if user_id not in dungeon_sessions:
        return

    session = dungeon_sessions[user_id]
    choice_made = session["choices"][number - 1]  # Speichert die getroffene Wahl

    # 📜 Reaktion auf Entscheidung
    reaction_texts = [
        f"Du hast `{choice_made}` gewählt... Etwas passiert!",
        f"Du spürst eine seltsame Präsenz nachdem du `{choice_made}` gewählt hast...",
        f"Plötzlich verändert sich die Umgebung nach deiner Entscheidung `{choice_made}`..."
    ]
    
    embed = discord.Embed(
        title="🔮 Entscheidung getroffen!",
        description=random.choice(reaction_texts),
        color=discord.Color.purple()
    )
    await message.channel.send(embed=embed)

    # Nächste Szene senden
    await send_dungeon_room(message.channel, user_id)

# ✅ AUTOMATISCHER RESET ALLE 2 STUNDEN
async def reset_dungeon():
    await bot.wait_until_ready()
    while not bot.is_closed():
        dungeon_sessions.clear()
        print("🔄 Alle Dungeon-Sessions wurden zurückgesetzt!")
        await asyncio.sleep(7200)  # 7200 Sekunden = 2 Stunden

# ✅ SETUP-HOOK VERWENDEN STATT LOOP-FEHLER
@bot.event
async def on_ready():
    print(f"✅ {bot.user} ist bereit!")
    bot.loop.create_task(reset_dungeon())  # Automatischer Reset wird hier gestartet!

# ✅ BOT STARTEN – FÜGE HIER DEINEN TOKEN EIN!
bot.run("TOKEN")
