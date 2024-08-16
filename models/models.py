from datetime import datetime

from common.db_helper import db_session
from common.db_helper import Base, engine
from contextlib import contextmanager

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship


class Project(Base):
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_name = Column(String)
    project_id = Column(String)
    project_description = Column(String)
    project_type = Column(Integer)
    worker_dir = Column(Integer)
    create_time = Column(DateTime, default=datetime.utcnow())

    def __repr__(self):
        return f"<Project(name='{self.project_name}', project_type='{self.project_type}')>"
    # 假设我们还有一个 Address 模型，用于演示关系


#
# class Address(Base):
#     __tablename__ = 'addresses'
#     id = Column(Integer, primary_key=True)
#     email_address = Column(String, nullable=False)
#     user_id = Column(Integer, ForeignKey('users.id'))
#     user = relationship("User", back_populates="addresses")
#
#     def __repr__(self):
#         return f"<Address(email_address='{self.email_address}')>"
#
#
# # 在 User 模型中添加对 Address 的反向引用
# User.addresses = relationship("Address", order_by=Address.id, back_populates="user")
# 创建所有表
Base.metadata.create_all(engine)
