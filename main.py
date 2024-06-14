from telethon import TelegramClient, events
import re
import json
from datetime import datetime
import pytz
import emoji
import asyncio
# Load the config data from config.json
with open('config.json') as f:
    config = json.load(f)

# Extract the values from the config
api_id = config['api_id']
api_hash = config['api_hash']
phone_number = config['phone_number']
channel_username = config['channel_username']
bot_username = config['bot_username']  # Add bot username to config

# Create the client and connect
client = TelegramClient('session_name', api_id, api_hash)
client.start(phone=phone_number)

# Function to parse the message
def parse_message(message):
    pattern = r"Period (\d+) \((BIG|SMALL)\) (\d+) RS"
    matches = re.findall(pattern, message)
    return [(int(period), prediction, int(amount)) for period, prediction, amount in matches]

# Function to display the next prediction and previous predictions
async def display_predictions(parsed_data):
    if not parsed_data:
        print("No data found.")
        return

    # Get the last period's data
    last_period, last_prediction, last_amount = parsed_data[-1]

    # Determine the next prediction
    next_prediction = last_prediction
    next_amount = last_amount  # Changed to integer for comparison

    # Display the next prediction
    print(f"Next Prediction for Period {last_period}: {next_prediction}")
    print(f"Amount: {next_amount}\n")
    if next_amount == 1:
        victory_emoji = emoji.emojize(":party_popper:")  # 🎉
        message_to_send = f"{victory_emoji}"
        await client.send_message(bot_username, message_to_send)
    # Send message to bot if next_amount is greater than equal 27
    if next_amount >= 27:
        red_emoji = emoji.emojize(":cross_mark:")  # ❌
        alert_message = "DON'T MISS THIS!!!"
        message_to_send = f"{red_emoji}Alert: {alert_message}{red_emoji}\nNext Prediction for Period {last_period}: {next_prediction}\nAmount: {next_amount}x"
        await client.send_message(bot_username, message_to_send)
    else:
        message_to_send = f"Next Prediction for Period {last_period}: {next_prediction}\nAmount: {next_amount}x"
        await client.send_message(bot_username, message_to_send)

    # Display previous predictions
    print("Previous Predictions:")
    for i in range(len(parsed_data) - 1, 0, -1):
        period, prediction, amount = parsed_data[i]
        prev_period, prev_prediction, prev_amount = parsed_data[i - 1]
        status = "Correct prediction" if amount == 1 else "Incorrect prediction"
        print(f"Period {prev_period}: {prev_prediction} ({prev_amount} RS) - {status}")

# Function to fetch and display the last message
async def fetch_last_message():
    messages = await client.get_messages(channel_username, limit=1)
    if messages:
        message = messages[0]
        timestamp = message.date.astimezone(pytz.timezone('Asia/Kolkata')).strftime("%d/%m/%Y %I:%M %p")
        print(f"Message received at: {timestamp}")
        parsed_data = parse_message(message.text)
        await display_predictions(parsed_data)

# Event handler for new messages
@client.on(events.NewMessage(chats=channel_username))
async def handler(event):
    message = event.message.message
    timestamp = event.message.date.astimezone(pytz.timezone('Asia/Kolkata')).strftime("%d/%m/%Y %I:%M %p")
    print(f"Message received at: {timestamp}")
    parsed_data = parse_message(message)
    await display_predictions(parsed_data)

# Function to send scheduled messages
async def send_scheduled_messages():
    victory_emoji = emoji.emojize(":victory_hand:")  # ✌️
    thumbs_up = emoji.emojize(":thumbs_up:") # 👍 Thumbs Up
    while True:
        current_time = datetime.now(pytz.timezone('Asia/Kolkata'))
        if current_time.hour == 22 and current_time.minute == 40:
            message = f"{victory_emoji} That's all for today.{victory_emoji}\n\nScript created by @myselfnixon"
            await client.send_message(bot_username, message)
        elif current_time.hour == 11 and current_time.minute == 30:
            message = f"Predictions will start soon. Be ready. Good Luck{thumbs_up}\n\nScript created by @myselfnixon"
            await client.send_message(bot_username, message)
        await asyncio.sleep(60)  # Check every minute

# Run the client
async def main():
    await fetch_last_message()
    await client.run_until_disconnected()

with client:
    client.loop.run_until_complete(main())