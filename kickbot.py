import os
import discord
from discord.ext import commands
import asyncio
from dotenv import load_dotenv
from flask import Flask
from threading import Thread
import static_ffmpeg

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

async def play_alarm(voice_client):
    """음성 채널에서 알람 소리를 재생하는 함수"""
    if not voice_client or not voice_client.is_connected():
        return

    # FFmpeg 실행 파일 경로 가져오기
    ffmpeg_path = static_ffmpeg.get_ffmpeg_path()

    # 알람 음원 재생
    audio_source = discord.FFmpegPCMAudio("alarm.mp3", executable=ffmpeg_path)
    if not voice_client.is_playing():
        voice_client.play(audio_source)

    await asyncio.sleep(3)  # 3초 동안 재생 후 종료

@bot.command()
async def 타이머(ctx, 시간: int):
    """지정된 시간이 지난 후 음성 채널에서 모든 사용자를 내보냅니다."""
    if not ctx.author.voice:
        await ctx.send("음성 채널에 먼저 접속하세요!")
        return

    voice_channel = ctx.author.voice.channel
    await ctx.send(f"⏳ {시간}분 타이머가 설정되었습니다! 시간이 끝나면 {voice_channel.name} 채널에서 모든 사용자를 내보냅니다.")

    # 봇이 음성 채널에 접속
    voice_client = await voice_channel.connect()

    # 1분 전 알람 (설정한 시간이 1분 이상일 때만)
    if 시간 > 1:
        await asyncio.sleep((시간 - 1) * 60)  # (시간 - 1)분 대기
        await ctx.send(f"⚠️ 1분 후 {voice_channel.name} 채널의 모든 사용자가 강퇴됩니다!")
        await play_alarm(voice_client)  # 알람 재생

    # 30초 전 알람
    await asyncio.sleep(30)  # 30초 대기
    await ctx.send(f"⏳ 30초 후 {voice_channel.name} 채널의 모든 사용자가 강퇴됩니다!")
    await play_alarm(voice_client)  # 알람 재생

    # 남은 30초 대기 후 강제 퇴장
    await asyncio.sleep(30)

    # 음성 채널의 모든 멤버 연결 끊기
    if voice_channel.members:
        for member in voice_channel.members:
            try:
                await member.move_to(None)  # 사용자를 음성 채널에서 내보냄
            except discord.Forbidden:
                await ctx.send(f"{member.name}을(를) 내보낼 권한이 없습니다.")
        await ctx.send(f"🚪 {voice_channel.name} 채널의 모든 사용자를 내보냈습니다.")

    # 봇이 음성 채널에서 나감
    await voice_client.disconnect()

# Flask 서버 설정 (Koyeb Health Check)
app = Flask("")

@app.route("/")
def home():
    print("Health check 요청을 받았습니다.")
    return "봇이 실행 중입니다.", 200

def run():
    print("Flask 서버가 시작되었습니다. 8000 포트를 열고 있습니다...")
    app.run(host="0.0.0.0", port=8000)

# Flask 서버를 별도의 스레드로 실행
Thread(target=run).start()

bot.run(os.getenv("DISCORD_BOT_TOKEN"))