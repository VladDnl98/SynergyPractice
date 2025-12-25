import os
from dotenv import load_dotenv

load_dotenv()

class OtherNormalUrls:
    BEZ_LI_URL = os.getenv("BEZ_LI_URL")
    BEZLIMIT_RU_URL = os.getenv("BEZ_LI_URL")
    BEZLIMIT_PRO_RU_URL = os.getenv("BEZLIMIT_PRO_RU_URL")
    RUS_IN_COM_URL = os.getenv("RUS_IN_COM_URL")
    BRITE_TELE_RU_URL = os.getenv("BRITE_TELE_RU_URL")
    TELECOM_ALFA_RU_URL = os.getenv("TELECOM_ALFA_RU_URL")
