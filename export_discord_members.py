import discord
import csv
import asyncio

# === Replace with your bot token ===
BOT_TOKEN = os.environ.get("DISCORD_TOKEN")

# === Replace with your server (guild) ID ===
GUILD_ID = 1373786836077514783  # Theoatrix Clan

intents = discord.Intents.default()
intents.members = True
intents.guilds = True

client = discord.Client(intents=intents)

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

client.run(BOT_TOKEN)

