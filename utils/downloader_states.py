import enum


class DownloaderState(str, enum.Enum):
    START = "in start menu"

    GET_LINKED_USERNAME = "get linked username"

    # Admin
    ENTER_REASON_FOR_REJECT = "enter reason for reject"
