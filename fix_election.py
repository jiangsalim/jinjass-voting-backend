from app import app, db
from models import Election, SystemSettings

with app.app_context():
    election = Election.query.first()
    if election:
        election.status = 'active'
        print(f"Election '{election.title}' set to active")
    
    settings = SystemSettings.query.first()
    if settings and election:
        settings.current_election_id = election.id
        settings.voting_open = True
        print("Voting is now OPEN")
    
    db.session.commit()
    print("Done!")