import os
import discord
from discord.ext import commands, tasks
import asyncio
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

load_dotenv() 
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.voice_states = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"강퇴하는 용우가 준비되었습니다!")

@bot.command()
async def 타이머(ctx, 시간: int):
    """지정된 시간이 지난 후 음성 채널에서 모든 사용자를 내보냅니다."""
    if not ctx.author.voice:
        await ctx.send("음성 채널에 먼저 접속하세요!")
        return

    voice_channel = ctx.author.voice.channel
    await ctx.send(f"⏳ {시간}분 타이머가 설정되었습니다! 시간이 끝나면 {voice_channel.name} 채널에서 모든 사용자를 내보냅니다.")

    # 1분 전 알림 (설정한 시간이 1분 이상일 때만)
    if 시간 > 1:
        await asyncio.sleep((시간 - 1) * 60)  # (시간 - 1)분 대기
        await ctx.send(f"⚠️ 1분 후 {voice_channel.name} 채널의 모든 사용자가 강퇴됩니다!")

    # 30초 전 알림
    await asyncio.sleep(30)  # 30초 대기
    await ctx.send(f"⏳ 30초 후 {voice_channel.name} 채널의 모든 사용자가 강퇴됩니다!")

    # 남은 30초 대기 후 강제 퇴장
    await asyncio.sleep(30)

    # 음성 채널의 모든 멤버 연결 끊기
    if voice_channel.members:  # 채널에 사용자가 있는 경우
        for member in voice_channel.members:
            try:
                await member.move_to(None)  # 사용자를 음성 채널에서 내보냄
            except discord.Forbidden:
                await ctx.send(f"{member.name}를 내보낼 권한이 없습니다.")
        await ctx.send(f"{voice_channel.name} 채널의 모든 사용자를 내보냈습니다.")
    else:
        await ctx.send(f"{voice_channel.name} 채널에 사용자가 없습니다.")



app = Flask("")

@app.route("/")
def home():
    return "봇이 실행 중입니다."

def run():
    app.run(host="0.0.0.0", port=8000)

# Flask 서버를 별도의 스레드로 실행
Thread(target=run).start()


# bot.run(os.getenv("DISCORD_BOT_TOKEN"))
bot.run(os.environ.get("DISCORD_BOT_TOKEN"))