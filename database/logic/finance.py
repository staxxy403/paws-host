import uuid
from sqlalchemy import select

from database.core import async_session
from database.core import Transaction, User

from shared.enums import TransactionStatus, TransactionType


async def charge_user(
    user_id: uuid.UUID,
    amount: int,
    tx_type: TransactionType = TransactionType.VPS_PURCHASE,
    description: str | None = None
) -> Transaction:
    '''Charges the User, raises ValueError if amount of money is not enough'''
    if amount <= 0:
        raise ValueError('Amount must be greater than zero')

    stmt = select(User).where(User.id == user_id).with_for_update()

    async with async_session() as session:
        user = await session.scalar(stmt)
        if not user:
            raise ValueError('User not found')

        if user.balance < amount:
            raise ValueError('Not enough money, topup your balance first')

        user.balance -= amount

        tx = Transaction(
            user_id=user_id,
            amount=-amount,
            type=tx_type,
            status=TransactionStatus.COMPLETED,
            description=description
        )
        session.add(tx)
        await session.commit()
        await session.refresh(tx)
        return tx


async def credit_user(
    user_id: uuid.UUID,
    amount: int,
    tx_type: TransactionType = TransactionType.REFUND,
    description: str | None = None
) -> Transaction:
    '''Add funds to the User's balance'''
    if amount <= 0:
        raise ValueError('Amount must be greater than zero')

    stmt = select(User).where(User.id == user_id).with_for_update()

    async with async_session() as session:
        user = await session.scalar(stmt)
        if not user:
            raise ValueError('User not found')

        user.balance += amount

        tx = Transaction(
            user_id=user_id,
            amount=amount,
            type=tx_type,
            status=TransactionStatus.COMPLETED,
            description=description
        )
        session.add(tx)
        await session.commit()
        await session.refresh(tx)
        return tx


async def create_deposit_invoice(
    user_id: uuid.UUID,
    amount: int,
    provider: str,
    provider_payment_id: str | None = None,
    description: str | None = None
) -> Transaction:
    '''Creates a pending invoice. The User's balance does not change'''
    tx = Transaction(
        user_id=user_id,
        amount=amount,
        type=TransactionType.DEPOSIT,
        status=TransactionStatus.PENDING,
        provider=provider,
        provider_payment_id=provider_payment_id,
        description=description
    )

    async with async_session() as session:
        session.add(tx)
        await session.commit()
        await session.refresh(tx)
        return tx


async def confirm_deposit_invoice(provider_payment_id: str) -> Transaction:
    '''Confirms payment from merchant and add funds to the User'''

    tx_stmt = select(Transaction).where(Transaction.provider_payment_id == provider_payment_id).with_for_update()

    async with async_session() as session:
        tx = await session.scalar(tx_stmt)
        if not tx:
            raise ValueError('Transaction not found')

        if tx.status == TransactionStatus.COMPLETED:
            return tx

        if tx.status != TransactionStatus.PENDING:
            raise ValueError(f'Cant confirm transaction with status {tx.status}')

        user = await session.scalar(select(User).where(User.id == tx.user_id).with_for_update())
        user.balance += tx.amount
        tx.status = TransactionStatus.COMPLETED

        await session.commit()
        await session.refresh(tx)
        return tx
