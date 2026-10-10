# Prissy — merged from Crumb + Clanker
# base: clanker (sharding, welcome embed, stats tracking)
# intents: crumb (members + message_content, required by automod/levelling/moderation)
# no external reporting: top.gg + pxsl API removed

import discord
from discord.ext import commands, tasks
import asyncio
import os
import json
import time
import configparser
from cogs.theming import get_success_colour

os.makedirs("db", exist_ok=True)

ini = configparser.ConfigParser()

with open("data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

ini.read("config.ini")

TESTING = ini["DEFAULT"].getboolean("TESTING")
TEST_GUILD_ID = int(ini["DEFAULT"].get("TEST_GUILD_ID", "0"))

TOKEN = ini["DEFAULT"].get("TOKEN", "")
if not TOKEN:
    raise ValueError("Token not found in config.ini!")

# crumb's richer intents — clanker's guilds-only set would break
# automod (message content), levelling (message events), moderation (members)
intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.message_content = True

class Prissy(commands.AutoShardedBot):
    def __init__(self):
        super().__init__(
            command_prefix="prissy uses slash commands!",
            intents=intents
        )

        # ccu tracking — feeds /admin ccu and the status line
        self.active_users = {}
        self.peak_ccu = 0
        self.start_time = time.time()
        self.total_commands = 0
        self.command_timestamps = []
        self.last_command_at = None

    def export_commands(self):
        commands_data = []

        def walk_command(command, parent_path=""):
            current_path = (
                f"{parent_path} {command.name}".strip()
            )

            if isinstance(command, discord.app_commands.Group):
                for child in command.commands:
                    walk_command(child, current_path)
                return

            if "admin" in current_path.lower():
                return

            command_data = command.to_dict(self.tree)
            command_data["name"] = current_path
            commands_data.append(command_data)

        for command in self.tree.get_commands():
            walk_command(command)

        with open(
            "commands.json",
            "w",
            encoding="utf-8"
        ) as f:
            json.dump(
                commands_data,
                f,
                indent=4,
                ensure_ascii=False
            )

        print(
            f"[COMMANDS] Exported "
            f"{len(commands_data)} executable slash commands!"
        )
        return commands_data

    async def setup_hook(self):
        print("[BOOT] Loading cogs...")

        for file in os.listdir("./cogs"):
            if file.endswith(".py") and not file.startswith("_"):
                try:
                    await self.load_extension(
                        f"cogs.{file[:-3]}"
                    )
                    print(f"[BOOT] Loaded cog: {file}")
                except Exception as e:
                    print(
                        f"[BOOT] FAILED cog {file}: "
                        f"{type(e).__name__}: {e}"
                    )

        print("[BOOT] Syncing commands...")

        if TESTING:
            print(
                "[BOOT] Running in TESTING mode, "
                "syncing to TEST guild only."
            )

            guild = discord.Object(id=TEST_GUILD_ID)
            self.tree.copy_global_to(guild=guild)
            synced = await self.tree.sync(guild=guild)

            print(
                f"[SYNC] Synced "
                f"{len(synced)} commands to TEST guild"
            )
        else:
            try:
                await self.tree.sync()
                print("[SYNC] Synced global commands")
            except Exception as e:
                print(
                    f"[SYNC] Failed to sync global commands: "
                    f"{type(e).__name__}: {e}"
                )

            synced = self.tree.get_commands()
            print(
                f"[SYNC] Synced "
                f"{len(synced)} global commands"
            )

        self.export_commands()

        print("[BOOT] Status loop starting...")
        self.statusloop.start()

    @tasks.loop(seconds=5)
    async def statusloop(self):
        guild_count = len(self.guilds)

        activity = discord.CustomActivity(
            name=f"👀 prissy in {guild_count:,} servers!"
        )
        await self.change_presence(activity=activity)

        print(
            f"[STATUS UPDATE] "
            f"Guilds: {guild_count} | "
            f"Members: {total_members} | "
            f"Shards: {self.shard_count}"
        )

    @statusloop.before_loop
    async def before_statusloop(self):
        await self.wait_until_ready()


bot = Prissy()
bot.data = data

def extract_interaction_options(options):
    values = []

    for option in options:
        if "value" in option:
            values.append(str(option["value"]))

        nested_options = option.get("options")
        if nested_options:
            values.extend(
                extract_interaction_options(nested_options)
            )

    return values

@bot.event
async def on_ready():
    print(f"[READY] Logged in as {bot.user}")
    print("Prissy is alive 😎")

@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type != discord.InteractionType.application_command:
        return

    now = time.time()
    bot.active_users[interaction.user.id] = now

    expired = [
        uid
        for uid, last_seen in bot.active_users.items()
        if now - last_seen > 300
    ]

    for uid in expired:
        del bot.active_users[uid]

    bot.peak_ccu = max(bot.peak_ccu, len(bot.active_users))

    cmd = interaction.data.get("name", "unknown")
    options = interaction.data.get("options", [])

    option_values = extract_interaction_options(options)
    args = " ".join(option_values)

    bot.total_commands += 1
    bot.command_timestamps.append(now)
    bot.last_command_at = now

    print(
        f"[COMMAND LOG] "
        f"@{interaction.user}: "
        f"{cmd}"
        f"{' ' + args if args else ''}"
    )

class WelcomeView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

        self.add_item(
            discord.ui.Button(
                label="Join the Community",
                emoji="💬",
                url="https://discord.gg/KbYKSTHR5h"
            )
        )

        self.add_item(
            discord.ui.Button(
                label="Legal & Privacy",
                emoji="📄",
                url="https://prissy.pxsl.dev/legal"
            )
        )

        self.add_item(
            discord.ui.Button(
                label="Support Me!",
                emoji="💜",
                url="https://ko-fi.com/pxsldev/"
            )
        )

@bot.event
async def on_guild_join(guild: discord.Guild):
    embed = discord.Embed(
        title="👋 Thanks for adding Prissy!",
        description=(
            "Thanks for inviting **Prissy** to your server! ❤️\n\n"

            "## 💬 Join the Prissy Community\n"
            "Prissy isn't just a bot - it's a community too!\n\n"

            "Join our Discord to **meet other Prissy users, chat, "
            "share memes, suggest new features, report bugs, get "
            "updates, and take part in community events.**\n\n"

            "## 🔒 Privacy & Legal\n"
            "Want to know what information Prissy stores and how "
            "it's used? You can find our legal and privacy information "
            "using the button below.\n\n"

            "## 💜 Support Me\n"
            "Prissy is 100% free, with absolutely no paid features "
            "whatsoever. You can show that you appreciate this bot "
            "and support the development of Prissy by donating on "
            "[ko-fi](https://ko-fi.com/pxsldev/)\n\n"

            "**Thanks for choosing Prissy! 💅**"
        ),
        colour=get_success_colour()
    )

    embed.set_footer(
        text="Made with ❤️ by the Prissy team"
    )

    view = WelcomeView()

    preferred_names = {
        "general",
        "chat",
        "main",
        "bot",
        "bots",
        "commands",
        "prissy"
    }

    if guild.system_channel:
        perms = guild.system_channel.permissions_for(guild.me)

        if perms.send_messages and perms.embed_links:
            try:
                await guild.system_channel.send(
                    embed=embed,
                    view=view
                )
                print(
                    f"[WELCOME] Sent welcome message in "
                    f"#{guild.system_channel.name} ({guild.id})"
                )
                return
            except discord.Forbidden:
                pass
            except discord.HTTPException:
                pass

    for channel in guild.text_channels:
        if channel.name.lower() not in preferred_names:
            continue

        perms = channel.permissions_for(guild.me)

        if not (perms.send_messages and perms.embed_links):
            continue

        try:
            await channel.send(embed=embed, view=view)
            print(
                f"[WELCOME] Sent welcome message in "
                f"#{channel.name} ({guild.id})"
            )
            return
        except discord.Forbidden:
            continue
        except discord.HTTPException:
            continue

    for channel in guild.text_channels:
        perms = channel.permissions_for(guild.me)

        if not (perms.send_messages and perms.embed_links):
            continue

        try:
            await channel.send(embed=embed, view=view)
            print(
                f"[WELCOME] Sent welcome message in "
                f"#{channel.name} ({guild.id})"
            )
            return
        except discord.Forbidden:
            continue
        except discord.HTTPException:
            continue

    print(
        f"[WELCOME] Could not find a channel to send in "
        f"{guild.name} ({guild.id})"
    )

async def main():
    async with bot:
        await bot.start(TOKEN)

asyncio.run(main())
