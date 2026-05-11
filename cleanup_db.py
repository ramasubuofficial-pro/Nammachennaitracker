from sqlmodel import Session, select
from backend.database import engine
from backend.models import Party, Event

def cleanup_duplicates():
    with Session(engine) as session:
        # Get all parties
        parties = session.exec(select(Party)).all()
        seen = set()
        to_delete = []
        
        for p in parties:
            if p.name in seen or p.name in ['VCK', 'TVK', 'தவெக', 'விசிக']:
                to_delete.append(p)
            else:
                seen.add(p.name)
        
        for p in to_delete:
            session.delete(p)
        
        session.commit()
        print(f"Deleted {len(to_delete)} duplicate parties.")

if __name__ == "__main__":
    cleanup_duplicates()
