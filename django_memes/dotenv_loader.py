import os
import dotenv


def load_dotenv():
    dotenv.load_dotenv(os.path.join(
        os.path.dirname(os.path.dirname(__file__)), '.env'))
