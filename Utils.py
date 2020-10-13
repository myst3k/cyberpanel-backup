import random
import string
from MySQLdb import connect


class Utils:

    @staticmethod
    def generate_repo_password() -> str:
        password_length = 24
        letters_and_digits = string.ascii_letters + string.digits
        result_str = ''.join((random.choice(letters_and_digits) for _ in range(password_length)))
        return result_str

    @staticmethod
    def get_websites_list():
        website_list = []  # [website_id, website_name, database_name]
        db = connect(db="cyberpanel", read_default_file="~/.my.cnf")
        cursor = db.cursor()
        cursor.execute("SELECT id, domain from websiteFunctions_websites")
        websites = cursor.fetchall()
        cursor.close()
        for website in websites:
            website_id = website[0]
            website_name = website[1]
            cursor = db.cursor()
            query = """SELECT dbName from databases_databases WHERE website_id='%s' LIMIT 1""" % website_id
            cursor.execute(query)
            db_name = cursor.fetchone()
            if db_name:
                website_list.append((website_id, website_name, str(db_name[0])))
            else:
                website_list.append((website_id, website_name, None))
            cursor.close()
        return website_list
