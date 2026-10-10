# 💅 Prissy

A powerful, feature-packed Discord bot — merging the server-management depth of **Crumb** with the entertainment breadth of **Clanker**.

🌐 Website: https://prissy.pxsl.dev/

## 🔗 Bot Links

You can invite Prissy or view more information here:

- Website: https://prissy.pxsl.dev/
- Discord: https://discord.gg/YtQdrkxfg7

Prissy is completely free to use, with no paid features or subscriptions.

## 🧩 What's Inside

Prissy is the union of two bots, so it carries both feature sets:

**From Crumb (server management / moderation):**

- `automod` — automated moderation, blocked words, spam/caps/links/mentions filters
- `moderation` — ban, kick, timeout, warn/warnings, purge, slowmode, deafen/move
- `security` — antinuke, antiraid, lockdown, whitelist
- `verify` — captcha verification, verified/unverified roles
- `logging` — server, member, role, channel, message, and moderation event logs
- `reactionroles` (`rr`) — reaction-role menus
- `giveaway` — giveaways with start/end/reroll
- `levelling` — XP, levels, leaderboard, rank cards
- `sticky` — sticky messages
- `messages` — custom command responses
- `reminder` — `/remindme`
- `serverstats` — server statistics
- `tempvc` — temporary voice channels
- `utilities` — serverinfo, userinfo, roleinfo, channelinfo, invites, avatar, banner, snowflake, timestamp

**From Clanker (fun / media / social):**

- `basic` — ping, help, invite, uptime, cmdcount, define, weather, translate, urban, qr, github, dns, portcheck, whois, ip, and more
- `image` — blur, brighten, sharpen, invert, greyscale, deepfry, pixelate, distortion, rotate, caption, and more
- `video` — reverse, nightcore, slowed, reverb, speed, pitch, volume, stereo, and more
- `audio` — bassboost, nightcore, slowed, reverb, speed, pitch, volume, treble, stereo
- `text` — mock, zalgo, leet, uwu, reverse, ascii, randomcase, novowels, emoji kitchen, and more
- `games` — hangman, snake, wordle, rps, coinflip, dice, slots, roulette, clicker, and more
- `economy` — balance, daily, work, rob, give, take, deposit, withdraw, atm, leaderboard
- `social` — profile, ship, hug, slap, poke, highfive, compliment, roast, and more
- `utility` — weather, translate, calculate, password, announce, optin/optout, forgetme, and more
- `admin` — addadmin, removeadmin, listadmins, dm
- `theming` — seasonal name/avatar/banner themes
- `patches` — occasional promotional follow-up messages

## 📌 About This Repository

This repository contains the source code for Prissy.

The code is open source so the community can:

- 🐛 Report bugs
- 💡 Suggest improvements
- 🔧 Contribute fixes and features
- 📖 Learn from the project

## ⚠️ Self Hosting

Self-hosting Prissy is **not officially supported**.

The code may depend on:

- private configuration
- external services
- internal systems
- infrastructure that is not included in this repository

You are welcome to look through the code and contribute, but getting your own instance running is not guaranteed.

## 🚀 Running

```bash
pip install -r requirements.txt
cp config.ini.example config.ini   # then fill in TOKEN
python launcher.py                  # or: python bot.py
```

`config.ini`:

```ini
[DEFAULT]
TESTING = true
TEST_GUILD_ID = 0
TOKEN =            # your bot token
TOPGG_TOKEN =      # optional
PXSL_API_KEY =     # required unless TESTING = true
```

- `TESTING = true` syncs commands to `TEST_GUILD_ID` only (instant). Set to `false` for global sync (can take up to an hour).
- `TOPGG_TOKEN` is optional — leave blank to disable top.gg posting.
- `PXSL_API_KEY` is only required when `TESTING = false` (it gates the stats/command upload to the pxsl API).

## 📄 License

See [LICENSE](LICENSE) and [LICENSE.md](LICENSE.md).
