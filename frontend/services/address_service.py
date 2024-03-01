from typing import List
from core.config import Config
from models.schema.address import Address
from utils.http_utils import HttpUtils

class AddressService:
    @staticmethod
    async def list() -> List[Address]:
        try:
            return await HttpUtils.get(Config.ADDRESS_SERVICE_LIST_ENDPOINT, response_model=list[Address])
        except Exception as e:
            raise e
