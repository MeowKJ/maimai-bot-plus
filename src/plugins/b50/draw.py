import random

from PIL import Image, ImageDraw, ImageFont
from src.libraries.assets import assets, AssetType
from src.libraries.common.images.alpha import (
    adjust_image_alpha,
    add_rounded_corners_to_image,
    deepen_image_color,
)
from src.libraries.common.images.text import (
    draw_centered_text,
    draw_centered_truncated_text,
    draw_truncated_text,
)

from src.libraries.common.images.components.user_info import draw_user_info

from src.libraries.common.game.maimai import SongRateType
from .image import DrawText
from .basic import *
from config import FontPaths, VERSION, DEFAULT_AVATAR_URL
from .player import B50Player, SongDifficulty


class Draw:

    def __init__(self, image: Image.Image = None) -> None:
        self._im = image
        dr = ImageDraw.Draw(self._im)
        self._mr = DrawText(dr, FontPaths.MEIRYO)
        self._sy = DrawText(dr, FontPaths.SIYUAN)
        self._tb = DrawText(dr, FontPaths.TORUS_BOLD)

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

        alpha = 0.6

        for i in range(5):
            img = deepen_image_color(self._diff[i], 1.5)
            self._diff[i] = adjust_image_alpha(img, alpha)

    async def whiledraw(
        self,
        data: List[SongDifficulty],
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

            cover_path = await assets.get_async(AssetType.COVER, info.id)
            if not cover_path:
                cover_path = await assets.get_async(AssetType.COVER, 0)
            cover = Image.open(cover_path).resize((135, 135)).convert("RGBA")
            version = (
                Image.open(
                    await assets.get_async(
                        AssetType.IMAGES, f"{info.song_type.value}.png"
                    )
                )
                .resize((55, 19))
                .convert("RGBA")
            )

            # rate sss和sss+的使用prism样式
            if info.user_score.rate:
                if (
                    info.user_score.rate == SongRateType.SSS
                    or info.user_score.rate == SongRateType.SSS_PLUS
                ):
                    rate = (
                        Image.open(
                            await assets.get_async(
                                AssetType.PRISM, f"{info.user_score.rate.value}.png"
                            )
                        )
                        .resize((95, 44))
                        .convert("RGBA")
                    )

                    rate = deepen_image_color(rate, 2)

                else:
                    rate = (
                        Image.open(
                            await assets.get_async(
                                AssetType.IMAGES,
                                f"UI_TTR_Rank_{score_Rank_l[info.user_score.rate.value]}.png",
                            )
                        )
                        .resize((110, 44))
                        .convert("RGBA")
                    )
            self._im.alpha_composite(self._diff[info.level_index], (x, y))
            self._im.alpha_composite(cover, (x + 5, y + 5))
            self._im.alpha_composite(version, (x + 80, y + 141))
            self._im.alpha_composite(rate, (x + 150, y + 98))
            if info.user_score.fc.value:
                fc = (
                    Image.open(
                        await assets.get_async(
                            AssetType.IMAGES,
                            f"UI_MSS_MBase_Icon_{fcl[info.user_score.fc.value]}.png",
                        )
                    )
                    .resize((45, 45))
                    .convert("RGBA")
                )

                self._im.alpha_composite(fc, (x + 246, y + 99))
            if info.user_score.fs.value:
                fs = (
                    Image.open(
                        await assets.get_async(
                            AssetType.IMAGES,
                            f"UI_MSS_MBase_Icon_{fsl[info.user_score.fs.value]}.png",
                        )
                    )
                    .resize((45, 45))
                    .convert("RGBA")
                )

                self._im.alpha_composite(fs, (x + 291, y + 99))

            dxnum = info.get_dx_score_num()

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
                info.id,
                TEXT_COLOR[info.level_index],
                anchor="mm",
            )
            title = info.title
            if coloumWidth(title) > 19:
                title = changeColumnWidth(title, 18) + "..."
            self._sy.draw(
                x + 155, y + 20, 20, title, TEXT_COLOR[info.level_index], anchor="lm"
            )
            self._tb.draw(
                x + 155,
                y + 50,
                32,
                f"{info.user_score.achievements:.4f}%",
                TEXT_COLOR[info.level_index],
                anchor="lm",
            )

            dxsocre_text = (
                f"{info.user_score.dx_score}/{info.dx_rating_max}"
                if info.user_score.dx_score
                else str(info.dx_rating_max)
            )
            self._tb.draw(
                x + 338,
                y + 82,
                20,
                dxsocre_text,
                TEXT_COLOR[info.level_index],
                anchor="mm",
            )
            self._tb.draw(
                x + 155,
                y + 82,
                22,
                f"{info.level} -> {info.user_score.rating}",
                TEXT_COLOR[info.level_index],
                anchor="lm",
            )


class DrawBest(Draw):

    def __init__(self, b50player: B50Player) -> None:

        background_image = random.choices(
            ["b50_bg1-min.png", "b50_bg2-min.png", "b50_bg3-min.png"],
            weights=[80, 10, 10],
            k=1,
        )[0]

        super().__init__(
            Image.open(assets.get(AssetType.PRISM, background_image)).convert("RGBA")
        )
        self.b50player = b50player

    async def draw(self) -> Image.Image:

        # 绘制用户信息板子
        default_plate_list = [
            await assets.get_async(AssetType.PRISM, f"p{i}-min.png")
            for i in range(1, 4)
        ]

        default_avatar_list = [
            await assets.get_async(AssetType.PRISM, f"logo{i}.png") for i in range(1, 6)
        ]

        sdrating, dxrating = sum(
            [_.user_score.rating for _ in self.b50player.song_data_b35]
        ), sum([_.user_score.rating for _ in self.b50player.song_data_b15])

        user_info_image = await draw_user_info(
            self.b50player.user_info,
            f"B35: {sdrating} + B15: {dxrating} = {self.b50player.user_info.rating}",
            random.choice(default_plate_list),
            random.choice(default_avatar_list),
        )

        self._im.alpha_composite(user_info_image, (500, 100))
        # 绘制徽章
        if self.b50player.favorite_id == 0:
            self.b50player.favorite_id = random.randint(1, 17)

        logo = (
            Image.open(
                assets.get(AssetType.ONGEKI, f"ongeki{self.b50player.favorite_id}.png")
            )
            .resize((int(220 * 1.2), int(290 * 1.2)))
            .convert("RGBA")
        )
        self._im.alpha_composite(logo, (130, 25))

        # 绘制底部信息
        footer_text_1 = f"Generated by Maimai Channel BOT [{VERSION}]"
        footer_text_2 = f"Designed by Komo | Maimai的频道 | 频道号: 82f4ywfvrm"
        self._mr.draw(
            490,
            2465,
            35,
            footer_text_2,
            (0, 50, 100, 255),
            "mm",
            3,
            (255, 255, 255, 255),
            font=ImageFont.truetype(FontPaths.ZHIZI, 35),
        )

        self._mr.draw(
            1750,
            2465,
            35,
            footer_text_1,
            (0, 50, 100, 255),
            "mm",
            3,
            (255, 255, 255, 255),
            font=ImageFont.truetype(FontPaths.ZHIZI, 35),
        )

        await self.whiledraw(self.b50player.song_data_b35, True)
        await self.whiledraw(self.b50player.song_data_b15, False)

        self._im = add_rounded_corners_to_image(self._im, 35)
        return self._im


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
