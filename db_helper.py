from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)
    nickname = Column(String)

    def __repr__(self):
        return f"<User(name='{self.name}', fullname='{self.fullname}', nickname='{self.nickname}')>"
    # 假设我们还有一个 Address 模型，用于演示关系


class Address(Base):
    __tablename__ = 'addresses'
    id = Column(Integer, primary_key=True)
    email_address = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="addresses")

    def __repr__(self):
        return f"<Address(email_address='{self.email_address}')>"

    # 在 User 模型中添加对 Address 的反向引用


User.addresses = relationship("Address", order_by=Address.id, back_populates="user")
# 创建数据库引擎
engine = create_engine('db.sqlite3', echo=True)

# 创建所有表
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()
