import math
import aiohttp
from io import BytesIO
from typing import Optional, Tuple, Union, overload

from PIL import Image, ImageDraw
from src.libraries.assets.get import assets, AssetType
from .image import DrawText
from .basic import *
from config import (
    MEIRYO_FONT,
    SIYUAN_FONT,
    TORUS_BOLD_FONT,
)
from .player import Player, SongData


class Draw:

    def __init__(self, image: Image.Image = None) -> None:
        self._im = image
        dr = ImageDraw.Draw(self._im)
        self._mr = DrawText(dr, MEIRYO_FONT)
        self._sy = DrawText(dr, SIYUAN_FONT)
        self._tb = DrawText(dr, TORUS_BOLD_FONT)

        self.basic = Image.open(
            assets.get(AssetType.IMAGES, "b50_score_basic")
        ).convert("RGBA")

        self.advanced = Image.open(
            assets.get(AssetType.IMAGES, "b50_score_advanced")
        ).convert("RGBA")
        self.expert = Image.open(
            assets.get(AssetType.IMAGES, "b50_score_expert")
        ).convert("RGBA")
        self.master = Image.open(
            assets.get(AssetType.IMAGES, "b50_score_master")
        ).convert("RGBA")
        self.remaster = Image.open(
            assets.get(AssetType.IMAGES, "b50_score_remaster")
        ).convert("RGBA")
        self.title_bg = (
            Image.open(assets.get(AssetType.IMAGES, "title2"))
            .convert("RGBA")
            .resize((600, 120))
        )
        self.design_bg = (
            Image.open(assets.get(AssetType.IMAGES, "design"))
            .convert("RGBA")
            .resize((1320, 120))
        )

        self._diff = [
            self.basic,
            self.advanced,
            self.expert,
            self.master,
            self.remaster,
        ]

    async def whiledraw(
        self,
        data: SongData,
        best: bool,
    ) -> None:

        # y为第一排纵向坐标，dy为各排间距
        dy = 170
        y = 430 if best else 1700

        TEXT_COLOR = [
            (255, 255, 255, 255),
            (255, 255, 255, 255),
            (255, 255, 255, 255),
            (255, 255, 255, 255),
            (138, 0, 226, 255),
        ]
        x = 70
        for num, info in enumerate(data):
            if num % 5 == 0:
                x = 70
                y += dy if num != 0 else 0
            else:
                x += 416

            cover = (
                Image.open(await assets.get_async(AssetType.COVER, info.song_id))
                .resize((135, 135))
                .convert("RGBA")
            )
            version = (
                Image.open(
                    await assets.get_async(AssetType.IMAGES, f"{info.type.upper()}.png")
                )
                .resize((55, 19))
                .convert("RGBA")
            )

            if info.rating_icon.islower():
                rate = (
                    Image.open(
                        await assets.get_async(
                            AssetType.IMAGES,
                            f"UI_TTR_Rank_{score_Rank_l[info.rating_icon]}.png",
                        )
                    )
                    .resize((95, 44))
                    .convert("RGBA")
                )
            else:
                rate = (
                    Image.open(
                        await assets.get_async(
                            AssetType.IMAGES,
                            f"UI_TTR_Rank_{score_Rank_l[info.rating_icon]}.png",
                        )
                    )
                    .resize((95, 44))
                    .convert("RGBA")
                )

            self._im.alpha_composite(self._diff[info.level_index], (x, y))
            self._im.alpha_composite(cover, (x + 5, y + 5))
            self._im.alpha_composite(version, (x + 80, y + 141))
            self._im.alpha_composite(rate, (x + 150, y + 98))
            if info.fc:
                fc = (
                    Image.open(
                        await assets.get_async(
                            AssetType.IMAGES, f"UI_MSS_MBase_Icon_{fcl[info.fc]}.png"
                        )
                    )
                    .resize((45, 45))
                    .convert("RGBA")
                )

                self._im.alpha_composite(fc, (x + 246, y + 99))
            if info.fs:
                fs = (
                    Image.open(
                        await assets.get_async(
                            AssetType.IMAGES, f"UI_MSS_MBase_Icon_{fsl[info.fs]}.png"
                        )
                    )
                    .resize((45, 45))
                    .convert("RGBA")
                )

                self._im.alpha_composite(fs, (x + 291, y + 99))

            # dxscore = info.dx_score
            dxnum = 0
            if info.total_dxscore != 0:
                dxnum = dxScore(info.dx_score / info.total_dxscore * 100)
            if dxnum:
                self._im.alpha_composite(
                    Image.open(
                        await assets.get_async(
                            AssetType.IMAGES,
                            f"UI_GAM_Gauge_DXScoreIcon_0{dxnum}.png",
                        )
                    ).convert("RGBA"),
                    (x + 335, y + 102),
                )

            self._tb.draw(
                x + 40,
                y + 148,
                20,
                info.song_id,
                TEXT_COLOR[info.level_index],
                anchor="mm",
            )
            title = info.title
            if coloumWidth(title) > 18:
                title = changeColumnWidth(title, 17) + "..."
            self._sy.draw(
                x + 155, y + 20, 20, title, TEXT_COLOR[info.level_index], anchor="lm"
            )
            self._tb.draw(
                x + 155,
                y + 50,
                32,
                f"{info.achievements:.4f}%",
                TEXT_COLOR[info.level_index],
                anchor="lm",
            )
            self._tb.draw(
                x + 338,
                y + 82,
                20,
                f"{info.dx_score}/{info.total_dxscore}",
                TEXT_COLOR[info.level_index],
                anchor="mm",
            )
            self._tb.draw(
                x + 155,
                y + 82,
                22,
                f"{info.ds} -> {info.rating}",
                TEXT_COLOR[info.level_index],
                anchor="lm",
            )


class DrawBest(Draw):

    def __init__(self, UserInfo: Player) -> None:
        super().__init__(
            Image.open(assets.get(AssetType.IMAGES, "b50_bg.png")).convert("RGBA")
        )
        self.userName = UserInfo.nickname
        self.plate = UserInfo.name_plate
        self.course_rank = UserInfo.course_rank
        self.Rating = UserInfo.rating
        self.sdBest = UserInfo.song_data_b35
        self.dxBest = UserInfo.song_data_b15
        self.avatar_id = UserInfo.avatar_id
        self.avatar_url = UserInfo.avatar_url

    def _findRaPic(self) -> str:
        if self.Rating < 1000:
            num = "01"
        elif self.Rating < 2000:
            num = "02"
        elif self.Rating < 4000:
            num = "03"
        elif self.Rating < 7000:
            num = "04"
        elif self.Rating < 10000:
            num = "05"
        elif self.Rating < 12000:
            num = "06"
        elif self.Rating < 13000:
            num = "07"
        elif self.Rating < 14000:
            num = "08"
        elif self.Rating < 14500:
            num = "09"
        elif self.Rating < 15000:
            num = "10"
        else:
            num = "11"
        return f"UI_CMN_DXRating_{num}.png"

    async def draw(self) -> Image.Image:
        logo = (
            Image.open(assets.get(AssetType.IMAGES, "logo.png"))
            .resize((378, 228))
            .convert("RGBA")
        )
        dx_rating = (
            Image.open(assets.get(AssetType.IMAGES, self._findRaPic()))
            .resize((300, 59))
            .convert("RGBA")
        )
        Name = Image.open(await assets.get_async(AssetType.IMAGES, "Name.png")).convert(
            "RGBA"
        )
        MatchLevel = (
            Image.open(await assets.get_async(AssetType.COURSE_RANK, self.course_rank))
            .resize((134, 55))
            .convert("RGBA")
        )
        ClassLevel = (
            Image.open(await assets.get_async(AssetType.IMAGES, "UI_FBR_Class_00.png"))
            .resize((144, 87))
            .convert("RGBA")
        )
        rating = (
            Image.open(
                await assets.get_async(AssetType.IMAGES, "UI_CMN_Shougou_Rainbow.png")
            )
            .resize((454, 50))
            .convert("RGBA")
        )

        self._im.alpha_composite(logo, (5, 130))
        if self.plate:

            plate = (
                Image.open(await assets.get_async(AssetType.PLATE, self.plate))
                .resize((1420, 230))
                .convert("RGBA")
            )

        else:
            plate = (
                Image.open(
                    await assets.get_async(AssetType.IMAGES, "UI_Plate_300501.png")
                )
                .resize((1420, 230))
                .convert("RGBA")
            )

        self._im.alpha_composite(plate, (390, 100))

        # 头像
        if self.avatar_id:

            icon = (
                Image.open(await assets.get_async(AssetType.AVATAR, self.avatar_id))
                .resize((214, 214))
                .convert("RGBA")
            )
        elif self.avatar_url:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(self.avatar_url) as resp:
                        icon = (
                            Image.open(BytesIO(await resp.read()))
                            .resize((214, 214))
                            .convert("RGBA")
                        )
            except:
                icon = (
                    Image.open(await assets.get_async(AssetType.AVATAR, 1))
                    .resize((214, 214))
                    .convert("RGBA")
                )
        else:  # 默认头像
            icon = (
                Image.open(await assets.get_async(AssetType.AVATAR, 1))
                .resize((214, 214))
                .convert("RGBA")
            )

        self._im.alpha_composite(icon, (398, 108))
        self._im.alpha_composite(dx_rating, (620, 122))
        Rating = f"{self.Rating:05d}"
        for n, i in enumerate(Rating):
            self._im.alpha_composite(
                Image.open(
                    await assets.get_async(AssetType.IMAGES, f"UI_NUM_Drating_{i}.png")
                )
                .resize((28, 34))
                .convert("RGBA"),
                (760 + 23 * n, 137),
            )

        self._im.alpha_composite(Name, (620, 200))
        self._im.alpha_composite(MatchLevel, (935, 205))
        self._im.alpha_composite(ClassLevel, (926, 105))
        self._im.alpha_composite(rating, (620, 275))

        self._sy.draw(635, 235, 40, self.userName, (0, 0, 0, 255), "lm")
        sdrating, dxrating = sum([_.rating for _ in self.sdBest]), sum(
            [_.rating for _ in self.dxBest]
        )
        self._tb.draw(
            847,
            295,
            28,
            f"B35: {sdrating} + B15: {dxrating} = {self.Rating}",
            (0, 0, 0, 255),
            "mm",
            3,
            (255, 255, 255, 255),
        )
        self._mr.draw(
            900,
            2465,
            35,
            f"Designed by Yuri-YuzuChaN & BlueDeer233 | Generated by Maimai Channel BOT",
            (0, 50, 100, 255),
            "mm",
            3,
            (255, 255, 255, 255),
        )

        await self.whiledraw(self.sdBest, True)
        await self.whiledraw(self.dxBest, False)

        return self._im.resize((1760, 2000))


def dxScore(dx: int) -> int:
    """
    返回值为 `Tuple`： `(星星种类，数量)`
    """
    if dx <= 85:
        result = 0
    elif dx <= 90:
        result = 1
    elif dx <= 93:
        result = 2
    elif dx <= 95:
        result = 3
    elif dx <= 97:
        result = 4
    else:
        result = 5
    return result


def getCharWidth(o) -> int:
    widths = [
        (126, 1),
        (159, 0),
        (687, 1),
        (710, 0),
        (711, 1),
        (727, 0),
        (733, 1),
        (879, 0),
        (1154, 1),
        (1161, 0),
        (4347, 1),
        (4447, 2),
        (7467, 1),
        (7521, 0),
        (8369, 1),
        (8426, 0),
        (9000, 1),
        (9002, 2),
        (11021, 1),
        (12350, 2),
        (12351, 1),
        (12438, 2),
        (12442, 0),
        (19893, 2),
        (19967, 1),
        (55203, 2),
        (63743, 1),
        (64106, 2),
        (65039, 1),
        (65059, 0),
        (65131, 2),
        (65279, 1),
        (65376, 2),
        (65500, 1),
        (65510, 2),
        (120831, 1),
        (262141, 2),
        (1114109, 1),
    ]
    if o == 0xE or o == 0xF:
        return 0
    for num, wid in widths:
        if o <= num:
            return wid
    return 1


def coloumWidth(s: str) -> int:
    res = 0
    for ch in s:
        res += getCharWidth(ord(ch))
    return res


def changeColumnWidth(s: str, len: int) -> str:
    res = 0
    sList = []
    for ch in s:
        res += getCharWidth(ord(ch))
        if res <= len:
            sList.append(ch)
    return "".join(sList)


@overload
def computeRa(ds: float, achievement: float) -> int:
    """
    - `ds`: 定数
    - `achievement`: 成绩
    """


@overload
def computeRa(ds: float, achievement: float, *, onlyrate: bool = False) -> str:
    """
    - `ds`: 定数
    - `achievement`: 成绩
    - `onlyrate`: 返回评价
    """


@overload
def computeRa(
    ds: float, achievement: float, *, israte: bool = False
) -> Tuple[int, str]:
    """
    - `ds`: 定数
    - `achievement`: 成绩
    - `israte`: 返回元组 (底分, 评价)
    """


def computeRa(
    ds: float, achievement: float, *, onlyrate: bool = False, israte: bool = False
) -> Union[int, Tuple[int, str]]:
    if achievement < 50:
        baseRa = 7.0
        rate = "D"
    elif achievement < 60:
        baseRa = 8.0
        rate = "C"
    elif achievement < 70:
        baseRa = 9.6
        rate = "B"
    elif achievement < 75:
        baseRa = 11.2
        rate = "BB"
    elif achievement < 80:
        baseRa = 12.0
        rate = "BBB"
    elif achievement < 90:
        baseRa = 13.6
        rate = "A"
    elif achievement < 94:
        baseRa = 15.2
        rate = "AA"
    elif achievement < 97:
        baseRa = 16.8
        rate = "AAA"
    elif achievement < 98:
        baseRa = 20.0
        rate = "S"
    elif achievement < 99:
        baseRa = 20.3
        rate = "Sp"
    elif achievement < 99.5:
        baseRa = 20.8
        rate = "SS"
    elif achievement < 100:
        baseRa = 21.1
        rate = "SSp"
    elif achievement < 100.5:
        baseRa = 21.6
        rate = "SSS"
    else:
        baseRa = 22.4
        rate = "SSSp"

    if israte:
        data = (math.floor(ds * (min(100.5, achievement) / 100) * baseRa), rate)
    elif onlyrate:
        data = rate
    else:
        data = math.floor(ds * (min(100.5, achievement) / 100) * baseRa)

    return data
