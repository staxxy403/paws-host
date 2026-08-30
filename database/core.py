import time
import os

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

DATABASE_URL = os.getenv('DATABASE_URL')

engine = create_async_engine(DATABASE_URL)
async_session = async_sessionmaker(engine, expire_on_commit=False)

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

    parent_interface: Mapped[str] = mapped_column(String(20), default="eth0")

    ip_address: Mapped[str] = mapped_column(String(50))
    api_port: Mapped[int] = mapped_column(default=8443)

    is_active: Mapped[bool] = mapped_column(default=True)

    max_ram_gb: Mapped[int] = mapped_column()
    cpu_cores: Mapped[int] = mapped_column()
    max_vms: Mapped[int] = mapped_column(default=30)

    vps_list: Mapped[list['VPS']] = relationship(back_populates='node')
    ip_pool: Mapped[list['IPAddress']] = relationship(back_populates='node')

    location_id: Mapped[int] = mapped_column(ForeignKey('locations.id'))
    location: Mapped['Location'] = relationship(back_populates='nodes')

    category_id: Mapped[int] = mapped_column(ForeignKey('categories.id'))
    category: Mapped['Category'] = relationship(back_populates='nodes')

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

    tariff_id: Mapped[int] = mapped_column(ForeignKey('tariffs.id'))
    tariff: Mapped['Tariff'] = relationship(back_populates='vps_list')

class OS(Base):
    __tablename__ = 'os'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    display_name: Mapped[str] = mapped_column(String(50))
    incus_name: Mapped[str] = mapped_column(String(50))

    vps: Mapped[list['VPS']] = relationship(back_populates='os')

class Tariff(Base):
    __tablename__ = 'tariffs'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    disk_gb: Mapped[int] = mapped_column()
    ram_gb: Mapped[int] = mapped_column()
    cpu_cores: Mapped[int] = mapped_column()

    price: Mapped[int] = mapped_column()
    is_active: Mapped[bool] = mapped_column(default=True)

    category_id: Mapped[int] = mapped_column(ForeignKey('categories.id'))
    category: Mapped['Category'] = relationship(back_populates='tariffs')

    vps_list: Mapped[list[VPS]] = relationship(back_populates='tariff')

class Location(Base):
    __tablename__ = 'locations'
    id: Mapped[int] = mapped_column(primary_key=True)
    display_name: Mapped[str] = mapped_column(String(50))
    country_code: Mapped[str] = mapped_column(String(2))

    nodes: Mapped[list['Node']] = relationship(back_populates='location')

class Category(Base):
    __tablename__ = 'categories'
    id: Mapped[int] = mapped_column(primary_key=True)
    display_name: Mapped[str] = mapped_column(String(50))
    cpu_desc: Mapped[str] = mapped_column(String(100))

    nodes: Mapped[list['Node']] = relationship(back_populates='category')
    tariffs: Mapped[list['Tariff']] = relationship(back_populates='category')
