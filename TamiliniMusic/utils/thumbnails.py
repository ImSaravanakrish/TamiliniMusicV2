import os
import re
import random

import aiofiles
import aiohttp
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
from unidecode import unidecode
from youtubesearchpython.__future__ import VideosSearch

from TamiliniMusic import app
from config import YOUTUBE_IMG_URL


def changeImageSize(maxWidth, maxHeight, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    newWidth = int(widthRatio * image.size[0])
    newHeight = int(heightRatio * image.size[1])
    newImage = image.resize((newWidth, newHeight))
    return newImage


def clear(text):
    list = text.split(" ")
    title = ""
    for i in list:
        if len(title) + len(i) < 60:
            title += " " + i
    return title.strip()


async def get_thumb(videoid):
    if os.path.isfile(f"cache/{videoid}.png"):
        return f"cache/{videoid}.png"

    url = f"https://www.youtube.com/watch?v={videoid}"
    try:
        results = VideosSearch(url, limit=1)
        for result in (await results.next())["result"]:
            try:
                title = result["title"]
                title = re.sub("\W+", " ", title)
                title = title.title()
            except:
                title = "Unsupported Title"
            try:
                duration = result["duration"]
            except:
                duration = "Unknown Mins"
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            try:
                views = result["viewCount"]["short"]
            except:
                views = "Unknown Views"
            try:
                channel = result["channel"]["name"]
            except:
                channel = "Unknown Channel"

        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status == 200:
                    f = await aiofiles.open(f"cache/thumb{videoid}.png", mode="wb")
                    await f.write(await resp.read())
                    await f.close()

        youtube = Image.open(f"cache/thumb{videoid}.png")
        image1 = changeImageSize(1280, 720, youtube)
        image2 = image1.convert("RGBA")
        background = image2.filter(filter=ImageFilter.BoxBlur(10))
        enhancer = ImageEnhance.Brightness(background)
        background = enhancer.enhance(0.5)
        draw = ImageDraw.Draw(background)
        arial = ImageFont.truetype("TamiliniMusic/assets/font2.ttf", 30)
        font = ImageFont.truetype("TamiliniMusic/assets/font.ttf", 30)
        font2 = ImageFont.truetype("TamiliniMusic/assets/font.ttf", 60)
        draw.text((1110, 8), unidecode(app.name), fill="white", font=font2)
        draw.text(
            (55, 560),
            f"{channel} | {views[:23]}",
            (255, 255, 255),
            font=arial,
        )
        draw.text(
            (57, 600),
            clear(title),
            (255, 255, 255),
            font=font,
        )
        draw.line(
            [(55, 660), (1220, 660)],
            fill="white",
            width=5,
            joint="curve",
        )
        draw.ellipse(
            [(918, 648), (942, 672)],
            outline="white",
            fill="white",
            width=15,
        )
        draw.text(
            (36, 685),
            "00:00",
            (255, 255, 255),
            font=arial,
        )
        draw.text(
            (1185, 685),
            f"{duration[:23]}",
            (255, 255, 255),
            font=arial,
        )
        try:
            os.remove(f"cache/thumb{videoid}.png")
        except:
            pass
        background.save(f"cache/{videoid}.png")
        return f"cache/{videoid}.png"
    except Exception as e:
        print(e)
        return YOUTUBE_IMG_URL



async def gen_thumb(thumbnail, title, videoid, theme, ctitle):
    async with aiohttp.ClientSession() as session:
        async with session.get(thumbnail) as resp:
            if resp.status == 200:
                f = await aiofiles.open(f"cache/thumb{videoid}.jpg", mode="wb")
                await f.write(await resp.read())
                await f.close()
    image1 = Image.open(f"cache/thumb{videoid}.jpg")
    image2 = Image.open(f"Utils/{theme}.PNG")
    image3 = changeImageSize(1280, 720, image1)
    image4 = changeImageSize(1280, 720, image2)
    image5 = image3.convert("RGBA")
    image6 = image4.convert("RGBA")
    Image.alpha_composite(image5, image6).save(f"cache/temp{videoid}.png")
    img = Image.open(f"cache/temp{videoid}.png")
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("TamiliniMusic/assets/font", 85)
    font2 = ImageFont.truetype("TamiliniMusic/assets/font", 60)
    draw.text(
        (20, 45),
        f"Playing on: {ctitle[:14]}...",
        fill="white",
        stroke_width=1,
        stroke_fill="white",
        font=font2,
    )
    draw.text(
        (25, 595),
        f"{title[:27]}...",
        fill="white",
        stroke_width=2,
        stroke_fill="white",
        font=font,
    )
    img.save(f"cache/final{videoid}.png")
    os.remove(f"cache/temp{videoid}.png")
    os.remove(f"cache/thumb{videoid}.jpg")
    final = f"cache/final{videoid}.png"
    return final
