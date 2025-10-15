from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from database.models.register_request import RegisterRequestStatusFarsi


class DownloaderInlineButtons:
    words = {
        "Add": "➕ افزودن",
        "Delete": "❌ حذف",
        "Edit": "✏️ ویرایش",
        "SubmitRequest": "✅ ثبت درخواست",
        "Submit": "✅ ثبت",
        "Return": "🔙 بازگشت",
        "Registers": "📝 عضویت ها",
        "Transfers": "🔁 انتقال ها",
        "Payouts": "💰 برداشت ها",
        "NextPage": "⏭ صفحه بعدی",
        "PreviousPage": "⏮ صفحه قبلی",
        "IUnderstand": "✅ متوجه شدم",
        "Search": "🔎 جستجو",
        "See": "📄 مشاهده",
        "Category": "📂 دسته بندی",
        "Title": "🏷️ عنوان",
        "Rate": "💰 نرخ",
        "Normal": "🟢 عادی",
        "RequestType": "📩 درخواستی",
        "ChooseByDownloader": "🎯 انتخاب توسط دانلودر",
        "Enable": "✅ فعال",
        "Disable": "❌ غیر فعال",
        "Skip": "⏩ رد کردن",
        "Done": "✅ انجام دادم",
        "SendToChannel": "📣 ارسال به کانال",
        "VerifyAd": "🧮 حسابرسی",
        "Details": "📋 جزئیات",
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

    manage_ads = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{words["Add"]}", callback_data="AddNewAd")],
        [InlineKeyboardButton(f"{words["See"]}", callback_data="SeeAds"),
         InlineKeyboardButton(f"{words["Search"]}", callback_data="SearchAd")],
        [InlineKeyboardButton(f"{words["Category"]}", callback_data="AdCategory")],
        [InlineKeyboardButton(f"{words["Return"]}", callback_data="ReturnToStart")]
    ])

    categories = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{words["Add"]}", callback_data="CreateAdCategory")],
        [InlineKeyboardButton(f"{words["Delete"]}", callback_data="RemoveAdCategory"),
         InlineKeyboardButton(f"{words["Edit"]}", callback_data="EditAdCategory")],
        [InlineKeyboardButton(f"{words["Return"]}", callback_data="ReturnToManageAds")]
    ])
    categories_empty = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{words["Add"]}", callback_data="CreateAdCategory")],
        [InlineKeyboardButton(f"{words["Return"]}", callback_data="ReturnToManageAds")]
    ])

    edit_category = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{words["Title"]}", callback_data="EditTitleThisCategory"),
         InlineKeyboardButton(f"{words["Rate"]}", callback_data="EditRateThisCategory")],
        [InlineKeyboardButton(f"{words["Return"]}", callback_data="ReturnToCategories")]
    ])

    choose_link_type_for_ad = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{words["Normal"]}", callback_data="ChooseThisLinkTypeForAd*NORMAL"), InlineKeyboardButton(f"{words["RequestType"]}", callback_data="ChooseThisLinkTypeForAd*REQUEST")],
        [InlineKeyboardButton(f"{words["ChooseByDownloader"]}", callback_data="ChooseThisLinkTypeForAd*BOTH")],
        [InlineKeyboardButton(f"{words["Return"]}", callback_data="ReturnToManageAds")]
    ])

    choose_auto_complete_for_ad = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{words["Enable"]}", callback_data="ChooseThisAutoCompleteForAd*True"), InlineKeyboardButton(f"{words["Disable"]}", callback_data="ChooseThisAutoCompleteForAd*False")],
        [InlineKeyboardButton(f"{words["Return"]}", callback_data="ReturnToManageAds")]
    ])

    skip_prize_for_ad = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{words["Skip"]}", callback_data="SkipThisPrizeForAd")],
        [InlineKeyboardButton(f"{words["Return"]}", callback_data="ReturnToManageAds")]
    ])

    submit_ad = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{words["Submit"]}", callback_data="SubmitThisAd")],
        [InlineKeyboardButton(f"{words["Return"]}", callback_data="ReturnToManageAds")]
    ])



    i_admin_bot = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{words["Done"]}", callback_data="IAdminBotForThisAd")],
        [InlineKeyboardButton(f"{words["Return"]}", callback_data="ReturnToManageAds")]
    ])

    return_to_categories = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{words["Return"]}", callback_data="ReturnToCategories")]
    ])
    return_to_mange_ads = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{words["Return"]}", callback_data="ReturnToManageAds")]
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
        "Break": "⇊ ─── دکمه های دانلودر ─── ⇊",
        "AccountProfile": "👤 حساب کاربری",
        "ActiveAds": "🟢 تبلیغات فعال",
        "TransferBalance": "🔁 انتقال",
        "PayoutBalance": "💵 برداشت"
    }

    new_user = ReplyKeyboardMarkup([
        [KeyboardButton(words["Login"]), KeyboardButton(words["Register"])],
        [KeyboardButton(words["ContactSupport"])]
    ], resize_keyboard=True)

    admin = ReplyKeyboardMarkup([
        [KeyboardButton(words["Ads"]), KeyboardButton(words["LinkManager"])],
        [KeyboardButton(words["Stats"]), KeyboardButton(words["Requests"])],
        [KeyboardButton(words["Accounts"]), KeyboardButton(words["Settings"]), KeyboardButton(words["Users"])],
        [KeyboardButton(words["Break"])],
        [KeyboardButton(words["AccountProfile"]), KeyboardButton(words["ActiveAds"])],
        [KeyboardButton(words["TransferBalance"]), KeyboardButton(words["PayoutBalance"])],
        [KeyboardButton(words["ContactSupport"]), KeyboardButton(words["CryptoOnline"])]
    ], resize_keyboard=True)

    downloader = ReplyKeyboardMarkup([
        [KeyboardButton(words["AccountProfile"]), KeyboardButton(words["ActiveAds"])],
        [KeyboardButton(words["TransferBalance"]), KeyboardButton(words["PayoutBalance"])],
        [KeyboardButton(words["ContactSupport"]), KeyboardButton(words["CryptoOnline"])]
    ], resize_keyboard=True)
