import discord
import requests
from discord.channel import VoiceChannel
from discord.player import FFmpegPCMAudio
import os

TOKEN = os.getenv('TOKEN')
client = discord.Client()

voiceChannel: VoiceChannel 

intents = discord.Intents.default()
intents.voice_states = True  # ボイスチャンネルの状態トラッキングが必要な場合に設定

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print('サービス起動。')

@client.event
async def on_message(message):
    global voiceChannel

    if message.author.bot:
        return
    if message.content == '/connect':
        voiceChannel = await VoiceChannel.connect(message.author.voice.channel)
        await message.channel.send('入出しました。')
        return
    elif message.content == '/disconnect':
        voiceChannel.stop()
        await message.channel.send('退出しました。')
        await voiceChannel.disconnect()
        return

    play_voice(message.content)

def play_voice(text):
    # APIのURLとテキストを組み合わせてリクエストを送信
    url = f"https://apis.caymankun.f5.si/tts/speach.php?text={text}"
    response = requests.get(url)
    
    if response.status_code == 200:
        # レスポンスから音声ファイルを取得し、一時ファイルとして保存
        with open("out.wav", "wb") as f:
            f.write(response.content)
        
        # MP3をDiscordのボイスチャンネルで再生
        voiceChannel.play(FFmpegPCMAudio("out.wav"))

    else:
        print(f"Failed to fetch voice from API. Status code: {response.status_code}")

client.run(TOKEN)
