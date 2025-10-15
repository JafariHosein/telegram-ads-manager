import math
from typing import List, Sequence

from telegram import InlineKeyboardMarkup, InlineKeyboardButton
import jdatetime

from bot.keyboard import DownloaderInlineButtons


class Pagination:

    @staticmethod
    def paginate(data: Sequence, callback_data: str, properties: list, buttons_callback: list, show_number: int = 20, page: int = 1, count: int = 2) -> List:
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

                item_id = getattr(data[item + number], properties[0][0], None)
                message_text += "<blockquote>"
                for my_property in properties:
                    prop_name = my_property[0]
                    prop_value = getattr(data[item + number], my_property[0], None)
                    message_text += my_property[1] + " : " + f"{Pagination.__format_value(prop_name, prop_value)}" + "\n"
                message_text += "</blockquote>" + "\n"

                temp_btns.append(InlineKeyboardButton(str(item_id),callback_data=f"{callback_data}*{item_id}"))

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
                                             callback_data=buttons_callback[2])])

        message_text += "👇 بر روی گزینه مورد نظر کلیک کنید"
        markup = InlineKeyboardMarkup(buttons)

        return [markup, message_text]

    @staticmethod
    def __format_value(property_name: str, property_value):
        if property_name == "created_at" or property_name == "updated_at":
            shamsi_date = jdatetime.datetime.fromgregorian(datetime=property_value)
            shamsi_date = shamsi_date.strftime('%Y/%m/%d ⏰ %H:%M')
            shamsi_date = str(shamsi_date).replace("-", "/")

            return shamsi_date

        return property_value
