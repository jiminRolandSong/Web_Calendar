from datetime import datetime
from datetime import date
from flask import request, abort
from flask import Flask
from flask import jsonify
from flask_restful import Resource, Api, reqparse, inputs
from flask_restful import Resource, Api, marshal_with, fields
import sys
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
api = Api(app)
db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///events.db'


class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    event = db.Column(db.String(80), nullable=False)
    date = db.Column(db.Date, nullable=False)


db.create_all()



class EventByID(Resource):

    def get(self, event_id):
        event = Event.query.filter(Event.id == event_id).first()
        if event is None:
            abort(404, "The event doesn't exist!")
        else:
            return jsonify({"id": event.id, "event": event.event, "date": str(event.date)})

    def delete(self, event_id):
        event = Event.query.filter(Event.id == event_id).first()
        if event is None:
            abort(404, "The event doesn't exist!")
        else:
            Event.query.filter(Event.id == event_id).delete()
            db.session.commit()
            message = {
                "message": "The event has been deleted!"
            }
            return jsonify(message)


api.add_resource(EventByID, '/event/<int:event_id>')

parser = reqparse.RequestParser()
parser.add_argument(
    'date',
    type=inputs.date,
    help="The event date with the correct format is required! The correct format is YYYY-MM-DD!",
    required=True
)
parser.add_argument(
    'event',
    type=str,
    help="The event name is required!",
    required=True
)


class Calendar(Resource):
    def post(self):
        args = parser.parse_args()
        message = {
            'message': 'The event has been added!',
            'event': args['event'],
            'date': str(args['date'].date())
        }
        event = Event(event=args['event'], date=args['date'].date())
        db.session.add(event)
        db.session.commit()
        return jsonify(message)

    def get(self):
        start = request.args.get('start_time')
        end = request.args.get('end_time')
        events = Event.query.all()
        if start and end:
            events = Event.query.filter(Event.date.between(start,end)).all()
        event_list = []
        for event in events:
            event_list.append({"id": event.id, "event": event.event, "date": str(event.date)})
        return jsonify(event_list)


api.add_resource(Calendar, '/event')


class Today(Resource):
    def get(self):
        events = Event.query.filter(Event.date == date.today()).all()
        event_list = []
        for event in events:
            event_list.append({"id": event.id, "event": event.event, "date": str(event.date)})
        return jsonify(event_list)


api.add_resource(Today, '/event/today')

# do not change the way you run the program
if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run()
