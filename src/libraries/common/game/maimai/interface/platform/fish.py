from ..interface import Interface


class DivingFishInterface(Interface):

    def __init__(self, id: str, platform_id: str):
        super().__init__(id, platform_id)
