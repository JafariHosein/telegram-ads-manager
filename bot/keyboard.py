from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from database.models.register_request import RegisterRequestStatusFarsi
from database.models.transfer_request import TransferRequestStatusFarsi
from database.crud.manager import Database
from database.crud.downloader_user import CRUDDownloaderUser
from utils.downloader_states import DownloaderState


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
        "Search": "🔎 جستجو",
        "See": "📪️ مشاهده",
        "Title": "🏷️ عنوان",
        "Rate": "💰 نرخ",
        "Normal": "🟢 عادی",
        "RequestType": "📩 درخواستی",
        "Enable": "✅ فعال",
        "SetEnable": "✅ فعال کردن",
        "Disable": "❌ غیر فعال",
        "SetDisable": "❌ غیر فعال کردن",
        "Skip": "⏩ رد کردن",
        "Done": "✅ انجام دادم",
        "SendToChannel": "📢 ارسال به چنل",
        "VerifyAd": "🧮 حسابرسی",
        "Details": "📋 جزئیات",
        "DownloadLink": "🔗 دریافت لینک",
        "ActiveAds": "🟢 تبلیغات فعال",
        "InActiveAds": "❌ تبلیغات غیر فعال",
        "NotVerifiedAds": "⚠️ تبلیغات حسابرسی نشده",
        "VerifiedAds": "✅ تبلیغات حسابرسی شده",
        "AllAds": "📚 تمام تبلیغات",
        "Prize": "🎖️ جایزه",
        "AutoComplete": "🤖 حسابرسی خودکار",
        "Capacity": "📦 ظرفیت",
        "Description": "📝 توضیحات",
        "WithChatID": "#️⃣ آیدی عددی کانال",
        "WithAdID": "📇 شماره تبلیغ",
        "SeePrize": "🎁 مشاهده جوایز",
        "SeeLeaderBoard": "📊 نفرات برتر",
        "DownloadSpecialLink": "🔗 دریافت لینک اختصاصی",
        "GoToMyProfile": "👤 رفتن به حساب کاربری",
        "MyLinks": "🔗 لینک ها",
        "MyChannels": "📢 یوزنیم ها",
        "MyHistory": "📜 سابقه",
        "MyBankAccounts": "🏦 حساب های بانکی",
        "ChangePassword": "🔒 تغییر رمز عبور",
        "Logout": "⏹️ خروج از حساب کاربری",
        "Yes": "✅ بله",
        "Verify": "📊 حسابرسی",
        "LinkUsers": "👥 مشاهده کاربران",
        "DeleteLink": "❌ حذف لینک",
        "WithAccountID": "🏷️ شماره اکانت",
        "WithUsername": "🔢 آیدی عددی",
        "Shaba": "شبا",
        "Card": "شماره کارت",
        "Tron": "🪙 ترون",
        "Rial": "💰 ریال",
        "TransferWalletBalance": "💰 موجودی ولت اتوماتیک",
        "ForceJoin": "📌 عضویت اجباری",
        "FinancialSupport": "💰 آیدی پشتببانی مالی",
        "AdvertisingSupport": "📢 آیدی پشتیبانی تبلیغات",
        "MinimumPayout": "💴 حداقل برداشت",
        "IsAutoTransfer": "🔁 تایید انتقال خودکار",
        "LogChannelChatId": "⚙️ کانال لاگ",
        "MainChannelChatId": "📡 کانال اصلی",
        "TransferWalletPrivateKey": "🔑 کلید ترون اتوماتیک",
        "TransferWalletPublicKey": "📥 آدرس ترون اتوماتیک",
        "ChangeStatus": "🔰 تغییر وضعیت",
        "SendMessageToAccount": "🚩 ارسال پیام به کاربر",
        "Balance": "💰 موجودی",
        "Role": "👤 نقش",
        "Status": "⚙️ وضعیت",
        "Ban": "🚫 بن",
        "Admin": "👑 ادمین",
        "Downloader": "📥 دانلودر",
        "GlobalMessage": "📢 پیام همگانی",
        "BlockList": "🚫 بلک لیست",
        "MoreAd": "✨ تبلیغات بیشتر",
        "Update": "♻️ بروزرسانی",
        "GetAdData": "⛓️ دریافت اطلاعات",
        "StatsAdNow": "🔰 آمار کنونی",
        "EditAdRate": "✍️ ادیت قیمت",
        "SetAdPrize": "🎁 تعیین جایزه",
        "RemoveAdPrize": "🎁 حذف جایزه",
        "DeleteAd": "🚫 حذف تبلیغ",
        "AdAvgPoint": "🔥 سنجش کیفیت لینک",
        "EditAdCapacity": "⏳ ادیت ظرفیت",
        "ReverseVerify": "حسابرسی معکوس",
        "TopFive": "پنج نفر اول"

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

    return_to_pending_transfer_requests = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{words["Return"]}", callback_data="ReturnToPendingTransferRequests")]
    ])

    return_to_pending_payout_requests = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{words["Return"]}", callback_data="ReturnToPendingPayoutRequests")]
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

    transfer_requests = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{TransferRequestStatusFarsi.PENDING.value}", callback_data="PendingTransferRequests")],
        [InlineKeyboardButton(f"{TransferRequestStatusFarsi.COMPLETED.value}", callback_data="CompletedTransferRequests")],
        [InlineKeyboardButton(f"{TransferRequestStatusFarsi.REJECTED.value}", callback_data="RejectedTransferRequests")],
        [InlineKeyboardButton(f"{words['Return']}", callback_data="ReturnToRequests")],
    ])

    payout_requests = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{TransferRequestStatusFarsi.PENDING.value}", callback_data="PendingPayoutRequests")],
        [InlineKeyboardButton(f"{TransferRequestStatusFarsi.COMPLETED.value}", callback_data="CompletedPayoutRequests")],
        [InlineKeyboardButton(f"{TransferRequestStatusFarsi.REJECTED.value}", callback_data="RejectedPayoutRequests")],
        [InlineKeyboardButton(f"{words['Return']}", callback_data="ReturnToRequests")],
    ])

    manage_ads = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{words["Add"]}", callback_data="AddNewAd")],
        [InlineKeyboardButton(f"{words["See"]}", callback_data="SeeAds"),
         InlineKeyboardButton(f"{words["Search"]}", callback_data="SearchAd")],
        [InlineKeyboardButton(f"{words["Return"]}", callback_data="ReturnToStart")]
    ])

    search_with = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{words["WithAdID"]}", callback_data="SearchWithAdID"),
         InlineKeyboardButton(f"{words["WithChatID"]}", callback_data="SearchWithChatID")],
        [InlineKeyboardButton(f"{words["Return"]}", callback_data="ReturnToManageAds")]
    ])

    choose_link_type_for_ad = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{words["Normal"]}", callback_data="ChooseThisLinkTypeForAd*NORMAL"), InlineKeyboardButton(f"{words["RequestType"]}", callback_data="ChooseThisLinkTypeForAd*REQUEST")]
    ])

    choose_auto_complete_for_ad = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{words["Enable"]}", callback_data="ChooseThisAutoCompleteForAd*True"), InlineKeyboardButton(f"{words["Disable"]}", callback_data="ChooseThisAutoCompleteForAd*False")]
    ])

    skip_prize_for_ad = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{words["Skip"]}", callback_data="SkipThisPrizeForAd")]
    ])

    submit_ad = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{words["Submit"]}", callback_data="SubmitThisAd")]
    ])

    i_admin_bot = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{words["Done"]}", callback_data="IAdminBotForThisAd")]
    ])

    all_ads = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{words["ActiveAds"]}", callback_data="ViewActiveAds"), InlineKeyboardButton(f"{words["InActiveAds"]}", callback_data="ViewInActiveAds")],
        [InlineKeyboardButton(f"{words["VerifiedAds"]}", callback_data="ViewVerifiedAds"), InlineKeyboardButton(f"{words["NotVerifiedAds"]}", callback_data="ViewNotVerifiedAds")],
        [InlineKeyboardButton(f"{words["AllAds"]}", callback_data="ViewAllAds")],
        [InlineKeyboardButton(f"{words["Return"]}", callback_data="ReturnToManageAds")]
    ])

    return_to_categories = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{words["Return"]}", callback_data="ReturnToCategories")]
    ])
    return_to_mange_ads = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{words["Return"]}", callback_data="ReturnToManageAds")]
    ])
    return_to_view_ads = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{words["Return"]}", callback_data="ReturnToViewAds")]
    ])

    return_to_ad_details = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{words["Return"]}", callback_data="ReturnToAdDetails")]
    ])

    account_profile = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{words["MyChannels"]}", callback_data="MyAccountChannels")],
        [InlineKeyboardButton(f"{words["MyHistory"]}", callback_data="MyAccountHistory"),
         InlineKeyboardButton(f"{words["MyBankAccounts"]}", callback_data="MyAccountBankAccounts")],
        [InlineKeyboardButton(f"{words["ChangePassword"]}", callback_data="ChangeMyPassword"),
         InlineKeyboardButton(f"{words["Logout"]}", callback_data="Logout")],
        [InlineKeyboardButton(f"{words["Return"]}", callback_data="ReturnToStart")]
    ])

    change_password_question = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{words["Yes"]}", callback_data="YesChangePassword")],
        [InlineKeyboardButton(f"{words["Return"]}", callback_data="ReturnToAccountProfile")]
    ])

    logout_question = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{words["Yes"]}", callback_data="YesLogout")],
        [InlineKeyboardButton(f"{words["Return"]}", callback_data="ReturnToAccountProfile")]
    ])

    return_to_account_profile = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{words["Return"]}", callback_data="ReturnToAccountProfile")]
    ])

    return_to_my_links = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{words["Return"]}", callback_data="MyAccountLinks")]
    ])

    no_linked_username = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{words["Add"]}", callback_data="AddAccountLinkedUsername")],
        [InlineKeyboardButton(f"{words["Return"]}", callback_data="ReturnToAccountProfile")]
    ])

    linked_username = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{words["Add"]}", callback_data="AddAccountLinkedUsername"),
         InlineKeyboardButton(f"{words["Delete"]}", callback_data="DeleteAccountLinkedUsername")],
        [InlineKeyboardButton(f"{words["Return"]}", callback_data="ReturnToAccountProfile")]
    ])

    return_to_usernames = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{words["Return"]}", callback_data="ReturnToUsernames")]
    ])

    return_to_active_ads = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{words["Return"]}", callback_data="ReturnToUserActiveAds")]
    ])

    return_to_transfer = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{words["Return"]}", callback_data="ReturnToTransfer")]
    ])

    view_link_menu = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{words["DeleteLink"]}", callback_data="DeleteThisLink"),
         InlineKeyboardButton(f"{words["LinkUsers"]}", callback_data="ViewThisLinkUsers")],
        [InlineKeyboardButton(f"{words["Return"]}", callback_data="ReturnToStart")]
    ])

    transfer_balance_menu = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{words["WithAccountID"]}", callback_data="TransferWithAccountID"),
         InlineKeyboardButton(f"{words["WithUsername"]}", callback_data="TransferWithUsername")],
        [InlineKeyboardButton(f"{words["Return"]}", callback_data="ReturnToStart")]
    ])

    submit_transfer_request = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{words["Submit"]}", callback_data="SubmitTransferRequest")],
        [InlineKeyboardButton(f"{words["Return"]}", callback_data="ReturnToTransfer")]
    ])

    my_bank_account_empty = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{words["Add"]}", callback_data="AddBankAccount")],
        [InlineKeyboardButton(f"{words["Return"]}", callback_data="ReturnToAccountProfile")]
    ])

    my_bank_account = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{words["Add"]}", callback_data="AddBankAccount")],
        [InlineKeyboardButton(f"{words["Delete"]}", callback_data="RemoveBankAccount")],
        [InlineKeyboardButton(f"{words["Return"]}", callback_data="ReturnToAccountProfile")]
    ])

    my_bank_account_type = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{words["Shaba"]}", callback_data="AddShabaBankAccount"),
         InlineKeyboardButton(f"{words["Card"]}", callback_data="AddCardBankAccount")],
        [InlineKeyboardButton(f"{words["Return"]}", callback_data="ReturnToBankAccount")]
    ])

    return_to_bank_account = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{words["Return"]}", callback_data="ReturnToBankAccount")]
    ])

    choose_payout_type = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{words["Tron"]}", callback_data="PayoutWithTron")],
        [InlineKeyboardButton(f"{words["Rial"]}", callback_data="PayoutWithRial")],
        [InlineKeyboardButton(f"{words["Return"]}", callback_data="ReturnToStart")]
    ])

    return_to_payout = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{words["Return"]}", callback_data="ReturnToPayout")]
    ])

    submit_payout_request = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{words["Submit"]}", callback_data="SubmitPayoutRequest")],
        [InlineKeyboardButton(f"{words["Return"]}", callback_data="ReturnToPayout")]
    ])

    setting_menu = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{words["Edit"]}", callback_data="EditSettings")],
        [InlineKeyboardButton(f"{words["TransferWalletBalance"]}", callback_data="ViewTransferWalletBalance"),
         InlineKeyboardButton(f"{words["ForceJoin"]}", callback_data="ForceJoin")],
        [InlineKeyboardButton(f"{words["Return"]}", callback_data="ReturnToStart")]
    ])

    edit_setting_menu = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{words["FinancialSupport"]}", callback_data="EditThisSetting*FinancialSupport"),
         InlineKeyboardButton(f"{words["AdvertisingSupport"]}", callback_data="EditThisSetting*AdvertisingSupport")],
        [InlineKeyboardButton(f"{words["MinimumPayout"]}", callback_data="EditThisSetting*MinimumPayout"),
         InlineKeyboardButton(f"{words["IsAutoTransfer"]}", callback_data="EditThisSetting*IsAutoTransfer")],
        [InlineKeyboardButton(f"{words["LogChannelChatId"]}", callback_data="EditThisSetting*LogChannelChatId"),
         InlineKeyboardButton(f"{words["MainChannelChatId"]}", callback_data="EditThisSetting*MainChannelChatId")],
        [InlineKeyboardButton(f"{words["TransferWalletPrivateKey"]}", callback_data="EditThisSetting*TransferWalletPrivateKey"),
         InlineKeyboardButton(f"{words["TransferWalletPublicKey"]}", callback_data="EditThisSetting*TransferWalletPublicKey")],
        [InlineKeyboardButton(f"{words["Return"]}", callback_data="ReturnToSettings")]
    ])

    edit_is_auto_transfer_to_enable = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{words["Enable"]}", callback_data="EnableIsAutoTransfer")],
        [InlineKeyboardButton(f"{words["Return"]}", callback_data="ReturnToSettings")]
    ])
    edit_is_auto_transfer_to_disable = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{words["Disable"]}", callback_data="DisableIsAutoTransfer")],
        [InlineKeyboardButton(f"{words["Return"]}", callback_data="ReturnToSettings")]
    ])

    return_to_settings = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{words["Return"]}", callback_data="ReturnToSettings")]
    ])

    force_join_empty = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{words["Add"]}", callback_data="AddForceJoinChannel")],
        [InlineKeyboardButton(f"{words["ChangeStatus"]}", callback_data="ChangeStatusForceJoinChannel")],
        [InlineKeyboardButton(f"{words["Return"]}", callback_data="ReturnToSettings")]
    ])
    force_join = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{words["Add"]}", callback_data="AddForceJoinChannel"),
         InlineKeyboardButton(f"{words["Delete"]}", callback_data="RemoveForceJoinChannel")],
        [InlineKeyboardButton(f"{words["ChangeStatus"]}", callback_data="ChangeStatusForceJoinChannel")],
        [InlineKeyboardButton(f"{words["Return"]}", callback_data="ReturnToSettings")]
    ])

    return_to_force_join = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{words["Return"]}", callback_data="ForceJoin")]
    ])

    account_menu = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{words["Edit"]}", callback_data="EditThisAccount"),
         InlineKeyboardButton(f"{words["ChangePassword"]}", callback_data="ChangeThisAccountPassword")],
        [InlineKeyboardButton(f"{words["SendMessageToAccount"]}", callback_data="SendMessageToThisAccount"),
         InlineKeyboardButton(f"{words["MyLinks"]}", callback_data="ViewLinksForThisAccount")],
        [InlineKeyboardButton(f"{words["Return"]}", callback_data="ReturnToAccounts")]
    ])

    account_menu_password_changed = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{words["Yes"]}", callback_data="SendNewPasswordToUser")],
        [InlineKeyboardButton(f"{words["Return"]}", callback_data="ReturnToSearchedAccount")]
    ])

    return_to_account_searched = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{words["Return"]}", callback_data="ReturnToSearchedAccount")]
    ])

    send_to_user = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{words["Yes"]}", callback_data="SendToThisAccount")],
        [InlineKeyboardButton(f"{words["Return"]}", callback_data="ReturnToSearchedAccount")]
    ])

    edit_account_menu = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{words["Balance"]}", callback_data="EditThisAccountBalance"),
         InlineKeyboardButton(f"{words["Role"]}", callback_data="EditThisAccountRole")],
        [InlineKeyboardButton(f"{words["Status"]}", callback_data="EditThisAccountStatus")],
        [InlineKeyboardButton(f"{words["Return"]}", callback_data="ReturnToSearchedAccount")]
    ])

    edit_account_status = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{words["Enable"]}", callback_data="ActiveThisAccount"),
         InlineKeyboardButton(f"{words["Ban"]}", callback_data="BanThisAccount")],
        [InlineKeyboardButton(f"{words["Return"]}", callback_data="ReturnToSearchedAccount")]
    ])

    edit_account_role = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{words["Admin"]}", callback_data="AdminThisAccount"),
         InlineKeyboardButton(f"{words["Downloader"]}", callback_data="DownloaderThisAccount")],
        [InlineKeyboardButton(f"{words["Return"]}", callback_data="ReturnToSearchedAccount")]
    ])

    users_menu = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{words["GlobalMessage"]}", callback_data="GlobalMessage"),
         InlineKeyboardButton(f"{words["SendMessageToAccount"]}", callback_data="SendMessageToUser")],
        [InlineKeyboardButton(f"{words["BlockList"]}", callback_data="BlockList")],
        [InlineKeyboardButton(f"{words["Return"]}", callback_data="ReturnToStart")]
    ])

    return_to_users = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{words["Return"]}", callback_data="ReturnToUsers")]
    ])

    users_global_message = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{words["Yes"]}", callback_data="SendThisGlblMessage")],
        [InlineKeyboardButton(f"{words["Return"]}", callback_data="ReturnToUsers")]
    ])

    user_private_message = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{words["Yes"]}", callback_data="SendThisPrivateMessage")],
        [InlineKeyboardButton(f"{words["Return"]}", callback_data="ReturnToUsers")]
    ])

    block_list_empty = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{words["Add"]}", callback_data="AddUserToBlockList")],
        [InlineKeyboardButton(f"{words["Return"]}", callback_data="ReturnToUsers")]
    ])

    block_list = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{words["Add"]}", callback_data="AddUserToBlockList"),
         InlineKeyboardButton(f"{words["Delete"]}", callback_data="RemoveUserToBlockList")],
        [InlineKeyboardButton(f"{words["Return"]}", callback_data="ReturnToUsers")]
    ])

    return_block_list = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{words["Return"]}", callback_data="BlockList")]
    ])

    more_ad = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{words["MoreAd"]}", callback_data="MoreAd")]
    ])

    more_history_ad = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{words["MoreAd"]}", callback_data="MoreHistoryAd")]
    ])

    @staticmethod
    def history_ad(ad_id: int):
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(f"{DownloaderInlineButtons.words["TopFive"]}", callback_data=f"TopFiveThisAd*{ad_id}"),
             InlineKeyboardButton(f"{DownloaderInlineButtons.words["StatsAdNow"]}", callback_data=f"ThisAdStatsAdNow*{ad_id}")],
            [InlineKeyboardButton(f"{DownloaderInlineButtons.words["GetAdData"]}", callback_data=f"ThisAdGetAdData*{ad_id}"),
             InlineKeyboardButton(f"{DownloaderInlineButtons.words["ReverseVerify"]}", callback_data=f"ReverseVerify*{ad_id}")]
        ])

    @staticmethod
    def ad_status_menu(ad_id: int):
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(f"{DownloaderInlineButtons.words["GetAdData"]}", callback_data=f"ThisAdGetAdData*{ad_id}"),
             InlineKeyboardButton(f"{DownloaderInlineButtons.words["StatsAdNow"]}", callback_data=f"ThisAdStatsAdNow*{ad_id}")],
            [InlineKeyboardButton(f"{DownloaderInlineButtons.words["Verify"]}", callback_data=f"ThisAdVerify*{ad_id}")],
            [InlineKeyboardButton(f"{DownloaderInlineButtons.words["EditAdRate"]}", callback_data=f"ThisAdEditAdRate*{ad_id}"),
             InlineKeyboardButton(f"{DownloaderInlineButtons.words["EditAdCapacity"]}", callback_data=f"ThisAdEditAdCapacity*{ad_id}")],
            [InlineKeyboardButton(f"{DownloaderInlineButtons.words["RemoveAdPrize"]}", callback_data=f"ThisAdRemoveAdPrize*{ad_id}"),
             InlineKeyboardButton(f"{DownloaderInlineButtons.words["SetAdPrize"]}", callback_data=f"ThisAdSetAdPrize*{ad_id}")],
            [InlineKeyboardButton(f"{DownloaderInlineButtons.words["DeleteAd"]}", callback_data=f"ThisAdDeleteAd*{ad_id}"),
             InlineKeyboardButton(f"{DownloaderInlineButtons.words["SendToChannel"]}", callback_data=f"ThisAdSendToChannel*{ad_id}")],
            [InlineKeyboardButton(f"{DownloaderInlineButtons.words["AdAvgPoint"]}", callback_data=f"ThisAdAdAvgPoint*{ad_id}")],

        ])

    @staticmethod
    def my_ads_menu(link_id: int):
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(f"{DownloaderInlineButtons.words["SeeLeaderBoard"]}", callback_data=f"SeeLeaderBoardThisMyAd*{link_id}"),
             InlineKeyboardButton(f"{DownloaderInlineButtons.words["Description"]}", callback_data=f"SeeDescriptionThisMyAd*{link_id}")],
            [InlineKeyboardButton(f"{DownloaderInlineButtons.words["Update"]}", callback_data=f"UpdateThisMyAd*{link_id}")]
        ])

    @staticmethod
    def return_to_view_link_menu(link_id: int):
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(f"{DownloaderInlineButtons.words["Return"]}", callback_data=f"ReturnToViewLinkMenu*{link_id}")],
        ])

    @staticmethod
    def get_active_ad_menu(ad_id: int, with_ad: bool = True):
        if not with_ad:
            return InlineKeyboardMarkup([
                [InlineKeyboardButton(f"{DownloaderInlineButtons.words["SeeLeaderBoard"]}", callback_data=f"SeeLeaderBoardOfThisAd*{ad_id}")],
                [InlineKeyboardButton(f"{DownloaderInlineButtons.words["DownloadSpecialLink"]}", callback_data=f"DownloadLinkOfThisAd*{ad_id}")]
            ])
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(f"{DownloaderInlineButtons.words["SeePrize"]}", callback_data=f"SeePrizeOfThisAd*{ad_id}"),
             InlineKeyboardButton(f"{DownloaderInlineButtons.words["SeeLeaderBoard"]}", callback_data=f"SeeLeaderBoardOfThisAd*{ad_id}")],
            [InlineKeyboardButton(f"{DownloaderInlineButtons.words["DownloadSpecialLink"]}", callback_data=f"DownloadLinkOfThisAd*{ad_id}")]
        ])

    @staticmethod
    def get_edit_ads_menu(ad_id: int) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(f"{DownloaderInlineButtons.words["Rate"]}", callback_data=f"EditDataThisAdd*{ad_id}*rate"),
             InlineKeyboardButton(f"{DownloaderInlineButtons.words["Prize"]}", callback_data=f"EditDataThisAdd*{ad_id}*prize")],
            [InlineKeyboardButton(f"{DownloaderInlineButtons.words["AutoComplete"]}", callback_data=f"EditDataThisAdd*{ad_id}*autocomplete"),
             InlineKeyboardButton(f"{DownloaderInlineButtons.words["Capacity"]}", callback_data=f"EditDataThisAdd*{ad_id}*capacity")],
            [InlineKeyboardButton(f"{DownloaderInlineButtons.words["Description"]}", callback_data=f"EditDataThisAdd*{ad_id}*description")],
            [InlineKeyboardButton(f"{DownloaderInlineButtons.words["Return"]}", callback_data=f"ViewThisAd*{ad_id}")]
        ])

    @staticmethod
    def get_ad_details_menu(ad_id: int, start: bool = False, center: bool = False, end: bool = False) -> InlineKeyboardMarkup:
        if start:
            return InlineKeyboardMarkup([
                [InlineKeyboardButton(f"{DownloaderInlineButtons.words["NextPage"]}", callback_data=f"GoToNextViewAdDetails*{ad_id}")],
                [InlineKeyboardButton(f"{DownloaderInlineButtons.words["Return"]}", callback_data=f"ViewThisAd*{ad_id}")]
            ])
        elif center:
            return InlineKeyboardMarkup([
                [InlineKeyboardButton(f"{DownloaderInlineButtons.words["NextPage"]}", callback_data=f"GoToNextViewAdDetails*{ad_id}"),
                 InlineKeyboardButton(f"{DownloaderInlineButtons.words["PreviousPage"]}", callback_data=f"GoToPreviousViewAdDetails*{ad_id}")],
                [InlineKeyboardButton(f"{DownloaderInlineButtons.words["Return"]}", callback_data=f"ViewThisAd*{ad_id}")]
            ])
        elif end:
            return InlineKeyboardMarkup([
                [InlineKeyboardButton(f"{DownloaderInlineButtons.words["PreviousPage"]}", callback_data=f"GoToPreviousViewAdDetails*{ad_id}")],
                [InlineKeyboardButton(f"{DownloaderInlineButtons.words["Return"]}", callback_data=f"ViewThisAd*{ad_id}")]
            ])

        return InlineKeyboardMarkup([
            [InlineKeyboardButton(f"{DownloaderInlineButtons.words["Return"]}", callback_data=f"ViewThisAd*{ad_id}")]
        ])

    @staticmethod
    def get_return_to_view_ad(ad_id: int) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(f"{DownloaderInlineButtons.words["Return"]}", callback_data=f"ViewThisAd*{ad_id}")]
        ])

    @staticmethod
    def get_return_to_edit_ad(ad_id: int, clear_prize: bool = False, auto_complete: bool = False) -> InlineKeyboardMarkup:

        if clear_prize:
            return InlineKeyboardMarkup([
                [InlineKeyboardButton(f"{DownloaderInlineButtons.words["Delete"]}", callback_data=f"ClearPrizeForThisAd*{ad_id}")],
                [InlineKeyboardButton(f"{DownloaderInlineButtons.words["Return"]}", callback_data=f"EditThisAd*{ad_id}")]
            ])

        if auto_complete:
            return InlineKeyboardMarkup([
                [InlineKeyboardButton(f"{DownloaderInlineButtons.words["Enable"]}", callback_data=f"EnableAutoCompleteForThisAdd*{ad_id}"),
                 InlineKeyboardButton(f"{DownloaderInlineButtons.words["Disable"]}", callback_data=f"DisableAutoCompleteForThisAdd*{ad_id}")],
                [InlineKeyboardButton(f"{DownloaderInlineButtons.words["Return"]}", callback_data=f"EditThisAd*{ad_id}")]
            ])

        return InlineKeyboardMarkup([
            [InlineKeyboardButton(f"{DownloaderInlineButtons.words["Return"]}", callback_data=f"EditThisAd*{ad_id}")]
        ])

    @staticmethod
    def get_ad_menu(ad_id: int, chat_id: str, is_active: bool) -> InlineKeyboardMarkup:
        with Database.get_session() as session:
            state = CRUDDownloaderUser.get_by_chat_id(session, chat_id).state

        if state == DownloaderState.FROM_NEW_AD:
            return InlineKeyboardMarkup([
                [InlineKeyboardButton(f"{DownloaderInlineButtons.words["SendToChannel"]}", callback_data=f"SendThisAdToChannel*{ad_id}"),
                 InlineKeyboardButton(f"{DownloaderInlineButtons.words["Details"]}", callback_data=f"ViewDetailsThisAd*{ad_id}")],
                [InlineKeyboardButton(f"{DownloaderInlineButtons.words["Edit"]}", callback_data=f"EditThisAd*{ad_id}"),
                 InlineKeyboardButton(f"{DownloaderInlineButtons.words["Delete"]}", callback_data=f"DeleteThisAd*{ad_id}")],
                [InlineKeyboardButton(f"{DownloaderInlineButtons.words["SetDisable"] if is_active else DownloaderInlineButtons.words["SetEnable"]}",
                                      callback_data=f"DisableThisAd*{ad_id}" if is_active else f"EnableThisAd*{ad_id}")],
                [InlineKeyboardButton(f"{DownloaderInlineButtons.words["Verify"]}", callback_data=f"VerifyThisAd*{ad_id}")]
            ])
        elif state == DownloaderState.FROM_VIEW_ALL_ADS:
            return InlineKeyboardMarkup([
                [InlineKeyboardButton(f"{DownloaderInlineButtons.words["SendToChannel"]}", callback_data=f"SendThisAdToChannel*{ad_id}"),
                 InlineKeyboardButton(f"{DownloaderInlineButtons.words["Details"]}", callback_data=f"ViewDetailsThisAd*{ad_id}")],
                [InlineKeyboardButton(f"{DownloaderInlineButtons.words["Edit"]}", callback_data=f"EditThisAd*{ad_id}"),
                 InlineKeyboardButton(f"{DownloaderInlineButtons.words["Delete"]}", callback_data=f"DeleteThisAd*{ad_id}")],
                [InlineKeyboardButton(f"{DownloaderInlineButtons.words["SetDisable"] if is_active else DownloaderInlineButtons.words["SetEnable"]}",
                                      callback_data=f"DisableThisAd*{ad_id}" if is_active else f"EnableThisAd*{ad_id}")],
                [InlineKeyboardButton(f"{DownloaderInlineButtons.words["Verify"]}", callback_data=f"VerifyThisAd*{ad_id}")]
            ])
        elif state == DownloaderState.FROM_VIEW_ACTIVE_ADS:
            return InlineKeyboardMarkup([
                [InlineKeyboardButton(f"{DownloaderInlineButtons.words["SendToChannel"]}", callback_data=f"SendThisAdToChannel*{ad_id}"),
                 InlineKeyboardButton(f"{DownloaderInlineButtons.words["Details"]}", callback_data=f"ViewDetailsThisAd*{ad_id}")],
                [InlineKeyboardButton(f"{DownloaderInlineButtons.words["Edit"]}", callback_data=f"EditThisAd*{ad_id}"),
                 InlineKeyboardButton(f"{DownloaderInlineButtons.words["Delete"]}", callback_data=f"DeleteThisAd*{ad_id}")],
                [InlineKeyboardButton(f"{DownloaderInlineButtons.words["SetDisable"] if is_active else DownloaderInlineButtons.words["SetEnable"]}",
                                      callback_data=f"DisableThisAd*{ad_id}" if is_active else f"EnableThisAd*{ad_id}")],
                [InlineKeyboardButton(f"{DownloaderInlineButtons.words["Verify"]}", callback_data=f"VerifyThisAd*{ad_id}")]
            ])
        elif state == DownloaderState.FROM_VIEW_INACTIVE_ADS:
            return InlineKeyboardMarkup([
                [InlineKeyboardButton(f"{DownloaderInlineButtons.words["SendToChannel"]}", callback_data=f"SendThisAdToChannel*{ad_id}"),
                 InlineKeyboardButton(f"{DownloaderInlineButtons.words["Details"]}", callback_data=f"ViewDetailsThisAd*{ad_id}")],
                [InlineKeyboardButton(f"{DownloaderInlineButtons.words["Edit"]}", callback_data=f"EditThisAd*{ad_id}"),
                 InlineKeyboardButton(f"{DownloaderInlineButtons.words["Delete"]}", callback_data=f"DeleteThisAd*{ad_id}")],
                [InlineKeyboardButton(f"{DownloaderInlineButtons.words["SetDisable"] if is_active else DownloaderInlineButtons.words["SetEnable"]}",
                                      callback_data=f"DisableThisAd*{ad_id}" if is_active else f"EnableThisAd*{ad_id}")],
                [InlineKeyboardButton(f"{DownloaderInlineButtons.words["Verify"]}", callback_data=f"VerifyThisAd*{ad_id}")]
            ])
        elif state == DownloaderState.FROM_VIEW_VERIFIED_ADS:
            return InlineKeyboardMarkup([
                [InlineKeyboardButton(f"{DownloaderInlineButtons.words["SendToChannel"]}", callback_data=f"SendThisAdToChannel*{ad_id}"),
                 InlineKeyboardButton(f"{DownloaderInlineButtons.words["Details"]}", callback_data=f"ViewDetailsThisAd*{ad_id}")],
                [InlineKeyboardButton(f"{DownloaderInlineButtons.words["Edit"]}", callback_data=f"EditThisAd*{ad_id}"),
                 InlineKeyboardButton(f"{DownloaderInlineButtons.words["Delete"]}", callback_data=f"DeleteThisAd*{ad_id}")],
                [InlineKeyboardButton(f"{DownloaderInlineButtons.words["SetDisable"] if is_active else DownloaderInlineButtons.words["SetEnable"]}",
                                      callback_data=f"DisableThisAd*{ad_id}" if is_active else f"EnableThisAd*{ad_id}")],
                [InlineKeyboardButton(f"{DownloaderInlineButtons.words["Verify"]}", callback_data=f"VerifyThisAd*{ad_id}")]
            ])
        elif state == DownloaderState.FROM_VIEW_NOT_VERIFIED_ADS:
            return InlineKeyboardMarkup([
                [InlineKeyboardButton(f"{DownloaderInlineButtons.words["SendToChannel"]}", callback_data=f"SendThisAdToChannel*{ad_id}"),
                 InlineKeyboardButton(f"{DownloaderInlineButtons.words["Details"]}", callback_data=f"ViewDetailsThisAd*{ad_id}")],
                [InlineKeyboardButton(f"{DownloaderInlineButtons.words["Edit"]}", callback_data=f"EditThisAd*{ad_id}"),
                 InlineKeyboardButton(f"{DownloaderInlineButtons.words["Delete"]}", callback_data=f"DeleteThisAd*{ad_id}")],
                [InlineKeyboardButton(f"{DownloaderInlineButtons.words["SetDisable"] if is_active else DownloaderInlineButtons.words["SetEnable"]}",
                                      callback_data=f"DisableThisAd*{ad_id}" if is_active else f"EnableThisAd*{ad_id}")],
                [InlineKeyboardButton(f"{DownloaderInlineButtons.words["Verify"]}", callback_data=f"VerifyThisAd*{ad_id}")]
            ])
        elif state in [DownloaderState.SEARCH_WITH_AD_ID, DownloaderState.SEARCH_WITH_CHANNEL_CHAT_ID]:
            return InlineKeyboardMarkup([
                [InlineKeyboardButton(f"{DownloaderInlineButtons.words["SendToChannel"]}", callback_data=f"SendThisAdToChannel*{ad_id}"),
                 InlineKeyboardButton(f"{DownloaderInlineButtons.words["Details"]}", callback_data=f"ViewDetailsThisAd*{ad_id}")],
                [InlineKeyboardButton(f"{DownloaderInlineButtons.words["Edit"]}", callback_data=f"EditThisAd*{ad_id}"),
                 InlineKeyboardButton(f"{DownloaderInlineButtons.words["Delete"]}", callback_data=f"DeleteThisAd*{ad_id}")],
                [InlineKeyboardButton(f"{DownloaderInlineButtons.words["SetDisable"] if is_active else DownloaderInlineButtons.words["SetEnable"]}",
                                      callback_data=f"DisableThisAd*{ad_id}" if is_active else f"EnableThisAd*{ad_id}")],
                [InlineKeyboardButton(f"{DownloaderInlineButtons.words["Verify"]}", callback_data=f"VerifyThisAd*{ad_id}")]
            ])

    @staticmethod
    def make_inline_table_separated(columns: list[str], rows: list[list], prefix: str = "cell") -> InlineKeyboardMarkup:
        """
        :param columns: لیست نام ستون‌ها (برای دکمه‌ها میشه همون نام ستون یا داده استفاده بشه)
        :param rows: لیست داده‌ها
        :param prefix: پیشوند callback_data برای هر دکمه
        :return: InlineKeyboardMarkup
        """
        keyboard = []
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        header_buttons = [
            InlineKeyboardButton(text=str(col), callback_data=f"nothing")
            for i, col in enumerate(columns)
        ]
        keyboard.append(header_buttons)

        keyboard.append([InlineKeyboardButton(text="▬▬▬▬▬▬" * len(columns), callback_data=f"nothing")])

        for row_idx, row in enumerate(rows):
            row_buttons = []
            for col_idx, cell in enumerate(row):
                text = str(cell)
                callback = f"nothing"
                row_buttons.append(InlineKeyboardButton(text=text, callback_data=callback))
            keyboard.append(row_buttons)

        keyboard.append([InlineKeyboardButton(text="▬▬▬▬▬▬" * len(columns), callback_data=f"nothing")])

        return InlineKeyboardMarkup(keyboard)


class DownloaderReplyButtons:
    words = {
        "Register": "📝 ثبت‌ نام",
        "Login": "🔑 ورود",
        "ContactSupport": "📞 ارتباط با پشتیبانی",
        "AdsStatus": "📊 وضعیت تبلیغ",
        "Stats": "📈 آمار کامل ربات",
        "LinkManager": "✍️ مدیریت لینک",
        "Requests": "♦️ درخواست ها",
        "Users": "👥 کاربران",
        "Accounts": "💼 اکانت ها",
        "CreateAd": "🔰 ثبت تبلیغ",
        "Settings": "🛠️ تنظیمات",
        "CryptoOnline": "💰 قیمت لحظه ایی",
        "History": "📆 سوابق اجرا",
        "AccountProfile": "👤 حساب کاربری",
        "ActiveAds": "✅ تبلیغ های فعال",
        "TransferBalance": "🔁 انتقال",
        "PayoutBalance": "💵 برداشت",
        "MyAds": "📊 تبلیغ های من",
        "RegisterMember": "🛒 ثبت سفارش ممبر"
    }

    new_user = ReplyKeyboardMarkup([
        [KeyboardButton(words["Login"]), KeyboardButton(words["Register"])],
        [KeyboardButton(words["ContactSupport"])]
    ], resize_keyboard=True)

    admin = ReplyKeyboardMarkup([
        [KeyboardButton(words["AdsStatus"]), KeyboardButton(words["CreateAd"])],
        [KeyboardButton(words["Requests"]), KeyboardButton(words["Stats"])],
        [KeyboardButton(words["LinkManager"]), KeyboardButton(words["History"])],
        [KeyboardButton(words["Settings"]), KeyboardButton(words["AccountProfile"])],
        [KeyboardButton(words["Accounts"]), KeyboardButton(words["Users"])],
        [KeyboardButton(words["ContactSupport"]), KeyboardButton(words["CryptoOnline"])],
    ], resize_keyboard=True)

    downloader = ReplyKeyboardMarkup([
        [KeyboardButton(words["MyAds"]), KeyboardButton(words["ActiveAds"])],
        [KeyboardButton(words["RegisterMember"]), KeyboardButton(words["AccountProfile"])],
        [KeyboardButton(words["TransferBalance"]), KeyboardButton(words["PayoutBalance"])],
        [KeyboardButton(words["ContactSupport"]), KeyboardButton(words["CryptoOnline"])]
    ], resize_keyboard=True)
