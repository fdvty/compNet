from app import app, db
from app.models import User, Unit, Role, Permission, Record, Evaluation

@app.shell_context_processor
def make_shell_context():
	return {'db': db, 'User': User, 'Unit':Unit, 'Role':Role, 'Permission':Permission, 'Record':Record, 'Evaluation':Evaluation}
