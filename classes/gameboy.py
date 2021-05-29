import asyncio

import discord
import pyboy
from discord.ext import commands
from pyboy import PyBoy
import os
from constants import emojis
import threading, queue


class GameBoy:
    def __init__(self, rom, channel, user, loop):
        self.loop = loop
        self.user = user
        self.channel = channel
        self.rom = rom
        self.done = False
        self.q = queue.Queue()
        self.counter = 0
        self.pyboy: PyBoy = None
        self.e = discord.Embed = None

    async def start_emulator(self, ctx: commands.Context):
        message: discord.Message = await ctx.reply(f"Starting the emulator {emojis.loading}")
        t1 = threading.Thread(target=self.emulator_start)
        t1.start()
        await message.edit(content=f"Emulator started")
        message = await ctx.reply("This is your message, you play here")
        self.e = discord.Embed()
        t2 = threading.Thread(target=self.get_frame, args=(message,))
        t2.start()


    def emulator_start(self):
        self.pyboy = PyBoy(self.rom, disable_renderer=True)
        while True:
            try:
                item = self.q.get(block=False)
                self.pyboy.send_input(item)
            except queue.Empty:
                pass

            if self.pyboy.tick() or self.done:
                self.pyboy.stop(False)
                self.done = True
                os.system("rm data/gameboy/images/*")
                return

    def comms(self, item):
        self.q.put(item, block=False)

    async def get_frame(self, message):
        while not self.done:
            pyboy.botsupport_manager().screen().screen_image().save(f'data/gameboy/images/{self.counter}.png')
            file = discord.File(f'data/gameboy/images/{self.counter}.png')
            self.e.set_image(url=f"attachments://{self.counter}.png")
            self.counter += 1
            await message.edit(file=file, embed=self.e)
            await asyncio.sleep(0.5)

