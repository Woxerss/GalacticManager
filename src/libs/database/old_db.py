from datetime import datetime
import time
import pymysql
import logging
import os.path
import sys
import re

from tabnanny import check
from time import timezone
from typing import List

logger = logging.getLogger(__name__)

# Connecting sql query for creating a new database and
# connecting path to the directory with the config file
if __name__ == '__main__':
    from libs.database.old_create_db_sql import create_status_table
    from libs.database.old_create_db_sql import create_users_table
    from libs.database.old_create_db_sql import insert_status
    sys.path.append('D:/!GitClones/DiscordBot/src/')
else:
    from .old_create_db_sql import create_status_table
    from .old_create_db_sql import create_users_table
    from .old_create_db_sql import insert_status
    sys.path.append(os.getcwdb()) 
    
from config import Config

# Singleton
class Database:
    __instance = None
    __connection = None
    __statusList = []

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(Database, cls).__new__(cls)
            cls.__connection = cls.create_connection()
            tableList = cls.execute_query(''' SHOW TABLES; ''')
            if (len(tableList) == 0):
                print('There are no tables, create new')
                logger.warning('MYSQL Create new tables')
                cls.execute_query(create_status_table)
                cls.execute_query(create_users_table)
                cls.execute_query(insert_status)
            tempStatusList = cls.execute_query(''' SELECT Name FROM status ''')
            for status in tempStatusList:
                 cls.__statusList.append(status[0])
            print('New Database Object created!')
            return cls.__instance

    # Connecting database
    @classmethod
    def create_connection(cls):
        connection = None
        try:
            connection = pymysql.connect(host=Config.get('mysql', 'host'), user=Config.get('mysql', 'user'), passwd=Config.get('mysql', 'passwd'), db=Config.get('mysql', 'db'))
            logger.info('Connecting to SQLite DB')
        except pymysql.Error as err_string:
            logger.exception(f'The exception in create_connection occured, {err_string}')
        return connection

    # Execute SQL query
    @classmethod
    def execute_query(cls, query):
        cursor = cls.__connection.cursor()
        try:
            cursor.execute(query)
            cls.__connection.commit()
            return cursor.fetchall()
        except pymysql.Error as err_string:
            logger.exception(f'The exception in execute_query occured, {err_string}')
            return -1
    
    # Check user
    @classmethod
    def check_user(cls, userId: int):
        result = cls.execute_query(f'''SELECT CASE WHEN EXISTS(SELECT Name FROM users where DiscordID = {userId}) = 1 THEN 1 ELSE 0 END''')
        return 1 if (result[0][0] == 1) else 0

    # Add a new user
    @classmethod
    def add_user(cls, id: int, inviterId: int = None, inviteCode: str = None):
        ts = time.time()
        now = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        if (cls.execute_query(f''' INSERT INTO users (DiscordID, JoinedDatetime, InviterId, InviteCode) VALUES ({id}, '{now}', {inviterId}, '{inviteCode}') ''')):
            return 1
        return 0

    # Update registration date
    @classmethod
    def get_user(cls, id: int):
        result = cls.execute_query(f''' SELECT * FROM users WHERE DiscordID = {id} ''')
        return result

    # Set user registration status
    @classmethod
    def set_status(cls, id: int, status):
        if status in cls.__statusList:
            cls.execute_query(f''' UPDATE users SET status="{status}" WHERE DiscordID={id} ''')
            return 1
        else:
            logger.error(f'The error in set_status occured, Invalid status: {status}')
        return 0

    # Set user name
    @classmethod
    def set_name(cls, id, name):
        match = re.fullmatch(Config.get('db', 'name_pattern'), name)
        if (match):
            if cls.check_user(id): 
                cls.execute_query(f''' UPDATE users SET Name="{name}" WHERE DiscordID={id} ''')
                return 1
            else:
                logger.error(f'The error in set_name occured, No player with such ID: {id}')
        else:
            logger.error(f'The error in set_name occured, Invalid name: {name}')
        return 0
    
    # Set user nickname
    @classmethod
    def set_nickname(cls, id, nickname):
        match = re.fullmatch(Config.get('db', 'nickname_pattern'), nickname)
        if (match):
            if cls.check_user(id): 
                cls.execute_query(f''' UPDATE users SET Nickname="{nickname}" WHERE DiscordID={id} ''')
                return 1
            else:
                logger.error(f'The error in set_nickname occured, No player with such ID: {id}')
        else:
            logger.error(f'The error in set_nickname occured, Invalid nickname: {nickname}')
        return 0

    # Get not confirmed invited players
    @classmethod
    def get_invited(cls, id):
        return cls.execute_query(f''' SELECT DiscordID FROM users WHERE InviterId = {id} AND Confirmed = 0 ''')
    
    # Get all not confirmed invited players
    @classmethod
    def get_all_invited(cls):
        return cls.execute_query(f''' SELECT DiscordID FROM users WHERE Confirmed = 0 ''')

    # Get current user status
    @classmethod
    def get_status(cls, id):
        if cls.check_user(id): 
            return cls.execute_query(f'''  SELECT Name, Description FROM status WHERE EXISTS (SELECT Status FROM users WHERE status.Name = users.Status AND users.DiscordID = {id}) ''')
        else:
            logger.error(f'The error in set_nickname occured, No player with such ID: {id}')
        return None

    # Confirm player
    @classmethod
    def confirm(cls, confirmatorId: int , userId: int):
        if (cls.check_user(userId)):
            user = cls.get_user(userId)
            if not (user[0][8]):
                cls.execute_query(f''' UPDATE users SET Confirmed=1 WHERE DiscordID={userId} ''')
                cls.execute_query(f''' UPDATE users SET ConfirmatorID={confirmatorId} WHERE DiscordID={userId} ''')
                return 1
            else:
                return 0
        return 0

    # Set joined date
    @classmethod
    def set_joined_date(cls, id, date):
        if cls.check_user(id): 
            cls.execute_query(f''' UPDATE users SET JoinedDatetime="{date}" WHERE DiscordID={id} ''')
        else:
            logger.error(f'The error in set_joined_date occured, No player with such ID: {id}')
        return 0
    
    # Update registration date
    @classmethod
    def update_reg_date(cls, id):
        if cls.check_user(id): 
            ts = time.time()
            now = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
            cls.execute_query(f''' UPDATE users SET RegDatetime="{now}" WHERE DiscordID={id} ''')
            return 1
        else:
            logger.error(f'The error in update_reg_date occured, No player with such ID: {id}')
        return 0

db = Database()