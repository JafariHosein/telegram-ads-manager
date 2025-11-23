import enum


class DownloaderState(str, enum.Enum):
    START = "in start menu"

    # Register
    GET_LINKED_USERNAME = "get linked username"

    # Login
    GET_CAPTCHA = "get captcha"
    GET_PASSWORD = "get password"
    GET_USERNAME = "get username"

    # New Ad
    ENTER_AD_CHANNEL_MESSAGE = "enter channel message"
    ENTER_AD_CAPACITY = "enter capacity"
    ENTER_AD_RATE = "enter rate"
    ENTER_AD_PRIZE = "enter prize"
    ENTER_AD_DESCRIPTION = "enter description"

    # Edit Ad
    EDIT_AD_RATE = "edit ad rate"
    EDIT_AD_CAPACITY = "edit ad capacity"
    EDIT_AD_PRIZE = "edit ad prize"
    EDIT_AD_DESCRIPTION = "edit ad description"

    # Search Ad
    SEARCH_WITH_CHANNEL_CHAT_ID = "search with channel chat id"
    SEARCH_WITH_AD_ID = "search with ad id"

    # Ad
    FROM_NEW_AD = "from new ad"
    FROM_VIEW_ALL_ADS = "from view all ads"
    FROM_VIEW_ACTIVE_ADS = "from view active ads"
    FROM_VIEW_INACTIVE_ADS = "from view inactive ads"
    FROM_VIEW_VERIFIED_ADS = "from view verified ads"
    FROM_VIEW_NOT_VERIFIED_ADS = "from view not verified ads"

    # Admin
    ENTER_REASON_FOR_REJECT = "enter reason for reject"
    ENTER_REASON_FOR_REJECT_TRANSFER = "enter reason for reject transfer"
    ENTER_REASON_FOR_REJECT_PAYOUT = "enter reason for reject payout"

    # New Username
    ENTER_NEW_USERNAME = "enter new username"

    # Manage Link
    ENTER_LINK_URL = "enter link url"

    # Transfer
    ENTER_ACCOUNT_ID = "enter account id"
    ENTER_ACCOUNT_USERNAME = "enter account username"
    ENTER_TRANSFER_VALUE = "enter transfer value"

    # Payout
    ENTER_PAYOUT_VALUE = "enter payout value"
    ENTER_WALLET_ADDRESS = "enter wallet address"

    # Bank Account
    ENTER_SHABA = "enter shaba"
    ENTER_CARD = "enter card"
    ENTER_FULL_NAME = "enter full name"

    # Setting
    EDIT_FINANCIAL_SUPPORT = "edit financial support"
    EDIT_ADVERTISING_SUPPORT = "edit advertising support"
    EDIT_MINIMUM_PAYOUT = "edit minimum payout"
    EDIT_LOG_CHANNEL_CHAT_ID = "edit log channel chat id"
    EDIT_MAIN_CHANNEL_CHAT_ID = "edit main channel chat id"
    EDIT_TRANSFER_WALLET_PRIVATE_KEY = "edit transfer wallet private key"
    EDIT_TRANSFER_WALLET_PUBLIC_KEY = "edit transfer wallet public key"
    ENTER_FORCE_JOIN_USERNAME = "enter force join username"

    # Accounts
    ENTER_ACCOUNT_SEARCH_TEXT = "enter account search text"
    ENTER_YOUR_MESSAGE_FOR_USER = "enter your message form user"
    ENTER_NEW_BALANCE = "enter new balance"

    # Users
    ENTER_GLOBAL_MESSAGE = "enter global message"
    ENTER_BLOCK_LIST = "enter block list"
    ENTER_USER_CHAT_ID = "enter user chat id"
    ENTER_YOUR_MESSAGE_FOR_PRIVATE = "enter your message form private"
