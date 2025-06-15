from discord.ext import commands
import discord
import yt_dlp
import asyncio
import re

ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': False,
    'nocheckcertificate': True,
    'ignoreerrors': True,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'ytsearch',
    'source_address': '0.0.0.0',
    'cookiefile': 'cookies.txt',
}


ffmpeg_opts = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

def format_duration(seconds):
    if seconds is None:
        return ""
    minutes, seconds = divmod(int(seconds), 60)
    return f"{minutes:02}:{seconds:02}"

def extract_stream_url(info):
    if info.get("url"):
        return info["url"]
    for f in info.get("formats", []):
        if f.get("url"):
            return f["url"]
    return None

def play_audio(ctx, url):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()

    audio = discord.FFmpegPCMAudio(url, **ffmpeg_opts)
    source = discord.PCMVolumeTransformer(audio)

    def after_playing(error):
        if error:
            print(f"🔴 FFmpeg lỗi khi phát: {error}")
            coro = ctx.send("❌ Không thể phát bài này do lỗi ffmpeg.")
            asyncio.run_coroutine_threadsafe(coro, ctx.bot.loop)

    ctx.voice_client.play(source, after=after_playing)

# ---- COG MUSIC ----
class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="join")
    async def join(self, ctx):
        if ctx.author.voice:
            await ctx.author.voice.channel.connect()
            await ctx.send(f"📻 Entered channel {ctx.author.voice.channel.name}")
        else:
            await ctx.send("❌ Bạn không ở kênh thoại nào cả.")

    @commands.command(name="leave")
    async def leave(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.send("📴 Left the voice channel.")
        else:
            await ctx.send("❌ Bot is not in voice channel.")

    @commands.command(name="pause")
    async def pause(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.send("⏸️ Music paused.")
        else:
            await ctx.send("❌ No music is playing.")

    @commands.command(name="resume")
    async def resume(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send("▶️ Music playback resumed.")
        else:
            await ctx.send("❌ No music is paused.")

    @commands.command(name="stop")
    async def stop(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send("⏹️ Music stopped.")
        else:
            await ctx.send("❌ No music is playing.")

    @commands.command(name="play")
    async def play(self, ctx, *, search: str):
        await self.handle_play(ctx, search)

    async def handle_play(self, ctx, search: str):
        if not ctx.voice_client:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("❌ Bạn không ở kênh thoại nào cả.")
                return

        youtube_url_pattern = r"(https?://)?(www\.)?(youtube\.com|youtu\.be|music\.youtube\.com)/"
        loop = asyncio.get_event_loop()

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                def get_info():
                    if re.match(youtube_url_pattern, search):
                        return ydl.extract_info(search, download=False)
                    else:
                        return ydl.extract_info(f"ytsearch5:{search}", download=False)

                initial_message = await ctx.send(f"🔍 Searching `{search}`...")
                info = await loop.run_in_executor(None, get_info)

                if "entries" in info and info["entries"]:
                    entries = info["entries"]
                    main_content = "**🤔 Choose a song:**\n"
                    for i, entry in enumerate(entries, start=1):
                        duration_str = format_duration(entry.get('duration'))
                        main_content += f"`{i}.` {entry.get('title', 'No title')} `[{duration_str}]`\n"

                    timeout_seconds = 30
                    full_message = main_content + f"\n*Enter a number to select. The order will expire after **{timeout_seconds}** seconds.*"
                    await initial_message.edit(content=full_message)

                    wait_for_message_task = asyncio.create_task(
                        self.bot.wait_for(
                            "message",
                            check=lambda m: m.author == ctx.author and m.channel == ctx.channel and m.content.isdigit() and 1 <= int(m.content) <= len(entries),
                            timeout=timeout_seconds
                        )
                    )

                    async def update_timer():
                        for i in range(timeout_seconds - 1, 0, -1):
                            await asyncio.sleep(1)
                            new_content = main_content + f"\n*Enter a number to select. The order will expire after **{i}** seconds.*"
                            if wait_for_message_task.done():
                                break
                            try:
                                await initial_message.edit(content=new_content)
                            except discord.errors.NotFound:
                                break

                    update_timer_task = asyncio.create_task(update_timer())
                    done, pending = await asyncio.wait(
                        {wait_for_message_task, update_timer_task},
                        return_when=asyncio.FIRST_COMPLETED
                    )

                    for task in pending:
                        task.cancel()

                    if wait_for_message_task in done:
                        try:
                            user_msg = wait_for_message_task.result()
                            chosen_entry = entries[int(user_msg.content) - 1]
                            await initial_message.edit(content=f"✅ Đã chọn: **{chosen_entry.get('title')}**\n*Preparing to play...*")

                            def get_chosen_info():
                                return ydl.extract_info(chosen_entry["webpage_url"], download=False)

                            stream_info = await loop.run_in_executor(None, get_chosen_info)
                            stream_url = extract_stream_url(stream_info)

                            if not stream_url:
                                await ctx.send("❌ Cannot get URL to play music.")
                                return

                            play_audio(ctx, stream_url)
                            await ctx.send(f"🎧 Now playing: **{stream_info.get('title', 'No name')}**")
                        except Exception as e:
                            print(f"Error while selecting song: {e}")
                            await ctx.send("❌ An error occurred while selecting a song..")
                    else:
                        await initial_message.edit(content="⌛ Time's up. Selection period ended.")
                elif "entries" not in info:
                    stream_url = extract_stream_url(info)
                    if not stream_url:
                        await initial_message.edit(content="❌ URL not found to play from this link.")
                        return
                    play_audio(ctx, stream_url)
                    await initial_message.delete()
                    await ctx.send(f"🎧 Đang phát: **{info.get('title', 'No name')}**")
                else:
                    await initial_message.edit(content="❌ No results found.")
        except Exception as e:
            print(f"Error in handle_play: {e}")
            try:
                await initial_message.edit(content="❌ An unexpected error occurred..")
            except:
                await ctx.send("❌ An unexpected error occurred.")


async def setup(bot):
    await bot.add_cog(Music(bot))