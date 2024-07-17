import discord
from discord import app_commands
from discord.player import FFmpegPCMAudio
import os
import re
import requests
import subprocess
from gtts import gTTS

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

    elif message.guild.voice_client:
        content = message.content
        content = re.sub(r'https?://\S+', 'URL', content)
        content = re.sub(r'\|\|([^|]+)\|\|', r'\1', content)

        await play_voice(message.content, message.guild)

async def play_voice(textcontent, guild):
    # Text to speech using gTTS and save as WAV
    tts = gTTS(textcontent, lang='ja')
    tts.save('out.wav')

    # Get voice client
    voice_client = guild.voice_client
    if voice_client:
        # Play WAV file in the voice channel
        voice_client.play(FFmpegPCMAudio('out.wav'))
    else:
        await guild.text_channels[0].send('ボイスチャンネルに接続していません。')


bot.run(TOKEN)
