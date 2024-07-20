import discord
from discord import app_commands
from discord.player import FFmpegPCMAudio
import os
import re
import requests
import subprocess
from pydub import AudioSegment
from yt_dlp import YoutubeDL

TOKEN = os.getenv('TOKEN')

intents = discord.Intents.all()
intents.voice_states = True  # ボイスチャンネルの状態トラッキングが必要な場合に設定

bot = discord.Client(intents=intents)   # プレフィックスを '/' に設定
tree = app_commands.CommandTree(bot)

@bot.event
async def on_ready():
    print('サービス起動しました。')
    await tree.sync()

@tree.command(name='play', description='URLから音楽を再生します')
async def play(interaction: discord.Interaction, url: str):
    if interaction.user.voice:
        voice_channel = interaction.user.voice.channel
        voice_client = interaction.guild.voice_client

        if voice_client and voice_client.channel != voice_channel:
            await voice_client.disconnect()
            voice_client = await voice_channel.connect()
        elif not voice_client:
            voice_client = await voice_channel.connect()

        url = convert_playlist_url_to_video_url(url)
        await interaction.response.send_message(f'{url}から音楽を再生します。')
        await download_and_play(url, interaction.guild)
    else:
        await interaction.response.send_message('ボイスチャンネルに接続していません。')

@tree.command(name='stop', description='音楽を停止し、ボイスチャンネルから切断します')
async def stop(interaction: discord.Interaction):
    voice_client = interaction.guild.voice_client
    if voice_client:
        voice_client.stop()
        await voice_client.disconnect()
        await interaction.response.send_message('音楽を停止し、ボイスチャンネルから切断しました。')
    else:
        await interaction.response.send_message('ボイスチャンネルに接続していません。')

@bot.event
async def on_message(message):
    if message.author == bot.user:  # ボット自身のメッセージは無視
        return

    if message.content.startswith('/connect'):
        if message.author.voice:  # メッセージから送信者を取得し、そのメンバーがボイスチャンネルに接続しているか確認します
            voice_channel = await message.author.voice.channel.connect()
            await message.channel.send(f'ボイスチャンネルに接続しました。')
        else:
            await message.channel.send('ボイスチャンネルに接続していません。')

    elif message.content.startswith('/disconnect'):
        voice_client = message.guild.voice_client
        if voice_client:
            await voice_client.disconnect()
            await message.channel.send('ボイスチャンネルから切断しました。')
        else:
            await message.channel.send('ボイスチャンネルに接続していません。')

    elif message.content.startswith('/play'):
        voice_client = message.guild.voice_client
        if voice_client:
            url = message.content.split(' ')[1]
            url = convert_playlist_url_to_video_url(url)
            await message.channel.send(f'{url}')
            await download_and_play(url, message.guild)
        else:
            await message.channel.send('ボイスチャンネルに接続していません。')

def convert_playlist_url_to_video_url(url):
    playlist_pattern = re.compile(r'(https://www\.youtube\.com/watch\?v=[^&]+)&list=[^&]+')
    match = playlist_pattern.match(url)
    if match:
        return match.group(1)
    return url

async def download_and_play(url, guild):
    ydl_opts = {
        'format': 'worstaudio/worst',
        'outtmpl': 'downloaded_audio.%(ext)s',
        'noplaylist': True,
    }

    # 音声をダウンロード
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    # MP3ファイルを読み込み
    audio = AudioSegment.from_file('downloaded_audio.webm')  # 'webm'や他のフォーマットを確認

    # WAVファイルに変換して保存
    audio.export('downloaded_audio.wav', format='wav')

    voice_client = guild.voice_client
    if voice_client:
        voice_client.play(FFmpegPCMAudio('downloaded_audio.wav'))
    else:
        await guild.text_channels[0].send('ボイスチャンネルに接続していません。')

bot.run(TOKEN)
