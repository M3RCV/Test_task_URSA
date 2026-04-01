import aiohttp
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Any
from datetime import date, timedelta
from config import TOKEN, URL


@dataclass(frozen=True)
class PandaScoreConfig:
    # Конфигурация для подключения к PandaScore API
    token: str
    base_url: str = URL
    per_page: int = 50
    timeout: int = 15


class BaseMatchFetcher(ABC):
    # Асинхронный абстрактный базовый класс для получения матчей любой игры
    def __init__(self, config: PandaScoreConfig):
        self.config = config
        self._session: aiohttp.ClientSession | None = None

    async def __aenter__(self):
        # Создаёт сессию при входе в контекст
        self._session = aiohttp.ClientSession(
            headers={"accept": "application/json"}
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Закрывает сессию при выходе из контекста
        if self._session:
            await self._session.close()

    @abstractmethod
    def get_url(self) -> str:
        # Возвращает полный URL для конкретной игры
        ...

    def get_base_params(self, date: str) -> Dict[str, Any]:
        # Общие параметры для всех запросов
        return {
            "token": self.config.token,
            "filter[begin_at]": date,
            "per_page": self.config.per_page,
        }

    async def fetch(self, date: str) -> List[Dict[str, Any]]:
        #  Метод получения матчей за одну дату
        if not self._session:
            raise RuntimeError("Сессия не создана. Используйте async with или вызовите init_session()")

        url = self.get_url()
        params = self.get_base_params(date)

        try:
            async with self._session.get(
                    url,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=self.config.timeout)
            ) as response:
                response.raise_for_status()
                data: List[Dict] = await response.json()

                print(f"✅ {self.__class__.__name__} → {len(data)} матчей за {date}")
                return data

        except aiohttp.ClientError as e:
            print(f"❌ {self.__class__.__name__} | Ошибка API: {e}")
            raise


class CS2MatchFetcher(BaseMatchFetcher):
    # cs2
    def get_url(self) -> str:
        return f"{self.config.base_url}/csgo/matches"

    def get_base_params(self, date: str) -> Dict[str, Any]:
        params = super().get_base_params(date)
        params["filter[videogame_title]"] = "cs-2"
        return params


class Dota2MatchFetcher(BaseMatchFetcher):
    # dota2
    def get_url(self) -> str:
        return f"{self.config.base_url}/dota2/matches"


class LoLMatchFetcher(BaseMatchFetcher):
    # LoL
    def get_url(self) -> str:
        return f"{self.config.base_url}/lol/matches"


def create_match_fetcher(game_slug: str, token: str) -> BaseMatchFetcher:
    # Синхронная фабрика для получения нужного fetcher'а
    config = PandaScoreConfig(token=token)

    slug = game_slug.lower().replace(" ", "-")

    if slug in {"cs2", "cs-2"}:
        return CS2MatchFetcher(config)
    elif slug == "dota2":
        return Dota2MatchFetcher(config)
    elif slug in {"lol", "league-of-legends"}:
        return LoLMatchFetcher(config)
    else:
        raise ValueError(f"Неизвестная игра: {game_slug}. Поддерживаются: cs2, dota2, lol")


def get_three_days() -> Dict[str, str]:
    # Возвращает даты
    today = date.today()
    return {
        "yesterday": (today - timedelta(days=1)).isoformat(),
        "today": today.isoformat(),
        "tomorrow": (today + timedelta(days=1)).isoformat(),
    }


async def get_matches_for_three_days(game_slug: str, token: str) -> Dict[str, List[Dict[str, Any]]]:
    """
    Асинхронно получает матчи за вчера, сегодня и завтра для выбранной игры.
    Возвращает словарь: {'yesterday': [...], 'today': [...], 'tomorrow': [...]}
    """
    fetcher = create_match_fetcher(game_slug, token)
    dates = get_three_days()
    result = {}

    print(f"\n🔄 Загрузка матчей за 3 дня для {game_slug.upper()}...")

    async with fetcher:
        for day_name, date_str in dates.items():
            try:
                result[day_name] = await fetcher.fetch(date_str)
            except Exception as e:
                print(f"⚠️  Ошибка при получении {day_name} ({date_str}): {e}")
                result[day_name] = []

    return result


async def get_all_matches_for_three_days() -> Dict[str, Dict[str, List[Dict]]]:
    # Возвращает данные о матчах за 3 дня для всех игр
    games = ["cs2", "dota2", "lol"]
    token = TOKEN
    all_data = {}

    for game in games:
        all_data[game] = await get_matches_for_three_days(game, token)

    return all_data
