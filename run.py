from dotenv import load_dotenv
load_dotenv()

from app import application
import os

if __name__ == "__main__":
    application.run(host=os.getenv("HOST"), port=os.getenv("PORT"))
