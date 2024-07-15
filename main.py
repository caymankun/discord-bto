import discord
import requests
from discord import app_commands
from discord.player import FFmpegPCMAudio
import os
import re

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
async def connect(interaction: discord.Interaction, user: discord.User):
    if user.voice:
        voice_channel = await user.voice.channel.connect()
        await interaction.response.send_message(f'{user.name}さんのボイスチャンネルに接続しました。')
    else:
        await interaction.response.send_message('ボイスチャンネルに接続していません。')

@tree.command(name='disconnect', description='ボットをボイスチャンネルから切断します')
async def disconnect(interaction: discord.Interaction, user: discord.User):
    voice_client = user.guild.voice_client
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
        if message.author.voice:
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

        # ネタばれコンテンツを置き換える
        content = re.sub(r'ネタばれコンテンツ', 'ネタばれコンテンツ', content)

        await play_voice(content, message.guild)

async def play_voice(text, guild):
    # APIのURLとテキストを組み合わせてリクエストを送信
    url = f"https://apis.caymankun.f5.si/tts/speach.php?text={text}"
    response = requests.get(url)
    
    if response.status_code == 200:
        # レスポンスから音声ファイルを取得し、一時ファイルとして保存
        with open("out.wav", "wb") as f:
            f.write(response.content)
        
        # Discordのボイスチャンネルで再生
        voice_client = guild.voice_client
        if voice_client:
            voice_client.play(FFmpegPCMAudio("out.wav"))
        else:
            print('ボイスチャンネルに接続していません。音声を再生できません。')

    else:
        print(f"Failed to fetch voice from API. Status code: {response.status_code}")

bot.run(TOKEN)
