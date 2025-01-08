import telebot
import moviepy.editor as mpe
import os
import logging

# Configure logging to catch errors more effectively.
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

# Replace 'YOUR_TELEGRAM_BOT_TOKEN' with your actual bot token
BOT_TOKEN = '7011113724:AAH6I1mdsKZyEa-LQiYmTrwumEjxB-N_sqk'
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(content_types=['video'])
def handle_video(message):
    """Handles incoming video messages, trims them into parts, and sends them back."""
    try:
        file_id = message.video.file_id
        file_info = bot.get_file(file_id)
        downloaded_file_path = bot.download_file(file_info.file_path)

        # Get the number of parts from the user with improved input handling
        msg = bot.reply_to(message, "How many parts do you want to split the video into? (Enter a positive integer)")
        bot.register_next_step_handler(msg, process_split_request, downloaded_file_path)

    except telebot.apihelper.ApiException as e:
        logging.error(f"Telegram API Error: {e}")
        bot.reply_to(message, "An error occurred while communicating with Telegram. Please try again later.")
    except Exception as e:
        logging.exception(f"An unexpected error occurred: {e}")
        bot.reply_to(message, "An unexpected error occurred. Please try again later.")


def process_split_request(message, downloaded_file_path):
    """Processes the user's response about how many parts to split into."""
    try:
        num_parts = int(message.text)
        if num_parts <= 0:
            raise ValueError("Number of parts must be a positive integer.")
        split_video(downloaded_file_path, num_parts, message)

    except ValueError as e:
        bot.reply_to(message, f"Invalid input: {e}. Please enter a positive integer.")
    except Exception as e:
        logging.exception(f"An error occurred during splitting request processing: {e}")
        bot.reply_to(message, "An error occurred. Please try again later.")


def split_video(file_path, num_parts, message):
    """Splits the video into the specified number of parts and sends them back."""
    try:
        video = mpe.VideoFileClip(file_path)
        total_duration = video.duration
        part_duration = total_duration / num_parts

        for i in range(num_parts):
            start_time = i * part_duration
            end_time = min((i + 1) * part_duration, total_duration) #Handle potential slight inaccuracies
            part = video.subclip(start_time, end_time)
            temp_file_path = f"part_{i+1}.mp4"
            part.write_videofile(temp_file_path, codec='libx264') #Specify codec for better compatibility
            with open(temp_file_path, 'rb') as f:
                bot.send_video(message.chat.id, f, supports_streaming=True) #Added supports_streaming
            os.remove(temp_file_path) # Clean up temporary files after sending

        video.close()

    except moviepy.editor.MoviePyError as e:
        logging.error(f"MoviePy Error: {e}")
        bot.reply_to(message, f"An error occurred during video processing: {e}. Is FFmpeg installed and configured correctly?")
    except Exception as e:
        logging.exception(f"An unexpected error occurred during video splitting: {e}")
        bot.reply_to(message, "An unexpected error occurred. Please try again later.")


bot.polling()
