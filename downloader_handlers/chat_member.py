import datetime

from telegram import Update, User
from telegram.constants import ParseMode
from telegram.ext import CallbackContext

from database import Database, CRUDLink, CRUDAd, CRUDAccount, AccountRole, CRUDSession, CRUDDownloaderUser, AdStatus, UpdateType

from utils import Regex, NumberTools


class ChatMember:

    @staticmethod
    async def new_change(update: Update, context: CallbackContext):
        chat_member_update = update.chat_member

        old_status = chat_member_update.old_chat_member.status
        new_status = chat_member_update.new_chat_member.status
        user = chat_member_update.new_chat_member.user

        if old_status in ("left", "kicked") and new_status == "member":  # Join
            if not chat_member_update.invite_link:
                return
            await ChatMember.__add_member(update, context, user, chat_member_update.invite_link.invite_link)
            await ChatMember.__check_suspicious_accounts(update, context, chat_member_update.invite_link.invite_link)
            await ChatMember.__check_completed(update, context, chat_member_update.invite_link.invite_link)
        elif old_status == "member" and new_status in ("left", "kicked"):  # Left
            with Database.get_session() as session:
                channels = CRUDAd.get_by_channel_chat_id(session, str(chat_member_update.chat.id), status=AdStatus.ACTIVE)
                if not channels:
                    return
            await ChatMember.__remove_member(user, chat_member_update)

    @staticmethod
    async def __add_member(update: Update, context: CallbackContext, user: User, invite_link: str):
        if user.is_bot:
            return

        with Database.get_session() as session:
            link = CRUDLink.get_by_url(session, invite_link)

            if link:
                data = {str(user.id): [user.username if user.username else "", await ChatMember.__calculate_score(update, context, user), str(datetime.datetime.now())]}
                # data = {str(user.id): [user.username if user.username else "", await ChatMember.__calculate_score(update, context, user)]}
                CRUDLink.add_member(session, link.id, data)

    @staticmethod
    async def __remove_member(user: User, chat_member_update):
        with Database.get_session() as session:
            ad = CRUDAd.get_by_channel_chat_id(session, str(chat_member_update.chat.id), status=AdStatus.ACTIVE)[0]
            if ad:
                CRUDLink.remove_member(session, ad.id, str(user.id))

    @staticmethod
    async def __calculate_score(update: Update, context: CallbackContext, user: User) -> int:
        chat = await context.bot.get_chat(chat_id=user.id)

        is_have_username = True if chat.username else False
        is_have_bio = True if chat.bio else False
        is_have_persian_bio = Regex.contains_persian(chat.bio) if chat.bio else False
        is_have_profile_picture = True if chat.photo else False
        is_have_persian_name = Regex.contains_persian(chat.full_name)

        point = 0

        if is_have_username:
            point += 30
        if is_have_bio:
            point += 15
        if is_have_persian_bio:
            point += 20
        if is_have_persian_name:
            point += 20
        if is_have_profile_picture:
            point += 15

        # Normal : +45 to 65
        # Good : +65 to 100
        # Bad : -30

        return point

    @staticmethod
    async def __check_suspicious_accounts(update: Update, context: CallbackContext, invite_link: str):

        def count_recent_joins_minutes(join_times: list, minutes: int):
            now = datetime.datetime.now()
            threshold = now - datetime.timedelta(minutes=minutes)
            return sum(1 for t in join_times if t >= threshold)

        def count_recent_joins_seconds(join_times: list, seconds: int):
            now = datetime.datetime.now()
            threshold = now - datetime.timedelta(seconds=seconds)
            return sum(1 for t in join_times if t >= threshold)

        with Database.get_session() as session:
            link = CRUDLink.get_by_url(session, invite_link)

            if not link:
                return

            ad = CRUDAd.get_by_id(session, link.ad_id)
            if ad.status != AdStatus.ACTIVE:
                return

            admins = CRUDAccount.get_by_role(session, AccountRole.ADMIN)
            times = []
            for _, member in link.members.items():  # noqa
                if len(member) == 3:
                    times.append(datetime.datetime.strptime(member[2], "%Y-%m-%d %H:%M:%S.%f"))

            sec_10_count = count_recent_joins_seconds(times, 10)
            min_1_count = count_recent_joins_minutes(times, 1)
            min_5_count = count_recent_joins_minutes(times, 5)
            min_30_count = count_recent_joins_minutes(times, 30)
            min_60_count = count_recent_joins_minutes(times, 60)

            num = 25
            message_text = "⚠️ هشدار" + "\n\n"
            has_warning = False
            if sec_10_count > num:
                message_text += " لینک به آدرس زیر تعداد" + str(sec_10_count) + " در 10 ثانیه عضو شده اند"
                message_text += "\n" + invite_link + "\n\n" + "برای بررسی بیشتر از قسمت مدیریت لینک جزئیات رو مشاهده کنید."
                has_warning = True
                if datetime.datetime.now() - link.updated_at >= datetime.timedelta(minutes=5):
                    for admin in admins:
                        session_admin = CRUDSession.get_by_account_id(session, admin.id)
                        user = CRUDDownloaderUser.get_by_id(session, session_admin[0].downloader_user_id)
                        await context.bot.send_message(chat_id=user.chat_id, text=message_text, parse_mode=ParseMode.HTML)
            if min_1_count > num * 6:
                message_text += " لینک به آدرس زیر تعداد" + str(min_1_count) + " در 1 دقیقه عضو شده اند"
                message_text += "\n" + invite_link + "\n\n" + "برای بررسی بیشتر از قسمت مدیریت لینک جزئیات رو مشاهده کنید."
                has_warning = True
                if datetime.datetime.now() - link.updated_at >= datetime.timedelta(minutes=5):
                    for admin in admins:
                        session_admin = CRUDSession.get_by_account_id(session, admin.id)
                        user = CRUDDownloaderUser.get_by_id(session, session_admin[0].downloader_user_id)
                        await context.bot.send_message(chat_id=user.chat_id, text=message_text, parse_mode=ParseMode.HTML)
            if min_5_count > num * 6 * 5:
                message_text += " لینک به آدرس زیر تعداد" + str(min_5_count) + " در 5 دقیقه عضو شده اند"
                message_text += "\n" + invite_link + "\n\n" + "برای بررسی بیشتر از قسمت مدیریت لینک جزئیات رو مشاهده کنید."
                has_warning = True
                if datetime.datetime.now() - link.updated_at >= datetime.timedelta(minutes=5):
                    for admin in admins:
                        session_admin = CRUDSession.get_by_account_id(session, admin.id)
                        user = CRUDDownloaderUser.get_by_id(session, session_admin[0].downloader_user_id)
                        await context.bot.send_message(chat_id=user.chat_id, text=message_text, parse_mode=ParseMode.HTML)
            if min_30_count > num * 6 * 30:
                message_text += " لینک به آدرس زیر تعداد" + str(min_30_count) + " در 30 دقیقه عضو شده اند"
                message_text += "\n" + invite_link + "\n\n" + "برای بررسی بیشتر از قسمت مدیریت لینک جزئیات رو مشاهده کنید."
                has_warning = True
                if datetime.datetime.now() - link.updated_at >= datetime.timedelta(minutes=5):
                    for admin in admins:
                        session_admin = CRUDSession.get_by_account_id(session, admin.id)
                        user = CRUDDownloaderUser.get_by_id(session, session_admin[0].downloader_user_id)
                        await context.bot.send_message(chat_id=user.chat_id, text=message_text, parse_mode=ParseMode.HTML)
            if min_60_count > num * 6 * 60:
                message_text += " لینک به آدرس زیر تعداد" + str(min_60_count) + " در 60 دقیقه عضو شده اند"
                message_text += "\n" + invite_link + "\n\n" + "برای بررسی بیشتر از قسمت مدیریت لینک جزئیات رو مشاهده کنید."
                has_warning = True
                if datetime.datetime.now() - link.updated_at >= datetime.timedelta(minutes=5):
                    for admin in admins:
                        session_admin = CRUDSession.get_by_account_id(session, admin.id)
                        user = CRUDDownloaderUser.get_by_id(session, session_admin[0].downloader_user_id)
                        await context.bot.send_message(chat_id=user.chat_id, text=message_text, parse_mode=ParseMode.HTML)

            if has_warning:
                CRUDLink.update_has_warning(session, link.id, True)

    @staticmethod
    async def __check_completed(update: Update, context: CallbackContext, invite_link: str):
        with Database.get_session() as session:
            link = CRUDLink.get_by_url(session, invite_link)

            if not link:
                return

            ad = CRUDAd.get_by_id(session, link.ad_id)
            if ad.status != AdStatus.ACTIVE:
                return
            all_ad_links = CRUDLink.get_by_ad_id(session, ad.id)
            full_value = 0
            count = 0

            for ad_link in all_ad_links:
                count += ad_link.count

            if count == ad.capacity:

                if ad.auto_complete:
                    CRUDAd.update_status(session, ad.id, AdStatus.COMPLETED)

                    if ad.prize:
                        top_links = CRUDLink.get_top_by_ad_id(session, ad.id, len(ad.prize.keys()))  # NOQA
                    else:
                        top_links = []
                    flag = False
                    for ad_link in all_ad_links:
                        new_balance = (ad_link.count * ad.rate) / 100
                        if top_links:
                            number = 1

                            for top_link in top_links:
                                if ad_link.id == top_link.id:
                                    for key, value in ad.prize.items():  # NOQA
                                        if int(key) == number:
                                            new_balance += value
                                            flag = True
                                            break
                                    if flag:
                                        break
                                number += 1
                        CRUDAccount.update_balance(session, ad_link.account_id, UpdateType.INCREMENT, new_balance)
                        try:
                            text = "✅ تبلیغ " + str(ad.id) + " حسابرسی شد"
                            text += "\n\n" + "لینک شما : " + "\n" + link.url
                            text += "\n" + "مبلغ اضافه شده : " + NumberTools.format_number(new_balance) + " تومان"
                            text += "\n" + "تعداد جذب توسط شما : " + NumberTools.format_number(link.count)
                            if flag:
                                text += "\n\n" + "جایزه تبلیغ را نیز دریافت کردید"
                            user = CRUDDownloaderUser.get_by_id(session, CRUDSession.get_by_account_id(session, link.account_id)[0].downloader_user_id)
                            await context.bot.send_message(chat_id=user.chat_id, text=text)
                        except Exception as e:
                            pass
                        full_value += new_balance
                        await context.bot.revoke_chat_invite_link(chat_id=ad.channel_chat_id, invite_link=ad_link.url)

                    admins = CRUDAccount.get_by_role(session, AccountRole.ADMIN)
                    message_text = "✅ حسابرسی تبلیغ " + str(ad.id) + " به طور خوکار انجام شد."
                    message_text += "\n\n" + "میزان مبلغ اضافه شده به موجودی ها : " + NumberTools.format_number(full_value) + " تومان"
                    message_text += "\n\n" + "تعداد افراد مشارکت کرده در تبلیغ : " + NumberTools.format_number(len(all_ad_links)) + " نفر"
                    for admin in admins:
                        session_admin = CRUDSession.get_by_account_id(session, admin.id)
                        user = CRUDDownloaderUser.get_by_id(session, session_admin[0].downloader_user_id)
                        await context.bot.send_message(chat_id=user.chat_id, text=message_text, parse_mode=ParseMode.HTML)
                else:
                    admins = CRUDAccount.get_by_role(session, AccountRole.ADMIN)
                    message_text = "📢 تبلیغ شماره" + " " + str(ad.id) + " تکمیل ظرفیت شده و آماده حسابرسی است." + "\n\n"
                    message_text += "⚠️ حسابرسی خودکار برای این تبلیغ غیرفعال است، لطفاً حسابرسی را به‌صورت دستی انجام دهید."
                    for admin in admins:
                        session_admin = CRUDSession.get_by_account_id(session, admin.id)
                        user = CRUDDownloaderUser.get_by_id(session, session_admin[0].downloader_user_id)
                        await context.bot.send_message(chat_id=user.chat_id, text=message_text, parse_mode=ParseMode.HTML)
