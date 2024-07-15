import discord
from discord import app_commands
from discord.player import FFmpegPCMAudio
import os
import re
import requests
import subprocess

TOKEN = os.getenv('TOKEN')

intents = discord.Intents.default()
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

@bot.event
async def on_message(message):
    if message.author == bot.user:  # ボット自身のメッセージは無視
        return

    if message.content.startswith('/connect'):
        if message.author.voice:  # メッセージから送信者を取得し、そのメンバーがボイスチャンネルに接続しているか確認します
            voice_channel = await message.author.voice.channel.connect()
            await message.channel.send(f'{message.author.name}さんのボイスチャンネルに接続しました。')
        else:
            await message.channel.send('ボイスチャンネルに接続していません。')

    elif message.content.startswith('/disconnect'):
        voice_client = message.guild.voice_client
        if voice_client:
            await voice_client.disconnect()
            await message.channel.send('ボイスチャンネルから切断しました。')
        else:
            await message.channel.send('ボイスチャンネルに接続していません。')

    elif message.guild.voice_client:  # ボットがボイスチャンネルに接続している場合のみ処理
        content = message.content

        # URLを置き換える
        content = re.sub(r'https?://\S+', 'URL', content)

        # ||で囲まれたテキストを置き換える
        content = re.sub(r'\|\|([^|]+)\|\|', r'\1', content)

        await play_voice(content, message.guild)

async def play_voice(text, guild):
    # APIのURLとテキストを組み合わせてリクエストを送信
    url = f"https://apis.caymankun.f5.si/tts/speach.php?text={text}"
    response = requests.get(url)
    
    if response.status_code == 200:
        # Save MP3 to a temporary file
        with open("out.mp3", "wb") as f:
            f.write(response.content)
        
        # Convert MP3 to Opus using FFmpeg (ensure FFmpeg is installed in your environment)
        subprocess.run(['ffmpeg', '-i', 'out.mp3', '-y', '-vn', '-ar', '48000', '-ac', '2', '-b:a', '192k', 'out.opus'])

        # Get the voice client of the command invoker
        voice_client = ctx.author.voice.channel.guild.voice_client
        
        if voice_client:
            # Play the Opus file in the voice channel
            voice_client.play(FFmpegPCMAudio('out.opus'))
        else:
            await ctx.send('ボイスチャンネルに接続していません。')

    else:
        await ctx.send(f"Failed to fetch voice from API. Status code: {response.status_code}")

bot.run(TOKEN)
