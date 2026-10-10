import discord
import datetime
from discord.ext import commands, tasks

THEMES = {
    "halloween": {
        "success": discord.Color.orange(),
        "fail": discord.Color.purple(),
        "avatar": "assets/halloween/avatar.png",
        "banner": "assets/halloween/banner.png",
        "name": "Spooky Prissy 🎃",
    },

    "fools": {
        "success": discord.Color.yellow(),
        "fail": discord.Color.magenta(),
        "avatar": "assets/fools/avatar.png",
        "banner": "assets/fools/banner.png",
        "name": "prissy uwu :3",
    },

    "christmas": {
        "success": discord.Color.green(),
        "fail": discord.Color.red(),
        "avatar": "assets/christmas/avatar.png",
        "banner": "assets/christmas/banner.png",
        "name": "Merry Prissy🎄",
    },

    "easter": {
        "success": discord.Color.green(),
        "fail": discord.Color.pink(),
        "avatar": "assets/easter/avatar.png",
        "banner": "assets/easter/banner.png",
        "name": "Prissy Bunny 🐰",
    },

    "default": {
        "success": discord.Color.blurple(),
        "fail": discord.Color.red(),
        "avatar": "assets/default/avatar.png",
        "banner": "assets/default/banner.png",
        "name": "Prissy",
    },
}

def get_theme():
    now = datetime.datetime.now(datetime.timezone.utc)

    if now.month == 4 and now.day == 1:
        return "fools"
    elif now.month == 10:
        return "halloween"
    elif now.month == 12:
        return "christmas"
    elif now.month == 3:
        return "easter"

    return "default"

def get_success_colour():
    return THEMES[get_theme()]["success"]

def get_fail_colour():
    return THEMES[get_theme()]["fail"]

def get_avatar():
    return THEMES[get_theme()]["avatar"]

def get_banner():
    return THEMES[get_theme()]["banner"]

def get_name():
    return THEMES[get_theme()]["name"]

class Theming(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.current_date = None
        self.applied_theme = None
        self.update_theme.start()

    def cog_unload(self):
        self.update_theme.cancel()

    async def apply_theme(self):
        # identity theming (seasonal username/avatar/banner) is disabled —
        # the bot keeps its own name/avatar. the seasonal *colours* still
        # work via get_success_colour()/get_fail_colour(), which cogs read
        # straight from THEMES. this now just tracks state so the loop is
        # a no-op instead of editing the bot's identity every midnight.
        now = datetime.datetime.now(datetime.timezone.utc)
        self.current_date = now.date()
        self.applied_theme = get_theme()

    @tasks.loop(
        time=datetime.time(
            hour=0,
            minute=0,
            second=0,
            tzinfo=datetime.timezone.utc
        )
    )
    async def update_theme(self):
        await self.apply_theme()

    @update_theme.before_loop
    async def before_update_theme(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    cog = Theming(bot)
    await bot.add_cog(cog)
    await cog.apply_theme()