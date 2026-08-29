import time
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from shared.enums import VPSStatus


class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(unique=True, index=True)
    balance: Mapped[int] = mapped_column(default=0)
    registered_at: Mapped[int] = mapped_column(default=lambda: int(time.time()))

    vps_list: Mapped[list['VPS']] = relationship(back_populates='owner')

class Node(Base):
    __tablename__ = 'nodes'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    country_code: Mapped[str] = mapped_column(String(2))

    parent_interface: Mapped[str] = mapped_column(String(20), default="eth0")

    ip_address: Mapped[str] = mapped_column(String(50))
    api_port: Mapped[int] = mapped_column(default=8443)

    is_active: Mapped[bool] = mapped_column(default=True)

    max_ram_gb: Mapped[int] = mapped_column()
    cpu_cores: Mapped[int] = mapped_column()
    max_vms: Mapped[int] = mapped_column(default=30)

    vps_list: Mapped[list['VPS']] = relationship(back_populates='node')
    ip_pool: Mapped[list['IPAddress']] = relationship(back_populates='node')

class IPAddress(Base):
    __tablename__ = 'ip_addresses'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ip: Mapped[str] = mapped_column(String(15), unique=True, index=True)
    gateway: Mapped[str] = mapped_column(String(15))
    netmask: Mapped[str] = mapped_column(String(15))

    is_allocated: Mapped[bool] = mapped_column(default=False)

    node_id: Mapped[int] = mapped_column(ForeignKey('nodes.id'))
    node: Mapped['Node'] = relationship(back_populates='ip_pool')

    vps: Mapped['VPS | None'] = relationship(back_populates='ip_address')

class VPS(Base):
    __tablename__ = 'vps'

    id: Mapped[int] = mapped_column(primary_key=True)
    uuid: Mapped[str] = mapped_column(unique=True)

    status: Mapped[VPSStatus] = mapped_column(default=VPSStatus.CREATING)

    cpu_cores: Mapped[int] = mapped_column()
    ram_gb: Mapped[int] = mapped_column()
    disk_gb: Mapped[int] = mapped_column()

    expire_at: Mapped[int] = mapped_column()

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    owner: Mapped['User'] = relationship(back_populates='vps_list')

    node_id: Mapped[int] = mapped_column(ForeignKey('nodes.id'))
    node: Mapped['Node'] = relationship(back_populates='vps_list')

    ip_id: Mapped[int] = mapped_column(ForeignKey('ip_addresses.id'))
    ip_address: Mapped['IPAddress'] = relationship(back_populates='vps')

    os_id: Mapped[int] = mapped_column(ForeignKey('os.id'))
    os: Mapped['OS'] = relationship(back_populates='vps')

class OS(Base):
    __tablename__ = 'os'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    display_name: Mapped[str] = mapped_column(String(50))
    incus_name: Mapped[str] = mapped_column(String(50))

    vps: Mapped[list['VPS']] = relationship(back_populates='os')
