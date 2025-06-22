import sys
import asyncio
from forecast import run_forecast
from wetterstation import run_station_update

async def main():
    if len(sys.argv) < 2:
        print("Bitte gib an: 'historisch' oder 'aktuell'")
        return

    case = sys.argv[1].lower()

    if case not in ("historisch", "aktuell"):
        print(" Ungültiger Parameter. Verwende nur 'historisch' oder 'aktuell'")
        return

    print(" Wetterstationen werden aktualisiert...")
    run_station_update()

    print(f" Starte Forecast: {case}")
    run_forecast(case)

if __name__ == "__main__":
    asyncio.run(main())
