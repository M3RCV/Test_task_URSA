from typing import Dict, Any


def get_team_name(opponent_data):
    # Обрабокта имени команды
    if not opponent_data:
        return "TBD"
    if isinstance(opponent_data, dict):
        # Вариант 1: есть вложенный объект opponent
        if "opponent" in opponent_data and opponent_data["opponent"]:
            return opponent_data["opponent"].get("name", "TBD")
        # Вариант 2: название прямо в текущем объекте
        if "name" in opponent_data:
            return opponent_data["name"]
    return "TBD"


def parse_pandascore_match(match: Dict[str, Any]) -> Dict[str, Any]:
    # Парсит данный в удобный для фронта формат
    videogame = match.get("videogame", {}) or {}
    discipline = videogame.get("name", "Unknown")

    # Команды
    opponents = match.get("opponents", [])
    if not opponents:
        team1 = "TBD"
        team2 = "TBD"
    else:
        team1 = get_team_name(opponents[0]) if len(opponents) > 0 else "TBD"
        team2 = get_team_name(opponents[1]) if len(opponents) > 1 else "TBD"

    # Время
    begin_at = match.get("begin_at", "")
    time_str = begin_at[11:16] if begin_at and "T" in begin_at else "00:00"

    # Статус и счёт
    status = match.get("status", "upcoming")
    score = None
    if status == "finished":
        results = match.get("results", []) or []
        score1 = results[0].get("score", 0) if len(results) > 0 else 0
        score2 = results[1].get("score", 0) if len(results) > 1 else 0
        score = f"{score1} : {score2}"

    # Лига
    serie = match.get("serie", {}) or {}
    league = match.get("league", {}) or {}
    league_name = serie.get("full_name") or league.get("name") or "Unknown League"

    return {
        "id": match.get("id"),
        "discipline": discipline,
        "league": league_name,
        "team1": team1,
        "team2": team2,
        "time": time_str,
        "status": status,
        "score": score,
        "begin_at": begin_at,
        "viewers": "—",
    }