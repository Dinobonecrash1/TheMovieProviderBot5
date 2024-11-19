import logging
from pyrogram import Client, filters
import datetime
import time
from database.users_chats_db import db
from info import ADMINS
from utils import broadcast_messages, broadcast_messages_group
import asyncio

logging.basicConfig(level=logging.INFO)

@Client.on_message(filters.command("broadcast") & filters.user(ADMINS) & filters.reply)
async def verupikkals(bot, message):
    try:
        users = await db.get_all_users()
        if not users:
            await message.reply_text("No users found for broadcasting.")
            return

        b_msg = message.reply_to_message
        if not b_msg:
            await message.reply_text("Please reply to a message you want to broadcast.")
            return

        sts = await message.reply_text('Broadcasting your messages...')
        start_time = time.time()

        total_users = await db.total_users_count()
        done = 0
        blocked = deleted = failed = success = 0

        async for user in users:
            try:
                pti, sh = await broadcast_messages(int(user['id']), b_msg)
                if pti:
                    success += 1
                elif not pti:
                    if sh == "Blocked":
                        blocked += 1
                    elif sh == "Deleted":
                        deleted += 1
                    elif sh == "Error":
                        failed += 1
            except Exception as e:
                logging.error(f"Error occurred for user {user['id']}: {e}")
                failed += 1

            done += 1
            await asyncio.sleep(2)

            if done % 20 == 0:
                await sts.edit(f"Broadcast in progress:\n\nTotal Users {total_users}\nCompleted: {done} / {total_users}\nSuccess: {success}\nBlocked: {blocked}\nDeleted: {deleted}")

        time_taken = datetime.timedelta(seconds=int(time.time() - start_time))
        await sts.edit(f"Broadcast Completed:\nCompleted in {time_taken} seconds.\n\nTotal Users {total_users}\nCompleted: {done} / {total_users}\nSuccess: {success}\nBlocked: {blocked}\nDeleted: {deleted}")
    except Exception as e:
        logging.error(f"An error occurred during broadcast: {e}")
        await message.reply_text("An error occurred during broadcasting.")

@Client.on_message(filters.command("grp_broadcast") & filters.user(ADMINS) & filters.reply)
async def broadcast_group(bot, message):
    try:
        groups = await db.get_all_chats()
        if not groups:
            await message.reply_text("No groups found for broadcasting.")
            return

        b_msg = message.reply_to_message
        if not b_msg:
            await message.reply_text("Please reply to a message you want to broadcast.")
            return

        sts = await message.reply_text('Broadcasting your messages To Groups...')
        start_time = time.time()

        total_groups = await db.total_chat_count()
        done = failed = success = 0

        async for group in groups:
            try:
                pti, sh = await broadcast_messages_group(int(group['id']), b_msg)
                if pti:
                    success += 1
                elif sh == "Error":
                    failed += 1
            except Exception as e:
                logging.error(f"Error occurred for group {group['id']}: {e}")
                failed += 1

            done += 1

            if done % 20 == 0:
                await sts.edit(f"Broadcast in progress:\n\nTotal Groups {total_groups}\nCompleted: {done} / {total_groups}\nSuccess: {success}")

        time_taken = datetime.timedelta(seconds=int(time.time() - start_time))
        await sts.edit(f"Broadcast Completed:\nCompleted in {time_taken} seconds.\n\nTotal Groups {total_groups}\nCompleted: {done} / {total_groups}\nSuccess: {success}")
    except Exception as e:
        logging.error(f"An error occurred during group broadcast: {e}")
        await message.reply_text("An error occurred during group broadcasting.")
        
