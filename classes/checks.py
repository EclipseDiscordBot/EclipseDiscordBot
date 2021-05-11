import discord


def created_at(mem: discord.User):
    return mem.created_at


def bot(m):
    return m.author.bot


def author_channel(ctx):
    def chek(m):
        return m.author == ctx.author and m.channel.id == ctx.channel.id

    return chek


def keyword(keyword_msg):
    def check(m):
        return keyword_msg.content in m.content

    return check

