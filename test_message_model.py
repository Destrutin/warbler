"""Message model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

class MessageModelTestCase(TestCase):
    """Test message model"""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        user = User.signup('TestUser', 'testemail@gmail.com', 'password', None)
        userid = 1
        user.id = userid

        db.session.commit()

        user = User.query.get(userid)

        self.user = user
        self.userid = userid

        self.client = app.test_client()

    def tearDown(self):
        """Clear data after test"""

        db.session.rollback()
        db.drop_all()

    def test_message_model(self):
        message = Message(text='Test message', user_id=self.userid)

        db.session.add(message)
        db.session.commit()

        self.asserEqual(message.text, 'Test message')
        self.assrtEqual(message.user_id, self.userid)

    def test_repr_method(self):
        db.session.add(self.user)
        db.session.commit()
        message = Message(text='Test message', user_id=self.userid)

        db.session.add(message)
        db.session.commit()
        self.assertEqual(repr(message), f'<Message #{message.id}: {message.text}, {message.timestamp}>')

    def test_get_message(self):
        message = Message.create(self.userid, 'Test message')
        db.session.commit()
        gotten_message = Message.query.get(message.id)

        self.assertEqual(gotten_message, message)

    def test_invalid_message(self):
        gotten_message = Message.query.get(99999999)

        self.assertIsNone(gotten_message)

    def test_create_message(self):
        message = Message.create(self.userid, 'Test message')
        db.session.commit()

        self.assertIsInstance(message, Message)
        self.assertEqual(message.text, 'Test message')
        self.assertEqual(message.user_id, self.userid)

    def test_empty_message(self):
        message = Message.create(self.userid, '')
        db.session.rollback()

        self.assertIsNone(message)

    def test_invalid_user(self):
        message = Message.create(999999999, 'Test message')
        db.session.rollback()

        self.assertIsNone(message)

    def test_delete_message(self):
        message = Message.create(self.userid, 'Test message')
        db.session.commit()
        Message.delete(message.id, self.userid)
        db.session.commit()

        deleted_message = Message.query.get(message.id)
        self.assertIsNone(deleted_message)

    def test_delete_message_wrong_user(self):
        message = Message.create(self.userid, 'Test message')
        db.session.commit()
        Message.delete(message.id, 99999)
        db.session.rollback()