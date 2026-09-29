"""Idempotently add realistic local-development complaint data.

Run from backend: ``python -m scripts.seed`` after ``alembic upgrade head``.
"""

import asyncio

from app.database import close_connections, create_session_factory
from app.providers.triage.rules import RuleBasedTriage
from app.repositories.complaints import ComplaintRepository
from app.schemas import ComplaintCreate
from app.services.complaints import ComplaintService
from app.services.triage import TriageService

SEED_COMPLAINTS: tuple[tuple[str, str], ...] = (
    ("Burst water pipe is flooding homes near the market.", "Street 12, Gulberg"),
    ("Water supply has been unavailable since yesterday morning.", "Block C, Model Town"),
    ("Sewer overflow is entering the lane after heavy rain.", "Canal View Road"),
    ("Exposed electricity wire is sparking beside the school gate.", "Johar Town Phase 2"),
    ("Transformer has failed and our block has no electricity.", "Iqbal Town Block H"),
    ("Loose wire is hanging dangerously above the footpath.", "Main Boulevard, DHA"),
    ("Garbage has not been collected for five days.", "Township Sector B"),
    ("Waste containers are overflowing and smell badly.", "Anarkali Bazaar"),
    ("Dead animal remains have not been removed from the road.", "Samanabad Main Road"),
    ("Large pothole is damaging vehicles near the bus stop.", "Ferozepur Road"),
    ("Road surface has collapsed after the recent rain.", "Wapda Town Gate 1"),
    ("Footpath is broken and unsafe for wheelchair users.", "Mall Road"),
    ("Streetlight outside our house has been off for a week.", "Garden Town Street 4"),
    ("Three lamps near the park are not working at night.", "Askari Park"),
    ("Light pole is leaning dangerously toward the road.", "Shadman Colony"),
    ("Request a pedestrian crossing near the clinic.", "Kareem Block"),
    ("Drain cover is missing and children could fall in.", "Sabzazar Block N"),
    ("Water meter chamber is leaking continuously.", "Valencia Town"),
    ("Open manhole is causing danger for motorcycles.", "Kot Lakhpat Road"),
    ("Sewage smell is unbearable around the community center.", "Mustafa Town"),
    ("Garbage dump is attracting stray dogs near homes.", "Ravi Road"),
    ("Broken road divider has sharp metal exposed.", "Ring Road Service Lane"),
    ("Potholes make the school route dangerous for children.", "Faisal Town"),
    ("Traffic signal pole has fallen after strong winds.", "Liberty Roundabout"),
    ("Streetlight flickers repeatedly and may cause a shock.", "Bahria Orchard"),
    ("No water pressure on upper floors every evening.", "Muslim Town"),
    ("Drain is blocked and rainwater is collecting outside shops.", "Hall Road"),
    ("Trash bin needs replacement because its lid is broken.", "Pak Arab Housing"),
    ("Minor crack has appeared in the neighborhood footpath.", "Walled City Lane 8"),
    ("Please add a bench at the public park entrance.", "Race Course Park"),
    ("Street road has loose gravel after repair work.", "Allama Iqbal Town"),
    ("Water tanker is leaking while filling the public tank.", "Babu Sabu Interchange"),
)


async def seed() -> None:
    created = 0
    async with create_session_factory()() as session:
        repository = ComplaintRepository(session)
        service = ComplaintService(repository, TriageService(RuleBasedTriage()))
        for text, location in SEED_COMPLAINTS:
            if not await repository.exists_with_text_and_location(text, location):
                await service.create(ComplaintCreate(text=text, location=location))
                created += 1
    print(f"Seed complete: created {created}; total fixtures {len(SEED_COMPLAINTS)}.")
    await close_connections()


if __name__ == "__main__":
    asyncio.run(seed())
