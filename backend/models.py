from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.String(36), primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))

    def to_dict(self):
        """
        Helper method to convert task to a dictionary
        """
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description
        }
