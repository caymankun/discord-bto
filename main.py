import discord
from discord import app_commands
from discord.player import FFmpegPCMAudio
import os
import re
import requests
import subprocess
from gtts import gTTS
from pydub import AudioSegment

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

        await play_voice(content, message.guild)

@bot.event
async def on_voice_state_update(member, before, after):
    if member == bot.user:
        return

    if before.channel is None and after.channel is not None:
        # ユーザーがボイスチャンネルに参加した
        message = f"{member.display_name}がボイスチャンネルに参加しました。"
    elif before.channel is not None and after.channel is None:
        # ユーザーがボイスチャンネルから退出した
        message = f"{member.display_name}がボイスチャンネルから退出しました。"
    else:
        return

    # ボイスチャンネルにメッセージを送信
    voice_client = after.channel.guild.voice_client if after.channel else before.channel.guild.voice_client
    if voice_client:
        await play_voice(message, voice_client.guild)

    # もしボイスチャンネルにボット以外のメンバーがいない場合、ボットを切断
    voice_channel = before.channel if before.channel is not None else after.channel
    if voice_channel and len(voice_channel.members) == 1:
        voice_client = voice_channel.guild.voice_client
        if voice_client:
            await voice_client.disconnect()

async def play_voice(textcontent, guild):
    # Text to speech using gTTS and save as MP3
    print(textcontent)
    tts = gTTS(textcontent, lang='ja')
    tts.save('out.mp3')

    # Convert MP3 to WAV using pydub
    sound = AudioSegment.from_mp3('out.mp3')
    sound.export('out.wav', format='wav')

    # Get voice client
    voice_client = guild.voice_client
    if voice_client:
        # Play WAV file in the voice channel
        voice_client.play(FFmpegPCMAudio('out.wav'))
    else:
        await guild.text_channels[0].send('ボイスチャンネルに接続していません。')


bot.run(TOKEN)
