"""User model tests."""

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


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        user1 = User.signup('TestUser1', 'testemail1@gmail.com', 'password', None)
        userid1 = 1
        user1.id = userid1

        user2 = User.signup('TestUser2', 'testemail2@gmail.com', 'password', None)
        userid2 = 2
        user2.id = userid2

        db.session.commit()

        user1 = User.query.get(userid1)
        user2 = User.query.get(userid2)

        self.user1 = user1
        self.userid1 = userid1
        self.user2 = user2
        self.userid2 = userid2

        self.client = app.test_client()

    def tearDown(self):
        """Clear data after test"""

        db.session.rollback()
        db.drop_all()

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    def test_repr_method(self):
        db.session.add(self.user1)
        db.session.commit()
        self.assertEqual(repr(self.user), '<User #1: TestUser1, testemail1@gmail.com>')

    # Follow Tests ---------------------------

    def test_is_following(self):
        self.user1.following.append(self.user2)
        db.session.add_all([self.user1, self.user2])
        db.session.commit()
        self.assertTrue(self.user1.is_following(self.user2))

    def test_is_not_following(self):
        db.session.add_all([self.user1, self.user2])
        db.session.commit()
        self.assertFalse(self.user1.is_following(self.user2))

    def test_is_followed_by(self):
        self.user2.following.append(self.user1)
        db.session.add_all([self.user1, self.user2])
        db.session.commit()
        self.assertTrue(self.user1.is_followed_by(self.user2))

    def test_is_not_followed_by(self):
        db.session.add_all([self.user1, self.user2])
        db.session.commit()
        self.assertFalse(self.user1.is_followed_by(self.user2))

    # Create Tests -----------------------------
        
    def test_creates(self):
        user = User.create(username='TestUser', email='testemail@gmail.com', password='password')
        db.session.commit()

        self.assertIsInstance(user, User)
        self.assertEqual(user.username, 'TestUser')
        self.assertEqual(user.email, 'testemail@gmail.com')

    def test_does_not_create(self):
        user = User.create(username='TestUser', email='testemail@gmail.com', password='password')
        db.session.add(user)
        db.session.commit()

        bad_user = User.create(username='TestUser', email='testemail@gmail.com', password='bad_password')
        db.session.rollback()

        self.assertIsNone(bad_user)

    # Authenticate Tests ---------------------------
        
    def test_authenticate(self):
        user = User.authenticate(self.user1.username, 'password')
        self.assertEqual(user, self.user1)

    def test_authenticate_invalid_username(self):
        user = User.authenticate('NoUser', 'password')
        self.assertFalse(user)

    def test_authenticate_invalid_password(self):
        user = User.authenticate(self.user1.username, 'wrong_password')
        self.assertFalse(user)