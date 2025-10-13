from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from database.models.register_request import RegisterRequestStatusFarsi


class DownloaderInlineButtons:
    words = {
        "Add": "➕ افزودن",
        "Delete": "❌ حذف",
        "SubmitRequest": "✅ ثبت درخواست",
        "Return": "🔙 بازگشت",
        "Registers": "📝 عضویت ها",
        "Transfers": "🔁 انتقال ها",
        "Payouts": "💰 برداشت ها",
        "NextPage": "⏭ صفحه بعدی",
        "PreviousPage": "⏮ صفحه قبلی",
        "IUnderstand": "✅ متوجه شدم"

    }

    register_empty = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{words["Add"]}", callback_data="AddLinkedUsername")],
        [InlineKeyboardButton(f"{words["Return"]}", callback_data="ReturnToStart")]
    ])

    register_not_empty = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{words["SubmitRequest"]}", callback_data="SubmitRegisterRequest")],
        [InlineKeyboardButton(f"{words["Add"]}", callback_data="AddLinkedUsername"),
         InlineKeyboardButton(f"{words["Delete"]}", callback_data="RemoveLinkedUsername")],
        [InlineKeyboardButton(f"{words["Return"]}", callback_data="ReturnToStart")]

    ])

    return_to_register = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{words["Return"]}", callback_data="ReturnToRegister")]
    ])

    return_to_start = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{words["Return"]}", callback_data="ReturnToStart")]
    ])

    return_to_pending_register_requests = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{words["Return"]}", callback_data="ReturnToPendingRegisterRequests")]
    ])

    requests = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{words['Registers']}", callback_data="RegistersMenu"),
         InlineKeyboardButton(f"{words['Transfers']}", callback_data="TransfersMenu")],
        [InlineKeyboardButton(f"{words['Payouts']}", callback_data="PayoutsMenu")],
        [InlineKeyboardButton(f"{words['Return']}", callback_data="ReturnToStart")],
    ])

    register_requests = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{RegisterRequestStatusFarsi.PENDING.value}", callback_data="PendingRegisterRequests")],
        [InlineKeyboardButton(f"{RegisterRequestStatusFarsi.APPROVED.value}", callback_data="ApprovedRegisterRequests")],
        [InlineKeyboardButton(f"{RegisterRequestStatusFarsi.REJECTED.value}", callback_data="RejectedRegisterRequests")],
        [InlineKeyboardButton(f"{words['Return']}", callback_data="ReturnToRequests")],
    ])

    i_saved_my_password = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{words["IUnderstand"]}", callback_data="ReturnToStart")]
    ])


class DownloaderReplyButtons:
    words = {
        "Register": "📝 ثبت‌ نام",
        "Login": "🔑 ورود",
        "ContactSupport": "📞 ارتباط با پشتیبانی",
        "Ads": "📢 تبلیغات",
        "Stats": "📊 آمار",
        "LinkManager": "🔗 مدیریت لینک",
        "Requests": "📨 درخواست ها",
        "Users": "👥 کاربران",
        "Accounts": "💼 اکانت ها",
        "Settings": "🛠️ تنظیمات",
        "CryptoOnline": "💰 قیمت لحظه ایی",
        "BalanceList": "💳 لیست موجودی ها"
    }

    new_user = ReplyKeyboardMarkup([
        [KeyboardButton(words["Login"]), KeyboardButton(words["Register"])],
        [KeyboardButton(words["ContactSupport"])]
    ], resize_keyboard=True)

    admin = ReplyKeyboardMarkup([
        [KeyboardButton(words["Ads"]), KeyboardButton(words["LinkManager"])],
        [KeyboardButton(words["Stats"]), KeyboardButton(words["Requests"])],
        [KeyboardButton(words["Accounts"]), KeyboardButton(words["Users"])],
        [KeyboardButton(words["Settings"]), KeyboardButton(words["BalanceList"])],
        [KeyboardButton(words["CryptoOnline"])]
    ])
