import math
from typing import List, Sequence

from telegram import InlineKeyboardMarkup, InlineKeyboardButton
import jdatetime

from bot.keyboard import DownloaderInlineButtons


class Pagination:

    @staticmethod
    def paginate(data: Sequence, callback_data: str, properties: list, buttons_callback: list, show_number: int = 20, page: int = 1) -> List:
        """
        example properties = [["username","یوزرنیم"],["password","رمز عبور"],...]
        example buttons_callback = [PreviousPage, NextPage, Return]
        """
        page_count = math.ceil(len(data) / show_number)

        message_text = "📄 صفحه " + str(page) + " " + "از " + str(page_count)
        message_text += "\n\n"

        buttons = []

        for item in range((page * show_number) - show_number, page * show_number, 2):
            if item > len(data) - 1:
                break

            message_text += "<blockquote>"
            for my_property in properties:
                prop_name = my_property[0]
                prop_value = getattr(data[item], my_property[0], None)
                message_text += my_property[1] + " : " + f"{Pagination.__format_value(prop_name, prop_value)}" + "\n"

            item_id = getattr(data[item], properties[0][0], None)
            try:
                item_id_2 = getattr(data[item + 1], properties[0][0], None)
                buttons.append([InlineKeyboardButton(str(item_id), callback_data=f"{callback_data}*{item_id}"),
                                InlineKeyboardButton(str(item_id_2), callback_data=f"{callback_data}*{item_id_2}")])

            except:
                buttons.append([InlineKeyboardButton(str(item_id), callback_data=f"{callback_data}*{item_id}")])

            message_text += "</blockquote>" + "\n"
            try:
                item_id_2 = getattr(data[item + 1], properties[0][0], None)
                message_text += "<blockquote>"
                for my_property in properties:
                    prop_name = my_property[0]
                    prop_value = getattr(data[item + 1], my_property[0], None)
                    message_text += my_property[1] + " : " + f"{Pagination.__format_value(prop_name, prop_value)}" + "\n"
                message_text += "</blockquote>" + "\n"
            except:
                pass

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

        message_text +=  "👇 بر روی گزینه مورد نظر کلیک کنید"
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
