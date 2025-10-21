from sqlalchemy.orm import Session
from sqlalchemy import select

from database.models.setting import Setting


class CRUDSetting:

    @staticmethod
    def init(db: Session):
        if not CRUDSetting.__exist(db):
            db.add(Setting())
            db.commit()

    @staticmethod
    def __exist(db: Session) -> bool:
        statement = select(Setting)
        result = db.execute(statement).scalars().all()

        if result:
            return True
        else:
            return False

    @staticmethod
    def get_all(db: Session) -> Setting:
        statement = select(Setting)
        return db.execute(statement).scalars().first()

    @staticmethod
    def get_main_wallet_address(db: Session) -> str:
        statement = select(Setting)
        return db.execute(statement).scalars().all()[0].main_wallet_address

    @staticmethod
    def get_fee(db: Session) -> int:
        statement = select(Setting)
        return db.execute(statement).scalars().all()[0].fee

    @staticmethod
    def get_financial_support(db: Session) -> str:
        statement = select(Setting)
        return db.execute(statement).scalars().all()[0].financial_support

    @staticmethod
    def get_advertising_support(db: Session) -> str:
        statement = select(Setting)
        return db.execute(statement).scalars().all()[0].advertising_support

    @staticmethod
    def get_forced_join_text(db: Session) -> str:
        statement = select(Setting)
        return db.execute(statement).scalars().all()[0].forced_join_text

    @staticmethod
    def get_is_forced_join_active(db: Session) -> bool:
        statement = select(Setting)
        return db.execute(statement).scalars().all()[0].is_forced_join_active

    @staticmethod
    def get_minimum_payout(db: Session) -> int:
        statement = select(Setting)
        return db.execute(statement).scalars().all()[0].minimum_payout

    @staticmethod
    def get_is_auto_transfer(db: Session) -> bool:
        statement = select(Setting)
        return db.execute(statement).scalars().all()[0].is_auto_transfer

    @staticmethod
    def get_transfer_wallet_private_key(db: Session) -> str:
        statement = select(Setting)
        return db.execute(statement).scalars().all()[0].transfer_wallet_private_key

    @staticmethod
    def get_transfer_wallet_public_key(db: Session) -> str:
        statement = select(Setting)
        return db.execute(statement).scalars().all()[0].transfer_wallet_public_key

    @staticmethod
    def get_transfer_wallet_balance(db: Session) -> float:
        statement = select(Setting)
        return db.execute(statement).scalars().all()[0].transfer_wallet_balance

    @staticmethod
    def get_log_channel_chat_id(db: Session) -> str:
        statement = select(Setting)
        return db.execute(statement).scalars().all()[0].log_channel_chat_id

    @staticmethod
    def get_main_channel_chat_id(db: Session) -> str:
        statement = select(Setting)
        return db.execute(statement).scalars().all()[0].main_channel_chat_id

    @staticmethod
    def update_main_wallet_address(db: Session, new_main_wallet_address: str):
        record = db.scalars(select(Setting)).first()
        record.main_wallet_address = new_main_wallet_address
        db.commit()

    @staticmethod
    def update_fee(db: Session, new_fee: int):
        record = db.scalars(select(Setting)).first()
        record.fee = new_fee
        db.commit()

    @staticmethod
    def update_financial_support(db: Session, new_financial_support: str):
        record = db.scalars(select(Setting)).first()
        record.financial_support = new_financial_support
        db.commit()

    @staticmethod
    def update_advertising_support(db: Session, new_advertising_support: str):
        record = db.scalars(select(Setting)).first()
        record.advertising_support = new_advertising_support
        db.commit()

    @staticmethod
    def update_forced_join_text(db: Session, new_forced_join_text: str):
        record = db.scalars(select(Setting)).first()
        record.forced_join_text = new_forced_join_text
        db.commit()

    @staticmethod
    def update_is_forced_join_active(db: Session, new_is_forced_join_active: bool):
        record = db.scalars(select(Setting)).first()
        record.is_forced_join_active = new_is_forced_join_active
        db.commit()

    @staticmethod
    def update_minimum_payout(db: Session, new_minimum_payout: int):
        record = db.scalars(select(Setting)).first()
        record.minimum_payout = new_minimum_payout
        db.commit()

    @staticmethod
    def update_is_auto_transfer(db: Session, new_is_auto_transfer: bool):
        record = db.scalars(select(Setting)).first()
        record.is_auto_transfer = new_is_auto_transfer
        db.commit()

    @staticmethod
    def update_transfer_wallet_private_key(db: Session, new_transfer_wallet_private_key: str):
        record = db.scalars(select(Setting)).first()
        record.transfer_wallet_private_key = new_transfer_wallet_private_key
        db.commit()

    @staticmethod
    def update_transfer_wallet_public_key(db: Session, new_transfer_wallet_public_key: str):
        record = db.scalars(select(Setting)).first()
        record.transfer_wallet_public_key = new_transfer_wallet_public_key
        db.commit()

    @staticmethod
    def update_transfer_wallet_balance(db: Session, new_transfer_wallet_balance: float):
        record = db.scalars(select(Setting)).first()
        record.transfer_wallet_balance = new_transfer_wallet_balance
        db.commit()

    @staticmethod
    def update_log_channel_chat_id(db: Session, new_log_channel_chat_id: str):
        record = db.scalars(select(Setting)).first()
        record.log_channel_chat_id = new_log_channel_chat_id
        db.commit()

    @staticmethod
    def update_main_channel_chat_id(db: Session, new_main_channel_chat_id: str):
        record = db.scalars(select(Setting)).first()
        record.main_channel_chat_id = new_main_channel_chat_id
        db.commit()
