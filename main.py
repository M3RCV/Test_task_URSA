from fastapi import FastAPI
from fastapi.responses import FileResponse, RedirectResponse
from fetcher import get_all_matches_for_three_days
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import asyncio
from generator import generate_all_pages
app = FastAPI()



scheduler = AsyncIOScheduler()

async def scheduled_update():
    print("🕛 Обновление данных по расписанию...")
    try:
        data = await get_all_matches_for_three_days()
        generate_all_pages(data)
        print("✅ Данные успешно обновлены.")
    except Exception as e:
        print(f"❌ Ошибка при обновлении данных: {e}")

@app.on_event("startup")
async def startup_event():
    # Первоначальное получение данных
    data = await get_all_matches_for_three_days()
    generate_all_pages(data)

    # Настройка задачи на полночь
    scheduler.add_job(
        scheduled_update,
        trigger=CronTrigger(hour=0, minute=0),
        id="update_matches",
        replace_existing=True
    )
    scheduler.start()

@app.get("/")
async def root():
    return RedirectResponse(url="/today")

@app.get("/yesterday")
async def yesterday():
    return FileResponse("static/yesterday.html")

@app.get("/today")
async def today():
    return FileResponse("static/today.html")

@app.get("/tomorrow")
async def tomorrow():
    return FileResponse("static/tomorrow.html")

@app.on_event("shutdown")
async def shutdown_event():
    if scheduler.running:
        scheduler.shutdown()
