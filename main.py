import discord
from discord import app_commands
from discord.player import FFmpegPCMAudio
import os
import re
import requests
import subprocess
from pydub import AudioSegment
import yt_dlp

TOKEN = os.getenv('TOKEN')

intents = discord.Intents.all()
intents.voice_states = True  # ボイスチャンネルの状態トラッキングが必要な場合に設定

bot = discord.Client(intents=intents)   # プレフィックスを '/' に設定
tree = app_commands.CommandTree(bot)

@bot.event
async def on_ready():
    print('サービス起動しました。')
    await tree.sync()

@tree.command(name='connect', description='ボットをボイスチャンネルに接続します')
async def connect(interaction: discord.Interaction):
    if interaction.user.voice:  # interactionから相互作用を発生させたユーザーを取得し、そのメンバーがボイスチャンネルに接続しているか確認します
        voice_channel = await interaction.user.voice.channel.connect()
        await interaction.response.send_message(f'ボイスチャンネルに接続しました。')
    else:
        await interaction.response.send_message('ボイスチャンネルに接続していません。')

@tree.command(name='disconnect', description='ボットをボイスチャンネルから切断します')
async def disconnect(interaction: discord.Interaction):
    voice_client = interaction.guild.voice_client
    if voice_client:
        await voice_client.disconnect()
        await interaction.response.send_message('ボイスチャンネルから切断しました。')
    else:
        await interaction.response.send_message('ボイスチャンネルに接続していません。')

@tree.command(name='play', description='URLから音楽を再生します')
async def play(interaction: discord.Interaction, url: str):
    voice_client = interaction.guild.voice_client
    if voice_client:
        url = convert_playlist_url_to_video_url(url)
        await interaction.response.send_message(f'{url}から音楽を再生します。')
        await download_and_play(url, interaction.guild)
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
            await message.channel.send(f'{url}から音楽を再生します。')
            await download_and_play(url, message.guild)
        else:
            await message.channel.send('ボイスチャンネルに接続していません。')

def convert_playlist_url_to_video_url(url):
    # プレイリストURLかどうかを確認し、動画URLに変換
    playlist_pattern = re.compile(r'(https://www\.youtube\.com/watch\?v=[^&]+)&list=[^&]+')
    match = playlist_pattern.match(url)
    if match:
        return match.group(1)
    return url

async def download_and_play(url, guild):
    
    ydl_opts = {
        "format": "mp3/bestaudio/best",
        'outtmpl': 'out.mp3',
        'noplaylist': True,  # プレイリストをダウンロードしない
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    
    # Convert MP3 to WAV using pydub
    sound = AudioSegment.from_mp3('out.mp3')
    sound.export('out.wav', format='wav')

    # Get voice client
    voice_client = guild.voice_client
    if voice_client:
        # Play WAV file in the voice channel
        voice_client.play(FFmpegPCMAudio('downloaded_audio.wav'))
    else:
        await guild.text_channels[0].send('ボイスチャンネルに接続していません。')


bot.run(TOKEN)
