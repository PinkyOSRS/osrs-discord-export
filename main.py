import os
import csv
import discord
import asyncio
from flask import Flask, request, jsonify
from threading import Thread

BOT_TOKEN = os.environ.get("DISCORD_TOKEN")
GUILD_ID = int(os.environ.get("DISCORD_GUILD_ID"))

intents = discord.Intents.default()
intents.members = True
intents.guilds = True

client = discord.Client(intents=intents)
app = Flask(__name__)

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

@app.route('/')
def index():
    return "Discord Export Bot is running."

@app.route('/export', methods=['POST'])
def export_members():
    def run_bot():
        loop.run_until_complete(run_export())

    Thread(target=run_bot).start()
    return jsonify({"status": "started"}), 202

async def run_export():
    await client.login(BOT_TOKEN)
    await client.connect()

@client.event
async def on_ready():
    print(f"[INFO] Logged in as {client.user}")
    guild = client.get_guild(GUILD_ID)

    if not guild:
        print(f"[ERROR] Could not find guild with ID {GUILD_ID}")
        await client.close()
        return

    print(f"[INFO] Fetching members from: {guild.name} ({guild.id})")
    members = [member async for member in guild.fetch_members(limit=None)]

    with open("discord_members.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["User", "Global Display Name", "ID", "Nickname"])
        writer.writeheader()
        for member in members:
            writer.writerow({
                "User": member.name,
                "Global Display Name": member.global_name or "",
                "ID": member.id,
                "Nickname": member.nick or ""
            })

    print("[INFO] Member list exported to discord_members.csv")
    await client.close()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

