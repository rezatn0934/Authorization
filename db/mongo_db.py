import motor.motor_asyncio

MONGO_URI = "mongodb://localhost:27017"
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
database = client["library"]


def get_db():

    """
    The get_db function opens a new database connection if there is none yet for the
    current application context.


    :return: The database
    :doc-author: Trelent
    """
    db = database
    return db
