import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from PIL import Image, ImageFont, ImageDraw
import io
import re

load_dotenv()
bot = commands.Bot(command_prefix="+")


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


@bot.command()
async def info(ctx):
    await ctx.send("""Wanna pixelate some text? LOOK NO FURTHER
Source code: https://github.com/qxxxb/pixelator""")


@bot.command()
async def ping(ctx):
    await ctx.send("{:.0f} ms".format(bot.latency * 1000))


@bot.command()
async def pix(ctx, *, msg):
    if len(msg) > 128:
        await ctx.send("Your message is too long")
        return

    def clean_spoilers(msg):
        """
        Example:
        Input: "I like ||potatoes|| and ||beans||"
        Output:
            "I like potatoes and beans"
            (7, 13), (20, 25)
        """

        p = re.compile(r"\|\|.*?\|\|")
        unmatched = p.split(msg)
        matched = p.findall(msg)

        msg_cleaned = ""
        spoilers = []
        for i, segment in enumerate(matched):
            msg_cleaned += unmatched[i]
            start = len(msg_cleaned)
            segment = segment[2:-2]  # ||stuff|| -> stuff
            msg_cleaned += segment
            end = len(msg_cleaned)
            spoilers.append((start, end))

        msg_cleaned += unmatched[-1]
        return msg_cleaned, spoilers

    def render(msg):
        msg, spoilers = clean_spoilers(msg)

        # Render text
        char_size = (16, 32)  # (width, height)
        width = char_size[0] * len(msg)
        image = Image.new("RGBA", (width, char_size[1]), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        font = ImageFont.load("./ter-x32b.pil")  # Terminus 32px
        draw.text((0, 0), msg, font=font)

        # Pixelate spoilers
        for start, end in spoilers:
            box = (start * char_size[0], 0, end * char_size[0], char_size[1])
            ic = image.crop(box)

            # Pixelate by downscaling then upscaling
            small_size = (ic.size[0] // 8, ic.size[1] // 8)
            small = ic.resize(small_size, resample=Image.BOX)
            ic = small.resize(ic.size, Image.NEAREST)

            image.paste(ic, box)

        # Save image to buffer as png
        buf = io.BytesIO()
        image.save(buf, format="PNG")
        return io.BytesIO(buf.getvalue())

    try:
        async with ctx.typing():
            buf = render(msg)
        await ctx.send(file=discord.File(buf, "x.png"))
    except UnicodeEncodeError:
        await ctx.send("Couldn't render your stupid message")


bot.run(os.environ.get("DISCORD_TOKEN"))
