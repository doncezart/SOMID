from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram import Update, InputMediaPhoto, InputMediaVideo
from tiktok_downloader import snaptik
from dotenv import load_dotenv
from typing import List, Union
import instaloader
import logging
import re
import os

load_dotenv()
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class MediaHandler:
    def __init__(self):
        self.temp_dir = "temp_downloads"
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)
            
        self.instagram = instaloader.Instaloader(
            download_pictures=True,
            download_videos=True,
            download_video_thumbnails=False,
            compress_json=False,
            save_metadata=False
        )

    def cleanup(self, files: List[str]):
        """Clean up downloaded files"""
        for file in files:
            try:
                if os.path.exists(file):
                    os.remove(file)
            except Exception as e:
                logger.error(f"Error deleting file {file}: {e}")

        for file in os.listdir(self.temp_dir):
            try:
                os.remove(os.path.join(self.temp_dir, file))
            except Exception as e:
                logger.error(f"Error cleaning up temp file {file}: {e}")

    async def process_url(self, url: str) -> List[str]:
        """Process URL and return list of downloaded file paths"""
        if "instagram.com" in url:
            return await self.handle_instagram(url)
        elif "tiktok.com" in url:
            return await self.handle_tiktok(url)
        return []

    async def handle_tiktok(self, url: str) -> List[str]:
        """Handle TikTok URLs"""
        try:
            logger.info(f"Processing TikTok URL: {url}")
            downloaded_files = []
            
            d = snaptik(url)
            if len(d) == 1:
                filename = os.path.join(self.temp_dir, 'video.mp4')
                d[0].download(filename)
                downloaded_files.append(filename)
            else:
                for index, item in enumerate(d):
                    filename = os.path.join(self.temp_dir, f'video_{index}.jpg')
                    item.download(filename)
                    downloaded_files.append(filename)
                    
            return downloaded_files
            
        except Exception as e:
            logger.error(f"Error processing TikTok URL: {str(e)}", exc_info=True)
            return []

    async def handle_instagram(self, url: str) -> List[str]:
        """Handle Instagram URLs"""
        try:
            logger.info(f"Processing Instagram URL: {url}")
            shortcode = self.extract_instagram_shortcode(url)
            if not shortcode:
                logger.error(f"Could not extract shortcode from URL: {url}")
                return []
            
            logger.info(f"Extracted shortcode: {shortcode}")
            post = instaloader.Post.from_shortcode(self.instagram.context, shortcode)
            downloaded_files = []

            logger.info(f"Downloading post to directory: {self.temp_dir}")
            self.instagram.download_post(post, target=self.temp_dir)

            files = os.listdir(self.temp_dir)
            logger.info(f"Files in temp directory: {files}")
            
            for file in files:
                if file.endswith(('.jpg', '.mp4')):
                    full_path = os.path.join(self.temp_dir, file)
                    downloaded_files.append(full_path)
                    logger.info(f"Added file to processing queue: {full_path}")

            if not downloaded_files:
                logger.warning("No media files were found after download")
                
            return downloaded_files
        except instaloader.exceptions.InstaloaderException as e:
            logger.error(f"Instaloader error: {str(e)}", exc_info=True)
            return []
        except Exception as e:
            logger.error(f"Unexpected error processing Instagram URL: {str(e)}", exc_info=True)
            return []

    @staticmethod
    def extract_instagram_shortcode(url: str) -> Union[str, None]:
        """Extract shortcode from Instagram URL"""
        patterns = [
            r'instagram\.com/(?:[^/]+/)?p/([^/?]+)',
            r'instagram\.com/(?:[^/]+/)?v/([^/?]+)',
            r'instagram\.com/(?:[^/]+/)?reels/([^/?]+)',
            r'instagram\.com/(?:[^/]+/)?reel/([^/?]+)',
            r'instagram\.com/(?:[^/]+/)?video/([^/?]+)',
            r'instagram\.com/(?:[^/]+/)?photo/([^/?]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

class TelegramBot:
    def __init__(self, token: str):
        self.token = token
        self.media_handler = MediaHandler()

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        await update.message.reply_text(
            "Hello! Send me an Instagram post URL, and I'll send you the media!"
        )

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming messages"""
        try:
            message = update.message.text
            user_id = update.message.from_user.id
            logger.info(f"Received message from user {user_id}: {message}")

            if not message:
                logger.warning(f"Empty message received from user {user_id}")
                return

            if "instagram.com" in message or "tiktok.com" in message:
                await update.message.reply_text("Processing your request...")
                logger.info(f"Processing media URL for user {user_id}")
                
                files = await self.media_handler.process_url(message)
                
                if not files:
                    logger.error(f"No files were processed for URL: {message}")
                    await update.message.reply_text("Sorry, I couldn't process that media.")
                    return

                logger.info(f"Successfully downloaded {len(files)} files")
                
                for i in range(0, len(files), 10):
                    chunk = files[i:i + 10]
                    media_group = []
                    
                    for file in chunk:
                        if file.endswith('.mp4'):
                            media_group.append(
                                InputMediaVideo(media=open(file, 'rb'))
                            )
                        elif file.endswith('.jpg'):
                            media_group.append(
                                InputMediaPhoto(media=open(file, 'rb'))
                            )
                    
                    if media_group:
                        await update.message.reply_media_group(media=media_group)

                logger.info("Cleaning up temporary files")
                self.media_handler.cleanup(files)
                
        except Exception as e:
            logger.error(f"Error in handle_message: {str(e)}", exc_info=True)
            await update.message.reply_text("An unexpected error occurred while processing your request.")


    def run(self):
        """Run the bot"""
        app = Application.builder().token(self.token).build()
        app.add_handler(CommandHandler("start", self.start))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        app.run_polling()

def main():
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    if not BOT_TOKEN:
        logger.error("No bot token found in environment variables")
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable is not set")
    
    bot = TelegramBot(BOT_TOKEN)
    bot.run()

if __name__ == "__main__":
    main()
