# SOMID | Social Media Downloader
SOMID, or by it's full name, Social Media Middleman, is a small Telegram bot wrote in python with the sole purpose to download videos and pictures from social media and send it back to the user.

![](https://github.com/doncezart/somid/blob/main/preview.gif)

## How to install
1. Download the latest version of [Python](https://www.python.org/downloads/) and install it.
2. OPTIONAL: Create a [virtual environment](https://docs.python.org/3/library/venv.html). This will isolate the project from the rest of your machine.
3. Install requirements via `pip install telegram tiktok_downloader instaloader`
4. Message `@BotFather` on Telegram and start the process of creating a Telegram bot
5. Create an `.env` file for the `BOT_TOKEN` you receive from BotFather
(Example: `BOT_TOKEN  =  '53223425:ASgdgsdf4SDFg4-3fdSDf4fSDf'`)
6. Start `main.py`

The bot will now run in an asynchronous environment. Keep the bot program open for as much as you want. If you want to run the bot in the background without keeping a program open manually, look into tmux, systemd or other ways.

## Types of media compatible
1. Instagram posts (video, photo or carousel) and reels
3. TikTok posts (video, photo or carousel, no watermark)

## To-Do List (media compatibility)
1. Instagram stories, profile pictures and full profile export
2. TikTok stories, sounds, collections, liked posts, reposts and full profile export
3. Youtube shorts and full-form videos
4. ...more

## Why Telegram?
I wanted a messaging platform, somewhere I can quickly send a message while browsing social media, as if I was just sharing a reel with a friend, and worry about the downloaded media later when I actually needed it. I had a few choices but ultimately ended up on Telegram. Discord had a low file-sharing limit compared to Telegram's 2GB/file. Whatsapp was also a choice, although I didn't like the fact that media would be locally stored on my phone which already constantly suffers from low storage. Messenger, Signal and other options were quickly eliminated because of their size and many weird quirks, so Telegram felt like the best choice.

## Disclaimer
I'm not responsible for your accounts or any restrictions that may appear. If you use this on your local network, don't spam it and I wouldn't recommend exposing your bot to the public. Social media platforms will notice that you're downloading dozens of media per minute and will impose restrictions. USE AT YOUR OWN RISK.

If you have questions or issues, you can reach me at my [website](https://ceza.ro) or on Discord & Telegram: @doncezart
