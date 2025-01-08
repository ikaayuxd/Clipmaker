import telebot
import moviepy.editor as mpe
import os

# Replace 'YOUR_TELEGRAM_BOT_TOKEN' with your actual bot token
BOT_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(content_types=['video'])
def handle_video(message):
    """Handles incoming video messages, trims them into parts, and sends them back."""
    try:
        file_id = message.video.file_id
        file_info = bot.get_file(file_id)
        downloaded_file_path = bot.download_file(file_info.file_path)

        #Get the number of parts from the user (you might want to improve this input method)
        bot.reply_to(message, "How many parts do you want to split the video into?")
        bot.register_next_step_handler(message, process_split_request, downloaded_file_path)

    except Exception as e:
        bot.reply_to(message, f"An error occurred: {e}")

def process_split_request(message, downloaded_file_path):
    """Processes the user's response about how many parts to split into."""
    try:
        num_parts = int(message.text)
        if num_parts <= 0:
            raise ValueError("Number of parts must be a positive integer.")
        split_video(downloaded_file_path, num_parts, message)

    except ValueError as e:
        bot.reply_to(message, f"Invalid input: {e}")
    except Exception as e:
        bot.reply_to(message, f"An error occurred: {e}")


def split_video(file_path, num_parts, message):
    """Splits the video into the specified number of parts and sends them back."""
    try:
        video = mpe.VideoFileClip(file_path)
        total_duration = video.duration
        part_duration = total_duration / num_parts

        for i in range(num_parts):
            start_time = i * part_duration
            end_time = (i + 1) * part_duration
            part = video.subclip(start_time, end_time)
            temp_file_path = f"part_{i+1}.mp4"
            part.write_videofile(temp_file_path)
            with open(temp_file_path, 'rb') as f:
                bot.send_video(message.chat.id, f)
            os.remove(temp_file_path) #Clean up temporary files after sending

        video.close()

    except Exception as e:
        bot.reply_to(message, f"An error occurred during video processing: {e}")



bot.polling()
