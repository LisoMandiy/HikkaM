# meta developer: @CristalixCEO
# meta pic: https://avatars.githubusercontent.com/u/128410002
# meta banner: https://chojuu.vercel.app/api/banner?img=https://avatars.githubusercontent.com/u/128410002&title=Aeza&description=Aeza%20hosting%20manager%20for%20Hikka%20Userbot

from .. import loader, utils
import aiohttp
from enum import Enum

class Error(Enum):
    unauthorized = "\u274c Неавторизован. Проверь API токен."
    not_found = "\u26a0\ufe0f Сервер не найден."
    unknown = "\u2753 Неизвестная ошибка."
    no_key = "\u26a0\ufe0f Не указан API ключ. Используй <code>.config AezaControl</code> чтобы задать его."

class AezaModule(loader.Module):
    """Управление серверами Aeza через API"""
    strings = {"name": "AezaControl"}

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "api_key",
                None,
                lambda: "API ключ Aeza. Получить можно в панели https://my.aeza.net/profile/api",
                validator=loader.validators.Hidden()
            )
        )

    async def client_ready(self, client, db):
        self.client = client

    async def aeza(self, message):
        await utils.answer(message, (
            "\u2699\ufe0f <b>Aeza Control</b>\n"
            "<code>.aeza list</code> - список серверов\n"
            "<code>.aeza start ID</code> - запустить сервер\n"
            "<code>.aeza stop ID</code> - остановить сервер\n"
            "<code>.aeza reboot ID</code> - перезапуск сервера"
        ))

    async def aeza_list(self, message):
        token = self.config.get("api_key")
        if not token:
            return await utils.answer(message, Error.no_key.value)

        async with aiohttp.ClientSession() as session:
            async with session.get("https://my.aeza.net/api/vm", headers={"X-API-Key": token}) as resp:
                if resp.status == 401:
                    return await utils.answer(message, Error.unauthorized.value)
                data = await resp.json()
                if not data.get("items"):
                    return await utils.answer(message, "\u274c Нет доступных серверов.")
                
                out = "\ud83c\udf10 <b>Список серверов:</b>\n"
                for vm in data["items"]:
                    out += (f"\u2022 <b>{vm['name']}</b> — {vm['main_ip']}, "
                            f"ID: <code>{vm['id']}</code>, "
                            f"Статус: <code>{vm['status']}</code>\n")
                await utils.answer(message, out)

    async def aeza_start(self, message):
        await self._action(message, "start")

    async def aeza_stop(self, message):
        await self._action(message, "stop")

    async def aeza_reboot(self, message):
        await self._action(message, "reboot")

    async def _action(self, message, action):
        args = utils.get_args_raw(message)
        if not args:
            return await utils.answer(message, f"\u26a0\ufe0f Укажи ID сервера для {action}.")

        token = self.config.get("api_key")
        if not token:
            return await utils.answer(message, Error.no_key.value)

        async with aiohttp.ClientSession() as session:
            url = f"https://my.aeza.net/api/vm/{args}/{action}"
            async with session.post(url, headers={"X-API-Key": token}) as resp:
                if resp.status == 401:
                    return await utils.answer(message, Error.unauthorized.value)
                elif resp.status == 404:
                    return await utils.answer(message, Error.not_found.value)
                elif resp.status not in [200, 202]:
                    return await utils.answer(message, Error.unknown.value)
                return await utils.answer(message, f"\u2705 Успешно: <code>{action}</code> для сервера {args}")
