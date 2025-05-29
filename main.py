import os
import csv
import discord
import asyncio
import base64
import requests
from datetime import datetime
from flask import Flask, request, jsonify
from threading import Thread

# === Bot config ===
BOT_TOKEN = os.environ.get("DISCORD_TOKEN")
GUILD_ID = int(os.environ.get("DISCORD_GUILD_ID"))

# === GitHub config ===
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_USERNAME = os.environ.get("GITHUB_USERNAME")
GITHUB_REPO = "osrs-clan-rank-sync"
GITHUB_FILEPATH = "data/discord_members.csv"

# === Discord client and Flask app setup ===
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

async def push_to_github():
    api_url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO}/contents/{GITHUB_FILEPATH}"

    with open("discord_members.csv", "rb") as f:
        content = f.read()
        encoded = base64.b64encode(content).decode()

    # Check if the file already exists to get the SHA
    response = requests.get(api_url, headers={"Authorization": f"token {GITHUB_TOKEN}"})
    sha = response.json().get("sha") if response.status_code == 200 else None

    commit_msg = f"Update discord_members.csv ({datetime.utcnow().isoformat()} UTC)"
    data = {
        "message": commit_msg,
        "content": encoded,
        "branch": "main",
    }
    if sha:
        data["sha"] = sha

    r = requests.put(api_url, headers={"Authorization": f"token {GITHUB_TOKEN}"}, json=data)

    if r.status_code in (200, 201):
        print("[INFO] File pushed to GitHub")
    else:
        print(f"[ERROR] GitHub push failed: {r.status_code}, {r.text}")

@client.event
async def on_ready():
    print(f"[INFO] Logged in as {client.user}")
    guild = client.get_guild(GUILD_ID)

    if not guild:
        print(f"[ERROR] Could not find guild with ID {GUILD_ID}")
        await client.close()
