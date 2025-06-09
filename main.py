from keep_alive import keep_alive
import discord
from discord.ext import commands, tasks
import datetime
import json
import os
import aiohttp

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Load saved birthdays
try:
    with open('birthdays.json', 'r') as f:
        birthdays = json.load(f)
except FileNotFoundError:
    birthdays = {}

@bot.event
async def on_ready():
    print(f'✅ Bot is online as {bot.user}')
    check_birthdays.start()
    send_good_morning.start()
    send_good_night.start()
    send_daily_quote.start()

@bot.command()
async def setbday(ctx, month: int, day: int):
    user_id = str(ctx.author.id)
    birthdays[user_id] = {"month": month, "day": day}
    with open('birthdays.json', 'w') as f:
        json.dump(birthdays, f)
    await ctx.send(f"🎉 Birthday saved for {ctx.author.mention}: {month}/{day}")

@bot.command()
async def addbday(ctx, user_id: int, month: int, day: int):
    birthdays[str(user_id)] = {"month": month, "day": day}
    with open('birthdays.json', 'w') as f:
        json.dump(birthdays, f)
    await ctx.send(f"🎉 Birthday saved for <@{user_id}>: {month}/{day}")

@bot.command()
async def ping(ctx):
    await ctx.send("🏓 Pong! I'm alive.")

@tasks.loop(hours=24)
async def check_birthdays():
    today = datetime.datetime.now()
    for user_id, bday in birthdays.items():
        if bday["month"] == today.month and bday["day"] == today.day:
            channel = discord.utils.get(bot.get_all_channels(), name='general')
            user = await bot.fetch_user(int(user_id))
            message = f"🎉 Happy Birthday, {user.mention}! 🎂\nWishing you a day filled with love, laughter, and unforgettable memories. May your journey ahead be as amazing as you are."
            gif_url = "https://media.giphy.com/media/xUPGcguWZHRC2HyBRS/giphy.gif"
            if channel:
                await channel.send(message)
                await channel.send(gif_url)
            try:
                await user.send(message)
                await user.send(gif_url)
            except:
                pass

@tasks.loop(time=datetime.time(hour=6, minute=0))
async def send_good_morning():
    gif_url = "https://media.giphy.com/media/l2JhLz2V7Nl6sB0u4/giphy.gif"
    message = "☀️ Good Morning! A brand new day awaits, full of possibilities. Have a great one! 💖"
    for user_id in birthdays.keys():
        user = await bot.fetch_user(int(user_id))
        try:
            await user.send(message)
            await user.send(gif_url)
        except:
            pass

@tasks.loop(time=datetime.time(hour=23, minute=0))
async def send_good_night():
    gif_url = "https://media.giphy.com/media/jlrE3zzkMXze8/giphy.gif"
    message = "🌙 Good Night! Drift off into dreams wrapped in stardust. Sleep well! 💖"
    for user_id in birthdays.keys():
        user = await bot.fetch_user(int(user_id))
        try:
            await user.send(message)
            await user.send(gif_url)
        except:
            pass

@tasks.loop(time=datetime.time(hour=12, minute=0))
async def send_daily_quote():
    quote_text = "Stay inspired!"  # Fallback
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://zenquotes.io/api/random") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    quote_text = f"{data[0]['q']} – {data[0]['a']}"
    except Exception as e:
        print("Quote fetch error:", e)

    for user_id in birthdays.keys():
        user = await bot.fetch_user(int(user_id))
        try:
            await user.send(f"🧐 Daily Quote:\n{quote_text}")
        except:
            pass

# Helper function to send Good Night message manually
async def send_good_night_function():
    gif_url = "https://media.giphy.com/media/jlrE3zzkMXze8/giphy.gif"
    message = "🌙 Good Night! Drift off into dreams wrapped in stardust. Sleep well! 💖"
    for user_id in birthdays.keys():
        user = await bot.fetch_user(int(user_id))
        try:
            await user.send(message)
            await user.send(gif_url)
        except:
            pass

# Command to manually trigger Good Night message
@bot.command()
async def testnight(ctx):
    await send_good_night_function()
    await ctx.send("✅ Good Night message manually sent.")

keep_alive()
bot.run(os.getenv("TOKEN"))

