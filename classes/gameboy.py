from __future__ import annotations

import asyncio
from typing import Optional

import io
import logging
import pathlib

import discord
import pyboy
from discord.enums import Enum
from discord.ext import commands
from ditto import CONFIG, BotBase, Cog, Context
from ditto.types import User

from PIL import Image

# Ignore RTC Warnings
logging.getLogger("pyboy.core.cartridge.mbc3").setLevel(logging.ERROR)


COG_CONFIG = CONFIG.EXTENSIONS[__name__]


HOLD_DURATION = 10
TICKS = 300

ROOT_DIR = pathlib.Path("./res/secret/gb")
SAVE_DIR = ROOT_DIR / "states"


class Button(Enum):
    SAVE = pyboy.WindowEvent.STATE_SAVE
    LOAD = pyboy.WindowEvent.STATE_LOAD
    REFRESH = pyboy.WindowEvent.PASS
    POWER = pyboy.WindowEvent.QUIT
    A = pyboy.WindowEvent.PRESS_BUTTON_A
    B = pyboy.WindowEvent.PRESS_BUTTON_B
    UP = pyboy.WindowEvent.PRESS_ARROW_UP
    DOWN = pyboy.WindowEvent.PRESS_ARROW_DOWN
    LEFT = pyboy.WindowEvent.PRESS_ARROW_LEFT
    RIGHT = pyboy.WindowEvent.PRESS_ARROW_RIGHT
    START = pyboy.WindowEvent.PRESS_BUTTON_START
    SELECT = pyboy.WindowEvent.PRESS_BUTTON_SELECT


INVERSE_BUTTON: dict[Button, int] = {
    Button.A: pyboy.WindowEvent.RELEASE_BUTTON_A,
    Button.B: pyboy.WindowEvent.RELEASE_BUTTON_B,
    Button.UP: pyboy.WindowEvent.RELEASE_ARROW_UP,
    Button.DOWN: pyboy.WindowEvent.RELEASE_ARROW_DOWN,
    Button.LEFT: pyboy.WindowEvent.RELEASE_ARROW_LEFT,
    Button.RIGHT: pyboy.WindowEvent.RELEASE_ARROW_RIGHT,
    Button.START: pyboy.WindowEvent.RELEASE_BUTTON_START,
    Button.SELECT: pyboy.WindowEvent.RELEASE_BUTTON_SELECT,
}


BUTTON_TEXT: dict[Button, str] = {
    Button.SAVE: "Save",
    Button.LOAD: "Load",
    Button.REFRESH: "⟳",
    Button.POWER: "╳",
    Button.A: "A",
    Button.B: "B",
    Button.UP: "↑",
    Button.DOWN: "↓",
    Button.LEFT: "←",
    Button.RIGHT: "→",
    Button.START: "Start",
    Button.SELECT: "Select",
}

BUTTON_COLOR: dict[Button, discord.ButtonStyle] = {
    Button.SAVE: discord.ButtonStyle.success,
    Button.LOAD: discord.ButtonStyle.danger,
    Button.REFRESH: discord.ButtonStyle.primary,
    Button.POWER: discord.ButtonStyle.danger,
    Button.A: discord.ButtonStyle.danger,
    Button.B: discord.ButtonStyle.danger,
    Button.UP: discord.ButtonStyle.primary,
    Button.DOWN: discord.ButtonStyle.primary,
    Button.LEFT: discord.ButtonStyle.primary,
    Button.RIGHT: discord.ButtonStyle.primary,
    Button.START: discord.ButtonStyle.secondary,
    Button.SELECT: discord.ButtonStyle.secondary,
}

BUTTON_MAP: list[list[Optional[Button]]] = [
    [Button.SAVE, Button.LOAD, None, Button.REFRESH, Button.POWER],
    [None, Button.UP, None, None, None],
    [Button.LEFT, None, Button.RIGHT, None, Button.A],
    [None, Button.DOWN, None, Button.B, None],
    [None, Button.SELECT, None, Button.START, None],
]


class UIButton(discord.ui.Button["GameBoyView"]):
    def __init__(self, button: Button, group: int):
        self.button = button
        super().__init__(style=BUTTON_COLOR[self.button], label=BUTTON_TEXT[self.button], group=group)

    async def callback(self, interaction: discord.Interaction):
        async with self.view.lock:
            await self.view.press(self.button)
            await self.view.tick()

            image_url = await self.view.render()
            await interaction.response.edit_message(embed=self.view.embed.set_image(url=image_url))


class SaveButton(UIButton):
    async def callback(self, interaction: discord.Interaction):
        with open(self.view.save_dir / f"{self.view.user.id}.state", "wb") as fp:
            self.view.game.save_state(fp)
        await super().callback(interaction)


class LoadButton(UIButton):
    async def callback(self, interaction: discord.Interaction):
        try:
            with open(
                f"res/secret/gb_states/{self.view.game.cartridge_title()}/{self.view.user.id}.state", "rb"
            ) as fp:
                self.view.game.load_state(fp)
        except FileNotFoundError:
            await interaction.response.send_message("You do not have a save-state.", ephemeral=True)
        await super().callback(interaction)


class PowerButton(UIButton):
    async def callback(self, interaction: discord.Interaction):
        for button in self.view.children:
            button.disabled = True

        self.view.cog.game = None

        await interaction.response.edit_message(content="Game Over!", view=self.view)


class UIBlank(discord.ui.Button["GameBoyView"]):
    def __init__(self, group: int):
        super().__init__(style=discord.ButtonStyle.secondary, label="\u200b", disabled=True, group=group)


class GameBoyView(discord.ui.View):
    children: list[UIButton]

    def __init__(self, cog: GameBoy, game: str, user: User):
        self.cog = cog
        self.user = user
        self.lock = asyncio.Lock()

        self.prev_message = None

        super().__init__(timeout=None)

        self.game = pyboy.PyBoy(
            game,
            window_type="headless",
        )
        self.game.set_emulation_speed(0)

        self.save_dir: pathlib.Path = SAVE_DIR / self.game.cartridge_title()
        self.save_dir.mkdir(exist_ok=True)

        for group, row in enumerate(BUTTON_MAP):
            for button in row:
                if button is None:
                    self.add_item(UIBlank(group))
                elif button is Button.POWER:
                    self.add_item(PowerButton(button, group))
                elif button is Button.SAVE:
                    self.add_item(SaveButton(button, group))
                elif button is Button.LOAD:
                    self.add_item(LoadButton(button, group))
                else:
                    self.add_item(UIButton(button, group))

    @property
    def embed(self) -> discord.Embed:
        return (
            discord.Embed()
            .set_author(name=f"{self.user}'s Gameboy", icon_url=self.user.avatar.url)
            .set_footer(text=f"Playing {self.game.cartridge_title()}")
        )

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if self.lock.locked():
            await interaction.response.send_message("Input disabled", ephemeral=True)
            return False

        if interaction.user != self.user:
            await interaction.response.send_message("This is not your game", ephemeral=True)

        return True

    async def press(self, button: Button):
        self.game.send_input(button.value)
        await self.tick(HOLD_DURATION)
        self.game.send_input(INVERSE_BUTTON.get(button, pyboy.WindowEvent.PASS))

    async def tick(self, n: int = TICKS):
        def run_game():
            for _ in range(n):
                self.game.tick()

        await self.cog.bot.loop.run_in_executor(None, run_game)

    async def render(self) -> str:
        if self.prev_message is not None:
            await self.prev_message.delete()

        frame = io.BytesIO()
        screen = self.game.botsupport_manager().screen()
        screen.screen_image().resize((160 * 4, 144 * 4), resample=Image.LANCZOS).save(frame, "PNG")
        frame.seek(0)

        self.prev_message = await COG_CONFIG.RENDER_CHANNEL.send(file=discord.File(frame, "frame.png"))
        return self.prev_message.attachments[0].url


class GameBoy(Cog):
    def __init__(self, bot: BotBase) -> None:
        super().__init__(bot)
        self.game = None

    @commands.command(aliases=["gb", "pokemon", "pkmn"])
    async def gameboy(self, ctx: Context, *, game_name: str = "red") -> None:  # type: ignore
        if self.game is not None:
            raise commands.BadArgument("You are already playing!")

        game = ROOT_DIR / f"{game_name}.gb"
        if not game.exists():
            game = ROOT_DIR / f"{game_name}.gbc"
            if not game.exists():
                raise commands.BadArgument(f"{game_name} is not a game!")

        async with ctx.typing():
            self.game = GameBoyView(self, str(game), ctx.author)
            image_url = await self.game.render()
            await ctx.send(embed=self.game.embed.set_image(url=image_url), view=self.game)  # type: ignore


def setup(bot: BotBase) -> None:
    bot.add_cog(GameBoy(bot))