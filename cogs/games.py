import aiohttp
import discord
import random
from discord import app_commands, Interaction
from discord.ext import commands
from cogs.theming import get_fail_colour, get_success_colour

class WordleView(discord.ui.View):
    def __init__(self, user_id, word, valid_words):
        super().__init__(timeout=900)

        self.user_id = user_id
        self.word = word.lower()
        self.valid_words = valid_words
        self.guesses = []
        self.finished = False

        self.guess_button = discord.ui.Button(
            label="Guess",
            style=discord.ButtonStyle.primary,
            emoji="✏️"
        )

        self.guess_button.callback = self.guess

        self.quit_button = discord.ui.Button(
            label="Quit",
            style=discord.ButtonStyle.danger,
            emoji="🚪"
        )

        self.quit_button.callback = self.quit

        self.add_item(self.guess_button)
        self.add_item(self.quit_button)

    async def interaction_check(self, interaction: Interaction):
        if interaction.user.id != self.user_id:
            embed = discord.Embed(
                title="🚫 That's not your Wordle!",
                description="You can't interact with someone else's game.",
                color=get_fail_colour()
            )

            await interaction.response.send_message(
                embed=embed,
                ephemeral=True
            )

            return False

        return True

    def get_grid(self):
        rows = []

        for guess in self.guesses:
            result = ["⬛"] * 5
            remaining = list(self.word)

            for i in range(5):
                if guess[i] == self.word[i]:
                    result[i] = "🟩"
                    remaining[i] = None

            for i in range(5):
                if result[i] == "🟩":
                    continue

                if guess[i] in remaining:
                    result[i] = "🟨"
                    remaining[remaining.index(guess[i])] = None

            rows.append(f"{guess}  {''.join(result)}")

        while len(rows) < 6:
            rows.append("-----  ⬜⬜⬜⬜⬜")

        return "\n".join(rows)

    def get_embed(self):
        embed = discord.Embed(
            title="Wordle",
            description=f"```text\n{self.get_grid()}\n```",
            color=get_success_colour()
        )

        embed.set_footer(
            text=f"Attempt {len(self.guesses)}/6 • Only you can play this game"
        )

        return embed

    async def guess(self, interaction: Interaction):
        if self.finished:
            embed = discord.Embed(
                title="🚫 Wordle has ended!",
                description="This game is already finished.",
                color=get_fail_colour()
            )

            await interaction.response.send_message(
                embed=embed,
                ephemeral=True
            )

            return

        await interaction.response.send_modal(
            WordleModal(self)
        )

    async def quit(self, interaction: Interaction):
        if self.finished:
            embed = discord.Embed(
                title="🚫 Wordle has ended!",
                description="This game is already finished.",
                color=get_fail_colour()
            )

            await interaction.response.send_message(
                embed=embed,
                ephemeral=True
            )

            return

        self.finished = True
        self.guess_button.disabled = True
        self.quit_button.disabled = True

        embed = self.get_embed()

        embed.title = "Wordle — You quit! 🚪"

        embed.description = (
            f"```text\n{self.get_grid()}\n```\n"
            f"The word was **{self.word}**.\n"
            f"Better luck next time!"
        )

        embed.color = get_fail_colour()
        embed.set_footer(text="Game ended by you.")

        await interaction.response.edit_message(
            embed=embed,
            view=self
        )

    async def on_timeout(self):
        self.finished = True
        self.guess_button.disabled = True
        self.quit_button.disabled = True

class WordleModal(discord.ui.Modal, title="Make a guess"):
    guess_input = discord.ui.TextInput(
        label="Your 5-letter guess",
        placeholder="Enter a word...",
        min_length=5,
        max_length=5,
        required=True
    )

    def __init__(self, game):
        super().__init__()
        self.game = game

    async def on_submit(self, interaction: Interaction):
        if self.game.finished:
            embed = discord.Embed(
                title="🚫 Wordle has ended!",
                description="This game is already finished.",
                color=get_fail_colour()
            )

            await interaction.response.send_message(
                embed=embed,
                ephemeral=True
            )

            return

        guess = self.guess_input.value.strip().lower()

        if len(guess) != 5 or not guess.isalpha():
            embed = discord.Embed(
                title="🚫 Invalid guess",
                description="Your guess must contain exactly **5 letters**.",
                color=get_fail_colour()
            )

            await interaction.response.send_message(
                embed=embed,
                ephemeral=True
            )

            return

        if guess not in self.game.valid_words:
            embed = discord.Embed(
                title="🚫 Not a valid word",
                description=f"**{guess}** isn't in the Wordle word list.",
                color=get_fail_colour()
            )

            await interaction.response.send_message(
                embed=embed,
                ephemeral=True
            )

            return

        self.game.guesses.append(guess)

        if guess == self.game.word:
            attempts = len(self.game.guesses)

            self.game.finished = True
            self.game.guess_button.disabled = True
            self.game.quit_button.disabled = True

            embed = self.game.get_embed()

            embed.title = "Wordle — You won! 🎉"

            embed.description = (
                f"```text\n{self.game.get_grid()}\n```\n"
                f"You guessed the correct word **{self.game.word}** "
                f"in **{attempts} attempt{'s' if attempts != 1 else ''}!**"
            )

            embed.color = get_success_colour()
            embed.set_footer(text="Congratulations! 🎉")

            await interaction.response.edit_message(
                embed=embed,
                view=self.game
            )

            return

        if len(self.game.guesses) >= 6:
            self.game.finished = True
            self.game.guess_button.disabled = True
            self.game.quit_button.disabled = True

            embed = self.game.get_embed()

            embed.title = "Wordle — Game over 💀"

            embed.description = (
                f"```text\n{self.game.get_grid()}\n```\n"
                f"The word was **{self.game.word}**.\n"
                f"Better luck next time!"
            )

            embed.color = get_fail_colour()
            embed.set_footer(text="Maybe you'll get it next time!")

            await interaction.response.edit_message(
                embed=embed,
                view=self.game
            )

            return

        await interaction.response.edit_message(
            embed=self.game.get_embed(),
            view=self.game
        )

class HangmanView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=900)
        
        self.user_id = user_id
        self.word = None
        self.guessed_letters = []
        self.wrong_letters = []
        self.remaining_attempts = 6
        self.finished = False
        
        self.set_word_button = discord.ui.Button(
            label="Set Word", style=discord.ButtonStyle.success, emoji="📝"
        )
        self.set_word_button.callback = self.set_word

        self.guess_word_button = discord.ui.Button(
            label="Guess Word",
            style=discord.ButtonStyle.primary,
            emoji="✏️",
            disabled=True,
        )
        self.guess_word_button.callback = self.guess_word

        self.add_item(self.set_word_button)
        self.add_item(self.guess_word_button)

    def get_display_word(self):
        if not self.word:
            return "_ " * 5

        return " ".join(
            letter if letter in self.guessed_letters else "_" for letter in self.word
        )

    def get_hangman(self):
        stages = [
            "```text\n  +---+\n  |   |\n      |\n      |\n      |\n=========\n```",
            "```text\n  +---+\n  |   |\n  O   |\n      |\n      |\n=========\n```",
            "```text\n  +---+\n  |   |\n  O   |\n  |   |\n      |\n=========\n```",
            "```text\n  +---+\n  |   |\n  O   |\n /|   |\n      |\n=========\n```",
            "```text\n  +---+\n  |   |\n  O   |\n /|\\  |\n      |\n=========\n```",
            "```text\n  +---+\n  |   |\n  O   |\n /|\\  |\n /    |\n=========\n```",
            "```text\n  +---+\n  |   |\n  O   |\n /|\\  |\n / \\  |\n=========\n```",
        ]

        return stages[6 - self.remaining_attempts]

    def get_embed(self):
        if not self.word:
            description = (
                "The game has been created, but no word has been set yet.\n\n"
                "The person who started the game can click Set Word "
                "to choose the secret word."
            )

        else:
            guessed = (
                ", ".join(self.guessed_letters) if self.guessed_letters else "None"
            )
            wrong = ", ".join(self.wrong_letters) if self.wrong_letters else "None"
            description = (
                f"{self.get_hangman()}\n"
                f"`Word:` {self.get_display_word()}\n\n"
                f"`Wrong letters:` {wrong}\n"
                f"`Guessed letters:` {guessed}\n\n"
                f"`Attempts remaining:` {self.remaining_attempts}"
            )

        embed = discord.Embed(title="Hangman", description=description, color=get_success_colour())

        if not self.word:
            embed.set_footer(
                text="Only the person who started the game can set the word."
            )
        else:
            embed.set_footer(text="Anyone can guess letters!")

        return embed

    async def set_word(self, interaction: Interaction):
        if interaction.user.id != self.user_id:
            embed = discord.Embed(
                title="🚫 You can't set the word",
                description="Only the person who started this Hangman game can set the word.",
                color=get_fail_colour(),
            )

            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if self.finished:
            embed = discord.Embed(
                title="🚫 Hangman has ended!",
                description="This game is already finished.",
                color=get_fail_colour(),
            )

            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        await interaction.response.send_modal(HangmanSetWordModal(self))

    async def guess_word(self, interaction: Interaction):
        if self.finished:
            embed = discord.Embed(
                title="🚫 Hangman has ended!",
                description="This game is already finished.",
                color=get_fail_colour(),
            )

            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if not self.word:
            embed = discord.Embed(
                title="🚫 No word has been set",
                description="The game creator needs to set the word before anyone can guess.",
                color=get_fail_colour(),
            )

            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        await interaction.response.send_modal(HangmanGuessModal(self))

    async def on_timeout(self):
        self.finished = True
        self.set_word_button.disabled = True
        self.guess_word_button.disabled = True


class HangmanSetWordModal(discord.ui.Modal, title="Set the Hangman word"):
    word_input = discord.ui.TextInput(
        label="Secret word",
        placeholder="Enter the word to use...",
        min_length=1,
        max_length=30,
        required=True,
    )

    def __init__(self, game):
        super().__init__()
        self.game = game

    async def on_submit(self, interaction: Interaction):
        word = self.word_input.value.strip().lower()

        if not word.isalpha():

            embed = discord.Embed(
                title="🚫 Invalid word",
                description="The Hangman word must contain letters only.",
                color=get_fail_colour(),
            )

            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        self.game.word = word
        self.game.set_word_button.disabled = True
        self.game.guess_word_button.disabled = False
        embed = self.game.get_embed()

        await interaction.response.edit_message(embed=embed, view=self.game)


class HangmanGuessModal(discord.ui.Modal, title="Guess a letter"):
    guess_input = discord.ui.TextInput(
        label="Your guess",
        placeholder="Enter one letter...",
        min_length=1,
        max_length=1,
        required=True,
    )

    def __init__(self, game):
        super().__init__()

        self.game = game

    async def on_submit(self, interaction: Interaction):

        if self.game.finished:
            embed = discord.Embed(
                title="🚫 Hangman has ended!",
                description="This game is already finished.",
                color=get_fail_colour(),
            )

            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        guess = self.guess_input.value.strip().lower()
        if not guess.isalpha():
            embed = discord.Embed(
                title="🚫 Invalid guess",
                description="Your guess must be a letter.",
                color=get_fail_colour(),
            )

            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if guess in self.game.guessed_letters or guess in self.game.wrong_letters:
            embed = discord.Embed(
                title="🚫 Already guessed",
                description=f"The letter {guess} has already been guessed.",
                color=get_fail_colour(),
            )

            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if guess in self.game.word:
            self.game.guessed_letters.append(guess)
        else:
            self.game.wrong_letters.append(guess)
            self.game.remaining_attempts -= 1

        if all(letter in self.game.guessed_letters for letter in self.game.word):
            self.game.finished = True
            self.game.set_word_button.disabled = True
            self.game.guess_word_button.disabled = True

            embed = self.game.get_embed()
            embed.title = "Hangman — You won! 🎉"
            embed.description += f"\n\n*You found the word* **{self.game.word}**!"
            embed.color = get_success_colour()
            embed.set_footer(
                text=f"Guessed by {interaction.user.display_name} • Congratulations! 🎉"
            )

            await interaction.response.edit_message(embed=embed, view=self.game)
            return

        if self.game.remaining_attempts <= 0:
            self.game.finished = True
            self.game.set_word_button.disabled = True
            self.game.guess_word_button.disabled = True

            embed = self.game.get_embed()
            embed.title = "Hangman — Game over 💀"
            embed.description += f"\n\nThe word was {self.game.word}."
            embed.color = get_fail_colour()
            embed.set_footer(
                text=f"Game over • Last guess by {interaction.user.display_name}"
            )

            await interaction.response.edit_message(embed=embed, view=self.game)

            return

        await interaction.response.edit_message(
            embed=self.game.get_embed(), view=self.game
        )
        
class Games(commands.GroupCog, group_name="games"):
    def __init__(self, bot):
        self.bot = bot

    group_1 = app_commands.Group(
        name="1",
        description="Games - page 1"
    )

    @group_1.command(
        name="wordle",
        description="Start a random wordle."
    )
    async def wordle(
        self,
        interaction: Interaction
    ):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://api.pxsl.dev/wordle.txt"
                ) as response:
                    response.raise_for_status()
                    text = await response.text()

            words = {
                word.strip().lower()
                for word in text.splitlines()
                if len(word.strip()) == 5
                and word.strip().isalpha()
            }

            if not words:
                raise ValueError(
                    "No valid five-letter words were found."
                )

            chosen = random.choice(list(words))

        except Exception as e:
            print(
                f"[Wordle] Failed to retrieve word list: "
                f"{type(e).__name__}: {e}"
            )

            embed = discord.Embed(
                title="🚫 Couldn't start Wordle",
                description=(
                    "I couldn't retrieve the Wordle word list right now.\n"
                    "Please try again in a moment."
                ),
                color=get_fail_colour()
            )

            await interaction.response.send_message(
                embed=embed
            )

            return

        game = WordleView(
            interaction.user.id,
            chosen,
            words
        )

        embed = game.get_embed()

        embed.description = (
            "Guess the **5-letter word**!\n\n"
            f"```text\n{game.get_grid()}\n```\n"
            "🟩 Correct letter and position\n"
            "🟨 Correct letter, wrong position\n"
            "⬛ Letter isn't in the word"
        )

        embed.set_author(
            name=interaction.user.display_name,
            icon_url=interaction.user.display_avatar.url
        )

        await interaction.response.send_message(
            embed=embed,
            view=game
        )


    @app_commands.command(
        name="hangman",
        description="Start a Hangman game."
    )
    async def hangman(
        self,
        interaction: Interaction
    ):
        game = HangmanView(interaction.user.id)
        embed = game.get_embed()
        embed.set_author(
            name=interaction.user.display_name,
            icon_url=interaction.user.display_avatar.url
        )
        await interaction.response.send_message(
            embed=embed,
            view=game
        )

async def setup(bot):
    await bot.add_cog(Games(bot))