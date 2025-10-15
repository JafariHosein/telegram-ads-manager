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

    # New Category
    ENTER_AD_CATEGORY_TITLE = "enter ad category title"
    ENTER_AD_CATEGORY_RATE = "enter ad category rate"

    # Edit Category
    EDIT_AD_CATEGORY_TITLE = "edit ad category title"
    EDIT_AD_CATEGORY_RATE = "edit ad category rate"

    # Admin
    ENTER_REASON_FOR_REJECT = "enter reason for reject"
