import contextlib
from typing import ContextManager

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
# 创建数据库引擎
engine = create_engine('sqlite:///db.sqlite3', echo=False)
Session = sessionmaker(bind=engine)


@contextlib.contextmanager
def db_session(auto_commit_exit=True) -> ContextManager[Session]:
    """使用上下文管理资源关闭"""
    session = Session()
    try:
        yield session
        # 退出时，是否自动提交
        if auto_commit_exit:
            session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
