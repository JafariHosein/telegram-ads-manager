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

    # New Category
    ENTER_AD_CATEGORY_TITLE = "enter ad category title"
    ENTER_AD_CATEGORY_RATE = "enter ad category rate"

    # Edit Category
    EDIT_AD_CATEGORY_TITLE = "edit ad category title"
    EDIT_AD_CATEGORY_RATE = "edit ad category rate"

    # Admin
    ENTER_REASON_FOR_REJECT = "enter reason for reject"
    ENTER_REASON_FOR_REJECT_TRANSFER = "enter reason for reject transfer"

    # New Username
    ENTER_NEW_USERNAME = "enter new username"

    # Manage Link
    ENTER_LINK_URL = "enter link url"

    # Transfer
    ENTER_ACCOUNT_ID = "enter account id"
    ENTER_ACCOUNT_USERNAME = "enter account username"
    ENTER_TRANSFER_VALUE = "enter transfer value"

    # Bank Account
    ENTER_SHABA = "enter shaba"
    ENTER_CARD = "enter card"
