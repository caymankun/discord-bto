import discord
import requests
from discord.player import FFmpegPCMAudio
import os

TOKEN = os.getenv('TOKEN')

intents = discord.Intents.default()
intents.voice_states = True  # ボイスチャンネルの状態トラッキングが必要な場合に設定

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print('サービス起動しました。')

@client.event
async def on_message(message):
    if message.author.bot:
        return
    
    if message.content.startswith('/play'):
        text = message.content[len('/play'):].strip()
        await play_voice(text, message.channel)
    
    elif message.content == '/connect':
        if message.author.voice:
            voice_channel = await message.author.voice.channel.connect()
            await message.channel.send('ボイスチャンネルに接続しました。')
        else:
            await message.channel.send('ボイスチャンネルに接続していません。')
    
    elif message.content == '/disconnect':
        voice_client = message.guild.voice_client
        if voice_client:
            await voice_client.disconnect()
            await message.channel.send('ボイスチャンネルから切断しました。')
        else:
            await message.channel.send('ボイスチャンネルに接続していません。')

async def play_voice(text, text_channel):
    # APIのURLとテキストを組み合わせてリクエストを送信
    url = f"https://apis.caymankun.f5.si/tts/speach.php?text={text}"
    response = requests.get(url)
    
    if response.status_code == 200:
        # レスポンスから音声ファイルを取得し、一時ファイルとして保存
        with open("out.wav", "wb") as f:
            f.write(response.content)
        
        # Discordのボイスチャンネルで再生
        voice_client = text_channel.guild.voice_client
        if voice_client:
            voice_client.play(FFmpegPCMAudio("out.wav"))
        else:
            await text_channel.send('ボイスチャンネルに接続していません。音声を再生できません。')

    else:
        print(f"Failed to fetch voice from API. Status code: {response.status_code}")

client.run(TOKEN)
