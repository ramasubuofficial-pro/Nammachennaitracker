from sqlmodel import Session, create_engine, select
from datetime import datetime, timedelta
from backend.models import Party, Event
from backend.database import engine

def seed_data():
    with Session(engine) as session:
        # Full Party List from PRD
        parties_data = [
            {"name": "DMK", "name_tamil": "திமுக", "color": "#ff0000", "official_url": "https://dmk.in"},
            {"name": "AIADMK", "name_tamil": "அதிமுக", "color": "#008000", "official_url": "https://aiadmk.org.in"},
            {"name": "BJP", "name_tamil": "பாஜக", "color": "#ff9933", "official_url": "https://www.bjp.org"},
            {"name": "Congress", "name_tamil": "காங்கிரஸ்", "color": "#0000ff", "official_url": "https://www.inc.in"},
            {"name": "TVK", "name_tamil": "தவெக", "color": "#ffd700", "official_url": "https://twitter.com/tvkvijayhq"},
            {"name": "NTK", "name_tamil": "நாதக", "color": "#ffa500", "official_url": "https://www.naamtamilar.org"},
            {"name": "MDMK", "name_tamil": "மதிமுக", "color": "#ff0000", "official_url": "https://mdmk.org.in"},
            {"name": "VCK", "name_tamil": "விசிக", "color": "#0000ff", "official_url": "https://vck.in"}
        ]
        
        for p_data in parties_data:
            existing = session.exec(select(Party).where(Party.name == p_data["name"])).first()
            if not existing:
                session.add(Party(**p_data))
        
        session.commit()
        
        session.commit()
        print("Parties seeded successfully!")
        print("Seed data created successfully!")

if __name__ == "__main__":
    from backend.database import create_db_and_tables
    create_db_and_tables()
    seed_data()
