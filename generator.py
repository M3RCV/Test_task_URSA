import json
import os

from parser import parse_pandascore_match

def generate_html_for_day(day: str, matches: list) -> str:
    # Генерация HTML страниц по дням
    titles = {
        "yesterday": "Матчи за вчерашний день",
        "today": "Матчи за сегодняшний день",
        "tomorrow": "Матчи на завтрашний день"
    }
    descriptions = {
        "yesterday": "Результаты киберспортивных матчей за вчерашний день. CS2, Dota 2, LoL и другие дисциплины.",
        "today": "Актуальные киберспортивные матчи сегодня. Расписание, трансляции, результаты.",
        "tomorrow": "Предстоящие киберспортивные матчи завтра. Следите за анонсами и планируйте просмотр."
    }
    page_title = titles.get(day, "Киберспорт матчи")
    page_description = descriptions.get(day, "Киберспортивные события: матчи, турниры, результаты.")

    organization_schema = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": "ES Matches",
        "url": "https://yourdomain.com",
        "logo": "https://yourdomain.com/static/logo.png",
        "sameAs": [
            "https://t.me/yourchannel",
            "https://twitter.com/yourprofile"
        ]
    }

    def render_match_card(match):
        score_html = f'<div class="text-center text-3xl font-bold text-emerald-400">{match["score"]}</div>' if match.get("score") else ''
        return f"""
        <div class="match-card bg-zinc-900 border border-zinc-800 rounded-3xl p-6">
            <div class="flex justify-between items-start mb-6">
                <div>
                    <div class="text-xs text-zinc-400">{match["discipline"]}</div>
                    <div class="font-medium">{match["league"]}</div>
                </div>
                <div class="text-right text-sm text-zinc-400">{match["time"]}</div>
            </div>
            <div class="text-2xl font-semibold text-center my-6">
                {match["team1"]} <span class="text-emerald-400 mx-4">VS</span> {match["team2"]}
            </div>
            {score_html}
        </div>
        """

    matches_html = ''.join(render_match_card(m) for m in matches) if matches else '<p class="text-center text-2xl col-span-full">Матчей в этот день пока нет</p>'

    active_class = 'text-emerald-400 border-b-2 border-emerald-400'
    inactive_class = 'hover:text-emerald-400'

    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{page_description}">
    <meta name="keywords" content="киберспорт, cs2, dota2, lol, матчи, {day}">
    <meta name="robots" content="index, follow">
    <title>{page_title}</title>
    <script type="application/ld+json">
        {json.dumps(organization_schema, ensure_ascii=False, indent=2)}
    </script>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Space+Grotesk:wght@500;600&display=swap');
        body {{ font-family: 'Inter', sans-serif; }}
        .logo-font {{ font-family: 'Space Grotesk', sans-serif; }}
        .match-card {{ transition: all 0.3s ease; }}
        .match-card:hover {{ transform: translateY(-8px); }}
    </style>
</head>
<body class="bg-zinc-950 text-white">

<nav class="bg-black border-b border-zinc-800 sticky top-0 z-50">
    <div class="max-w-screen-2xl mx-auto px-6">
        <div class="h-16 flex items-center justify-between">
            <div class="flex items-center gap-3">
                <div class="w-9 h-9 bg-emerald-500 rounded-2xl flex items-center justify-center text-2xl">🎮</div>
                <div class="logo-font text-3xl tracking-tighter font-semibold">ES MATCHES</div>
            </div>
            <div class="flex gap-10 text-lg">
                <a href="/yesterday" class="{active_class if day == 'yesterday' else inactive_class}">Вчера</a>
                <a href="/today" class="{active_class if day == 'today' else inactive_class}">Сегодня</a>
                <a href="/tomorrow" class="{active_class if day == 'tomorrow' else inactive_class}">Завтра</a>
            </div>
            <div onclick="alert('Обновление данных...')" class="cursor-pointer bg-emerald-600 hover:bg-emerald-500 px-6 py-2 rounded-2xl text-sm font-medium">
                Обновить данные
            </div>
        </div>
    </div>
</nav>

<div class="max-w-screen-2xl mx-auto px-6 py-10">
    <h1 class="text-5xl font-semibold logo-font tracking-tighter">{page_title}</h1>
    <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4 gap-6 mt-10">
        {matches_html}
    </div>
</div>

</body>
</html>"""


def generate_all_pages(matches_data: dict, output_dir: str = "static") -> None:
    """
    Генерирует HTML-страницы для yesterday, today, tomorrow
    на основе данных matches_data (по играм) и сохраняет их в output_dir.

    matches_data: {
        "cs2": {"yesterday": [raw_match1, ...], "today": [...], "tomorrow": [...]},
        "dota2": {"yesterday": [...], "today": [...], "tomorrow": [...]},
        ...
    }
    """
    os.makedirs(output_dir, exist_ok=True)

    combined = {"yesterday": [], "today": [], "tomorrow": []}
    for game_data in matches_data.values():
        for day in combined.keys():
            raw_matches = game_data.get(day, [])
            # Преобразуем сырые матчи в формат для карточек
            parsed = [parse_pandascore_match(m) for m in raw_matches]
            combined[day].extend(parsed)

    # Генерируем и сохраняем страницы
    for day in combined.keys():
        html = generate_html_for_day(day, combined[day])
        file_path = os.path.join(output_dir, f"{day}.html")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"✅ Сохранена страница {file_path}")