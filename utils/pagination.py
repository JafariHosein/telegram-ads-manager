import math
from typing import List, Sequence

from telegram import InlineKeyboardMarkup, InlineKeyboardButton
import jdatetime

from bot.keyboard import DownloaderInlineButtons
from database import Database, CRUDLink, CRUDAd, CRUDSession, CRUDAccount, CRUDDownloaderUser, PayoutRequestDestinationTypeFarsi
from utils.num_tools import NumberTools


class Pagination:

    @staticmethod
    def paginate(data: Sequence, callback_data: str, properties: list, buttons_callback: list, show_number: int = 20, page: int = 1, count: int = 2, one_page_only: bool = False, end_text: str = "",
                 callback_number_name: str = "", no_callback: bool = False) -> List:
        """
        example properties = [["username","یوزرنیم"],["password","رمز عبور"],...]
        example buttons_callback = [PreviousPage, NextPage, Return]
        """
        buttons = []
        if len(data) == 0:
            message_text = "🛑 چیزی برای نمایش وجود ندارد."
            buttons.append([InlineKeyboardButton(DownloaderInlineButtons.words["Return"],
                                                 callback_data=buttons_callback[2])])
            markup = InlineKeyboardMarkup(buttons)
            return [markup, message_text]

        page_count = math.ceil(len(data) / show_number)

        message_text = ""
        if not one_page_only:
            message_text += "📄 صفحه " + str(page) + " " + "از " + str(page_count)
            message_text += "\n\n"

        for item in range((page * show_number) - show_number, page * show_number, count):
            if item > len(data) - 1:
                break

            # Generate MessageText
            temp_btns = []
            for number in range(0, count):
                if len(data) <= item + number:
                    break

                item_id = getattr(data[item + number], properties[0][0], None)
                message_text += "<blockquote>"
                for my_property in properties:
                    prop_name = my_property[0]
                    prop_value = getattr(data[item + number], my_property[0], None)
                    message_text += my_property[1] + " : " + f"{Pagination.__format_value(prop_name, prop_value)}" + "\n"
                message_text += "</blockquote>" + "\n"

                if no_callback:
                    continue

                if callback_number_name:
                    item_id_2 = getattr(data[item + number], callback_number_name, None)
                    temp_btns.append(InlineKeyboardButton(str(item_id), callback_data=f"{callback_data}*{item_id_2}"))
                else:
                    temp_btns.append(InlineKeyboardButton(str(item_id), callback_data=f"{callback_data}*{item_id}"))

            buttons.append(temp_btns)

        if not one_page_only:
            if len(data) > show_number:
                if page_count == page:  # Last Page
                    buttons.append([InlineKeyboardButton(DownloaderInlineButtons.words["PreviousPage"],
                                                         callback_data=f"{buttons_callback[0]}*{page - 1}")])
                elif page == 1:  # First Page
                    buttons.append([InlineKeyboardButton(DownloaderInlineButtons.words["NextPage"],
                                                         callback_data=f"{buttons_callback[0]}*{page + 1}")])
                else:  # Between first and last
                    buttons.append([InlineKeyboardButton(DownloaderInlineButtons.words["PreviousPage"], callback_data=f"{buttons_callback[0]}*{page - 1}"),
                                    InlineKeyboardButton(DownloaderInlineButtons.words["NextPage"], callback_data=f"{buttons_callback[0]}*{page + 1}")])

        buttons.append([InlineKeyboardButton(DownloaderInlineButtons.words["Return"],
                                             callback_data=buttons_callback[2])])

        if end_text:
            message_text += end_text
        else:
            message_text += "👇 بر روی گزینه مورد نظر کلیک کنید"
        markup = InlineKeyboardMarkup(buttons)

        return [markup, message_text]

    @staticmethod
    def paginate_ads(data: Sequence, callback_data: str, properties: list, buttons_callback: list, account_id: int, show_number: int = 20, page: int = 1, count: int = 2) -> list:
        """
               example properties = [["username","یوزرنیم"],["password","رمز عبور"],...]
               example buttons_callback = [PreviousPage, NextPage, Return]
               """
        buttons = []
        if len(data) == 0:
            message_text = "🛑 چیزی برای نمایش وجود ندارد."
            buttons.append([InlineKeyboardButton(DownloaderInlineButtons.words["Return"],
                                                 callback_data=buttons_callback[2])])
            markup = InlineKeyboardMarkup(buttons)
            return [markup, message_text]

        page_count = math.ceil(len(data) / show_number)

        message_text = "📍 تبلیغ ها"
        message_text += "\n\n"

        for item in range((page * show_number) - show_number, page * show_number, count):
            if item > len(data) - 1:
                break

            # Generate MessageText
            temp_btns = []
            for number in range(0, count):
                if len(data) <= item + number:
                    break

                item_id = getattr(data[item + number], properties[0][0], None)
                message_text += "شماره تبلیغ : " + f"{item_id}#"
                message_text += "<blockquote>"
                for my_property in properties:
                    prop_name = my_property[0]
                    if prop_name == "id":
                        continue
                    prop_value = getattr(data[item + number], my_property[0], None)
                    message_text += my_property[1] + " : " + f"{Pagination.__format_value(prop_name, prop_value, item_id)}" + "\n"

                with Database.get_session() as session:
                    already_have = CRUDLink.exist(session, item_id, account_id)
                    if already_have:
                        message_text += "\n<b>" + "🟢 لینک این تبلیغ را قبلا گرفته اید" + "</b>"
                message_text += "</blockquote>" + "\n"

                temp_btns.append(InlineKeyboardButton("📎 " + str(item_id), callback_data=f"{callback_data}*{item_id}"))

            buttons.append(temp_btns)

        if len(data) > show_number:
            if page_count == page:  # Last Page
                buttons.append([InlineKeyboardButton(DownloaderInlineButtons.words["PreviousPage"],
                                                     callback_data=f"{buttons_callback[0]}*{page - 1}")])
            elif page == 1:  # First Page
                buttons.append([InlineKeyboardButton(DownloaderInlineButtons.words["NextPage"],
                                                     callback_data=f"{buttons_callback[1]}*{page + 1}")])
            else:  # Between first and last
                buttons.append([InlineKeyboardButton(DownloaderInlineButtons.words["PreviousPage"], callback_data=f"{buttons_callback[0]}*{page - 1}"),
                                InlineKeyboardButton(DownloaderInlineButtons.words["NextPage"], callback_data=f"{buttons_callback[1]}*{page + 1}")])

        buttons.append([InlineKeyboardButton(DownloaderInlineButtons.words["Return"],
                                             callback_data=buttons_callback[2])])

        message_text += "📄 صفحه " + str(page) + " " + "از " + str(page_count) + "\n\n"
        message_text += "👇 " + "جهت مشاهده جزئیات و دریافت لینک اختصاصی بر روی شماره تبلیغ مورد نظر کلیک کنید"
        markup = InlineKeyboardMarkup(buttons)

        return [markup, message_text]

    @staticmethod
    def paginate_members(raw_data: dict, callback_data: str, buttons_callback: list, count: int, show_number: int = 20, page: int = 1, end_text: str = "") -> List:
        """
        example buttons_callback = [PreviousPage, NextPage, Return]
        """

        data = []

        for chat_id, member in raw_data.items():
            data.append([chat_id, member])

        buttons = []
        if len(data) == 0:
            message_text = "🛑 چیزی برای نمایش وجود ندارد."
            buttons.append([InlineKeyboardButton(DownloaderInlineButtons.words["Return"],
                                                 callback_data=buttons_callback[2])])
            markup = InlineKeyboardMarkup(buttons)
            return [markup, message_text]

        page_count = math.ceil(len(data) / show_number)

        message_text = "📄 صفحه " + str(page) + " " + "از " + str(page_count)
        message_text += "\n\n"

        for item in range((page * show_number) - show_number, page * show_number, count):
            if item > len(data) - 1:
                break

            # Generate MessageText
            temp_btns = []
            for number in range(0, count):
                if len(data) <= item + number:
                    break
                message_text += "<blockquote>"
                message_text += "- آیدی عددی : " + str(data[item][0]) + "\n"
                message_text += "- یوزرنیم : " + (f"@{data[item][1][0]}" if data[item][1][0] else "ندارد") + "\n"
                message_text += "- امتیاز کاربر : " + str(data[item][1][1]) + "\n"
                temp_btns.append(InlineKeyboardButton(str(data[item][0]), callback_data=f"{callback_data}*{data[item][0]}"))
                message_text += "</blockquote>" + "\n"

            buttons.append(temp_btns)

        if len(data) > show_number:
            if page_count == page:  # Last Page
                buttons.append([InlineKeyboardButton(DownloaderInlineButtons.words["PreviousPage"],
                                                     callback_data=f"{buttons_callback[0]}*{page - 1}")])
            elif page == 1:  # First Page
                buttons.append([InlineKeyboardButton(DownloaderInlineButtons.words["NextPage"],
                                                     callback_data=f"{buttons_callback[0]}*{page + 1}")])
            else:  # Between first and last
                buttons.append([InlineKeyboardButton(DownloaderInlineButtons.words["PreviousPage"], callback_data=f"{buttons_callback[0]}*{page - 1}"),
                                InlineKeyboardButton(DownloaderInlineButtons.words["NextPage"], callback_data=f"{buttons_callback[0]}*{page + 1}")])

        buttons.append([InlineKeyboardButton(DownloaderInlineButtons.words["Return"],
                                             callback_data=buttons_callback[2] + f"*{callback_data.split("*")[1]}")])

        if end_text:
            message_text += end_text
        else:
            message_text += "👇 بر روی کاربر مورد نظر جهت حذف از لینک، کلیک کنید"
        markup = InlineKeyboardMarkup(buttons)

        return [markup, message_text]

    @staticmethod
    def __format_value(property_name: str, property_value, ad_id: int = None):
        if property_name == "created_at" or property_name == "updated_at":
            shamsi_date = jdatetime.datetime.fromgregorian(datetime=property_value)
            shamsi_date = shamsi_date.strftime('%Y/%m/%d ⏰ %H:%M')
            shamsi_date = str(shamsi_date).replace("-", "/")

            return shamsi_date

        elif property_name == "rate":
            return NumberTools.format_number(property_value) + " تومان" + " برای هر 100 نفر"
        elif property_name == "amount":
            return NumberTools.format_number(property_value) + " تومان"
        elif property_name == "capacity":
            return NumberTools.format_number(property_value) + " نفر"
        elif property_name == "destination_type":
            return PayoutRequestDestinationTypeFarsi[property_value.name].value
        elif property_name == "count_minus":
            count = 0
            with Database.get_session() as session:
                ad = CRUDAd.get_by_id(session, ad_id)
                links = CRUDLink.get_by_ad_id(session, ad_id)
                for link in links:
                    count += link.count

                final_value = ad.capacity - count
                if final_value >= 0:
                    return NumberTools.format_number(final_value) + " نفر"
                else:
                    return "0" + " نفر"
        elif property_name == "has_warning":
            return "⚠️ دارد" if property_value else "ندارد"
        elif property_name == "downloader_user_id":
            with Database.get_session() as session:
                return CRUDDownloaderUser.get_by_id(session, int(property_value)).chat_id
        return property_value
