# run these tests with:
#
#    python -m unittest test_user_model.py

import os
from unittest import TestCase
from sqlalchemy import exc
from models import db, connect_db, User, UserRecipe, Board, Recipe

# create database in venv:
#
#   createdb capstone_one-test
#
# Do this step first before running tests!

os.environ['DATABASE_URL'] = 'postgresql:///capstone_one-test'

from app import app

db.create_all()


class UserModelTestCase(TestCase):
    """Test User Model"""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        user1 = User.register('test1', 'password', 'test1@testing.com', "Test", "User")
        user1.id = 131313
        user2 = User.register('test2', 'password', 'test2@testing.com', "Brock", "Lewis")
        user2.id = 131315

        db.session.commit()

        testboard = Board(name="tester", user_id=131313)
        testboard.id = 999999
        db.session.add(testboard)
        db.session.commit()

        user1 = User.query.get(131313)
        user2 = User.query.get(131315)
        testboard = Board.query.get(999999)

        self.user1 = user1
        self.user2 = user2
        self.testboard = testboard

        self.client = app.test_client()
    
    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD",
            first_name="Hello",
            last_name="World"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no boards & no created recipes
        self.assertEqual(len(u.boards), 0)
        self.assertEqual(len(u.created_recipes), 0)
    
    def test_valid_register(self):
        user_test = User.register('testing', 'password', 'testing@testing.com', "Test_FirstName", "Test_LastName")
        user_test.id = 121212
        db.session.commit()

        user_test = User.query.get(121212)
        self.assertEqual(user_test.username, 'testing')
        self.assertEqual(user_test.email, 'testing@testing.com')
        self.assertEqual(user_test.first_name, "Test_FirstName")
        self.assertEqual(user_test.last_name, "Test_LastName")
        self.assertNotEqual(user_test.password, 'password')
        # With Bcrypt, strings should start with $2b$
        self.assertTrue(user_test.password.startswith("$2b$"))
    
    def test_invalid_username_register(self):
        invalid_user = User.register(None, 'password', 'test5@email.com', "Bad", "Test")
        invalid_user.id = 444444

        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()
    
    def test_invalid_email_register(self):
        invalid_user = User.register('hello', 'password', None, "BAD", "TEST")
        invalid_user.id = 555555
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()
    
    def test_valid_authentication(self):
        user = User.authenticate(self.user1.username, 'password')
        self.assertIsNotNone(user)
        self.assertEqual(user.id, self.user1.id)
    
    def test_invalid_username(self):
        self.assertFalse(User.authenticate("notavaliduser", "password"))
    
    def test_invalid_password(self):
        self.assertFalse(User.authenticate(self.user1.username, 'wrongpassword'))

# Test board model for user2
    def test_board_model(self):
        """Does basic model work?"""

        b = Board(
            name="pasta",
            user_id=131315,
        )

        db.session.add(b)
        db.session.commit()

        # User should have no boards & no created recipes
        self.assertEqual(len(b.recipe_ids), 0)
        self.assertEqual(len(self.user2.boards), 1)

# Test recipe model for testboard
    def test_recipe_model(self):
        '''Does basic model work?'''

        r = Recipe(
            board_id=999999,
            id=99999999
        )

        db.session.add(r)
        db.session.commit()

        self.assertEqual(len(self.testboard.recipe_ids), 1)

# Test user recipe model for user2
    def test_user_recipe_model(self):
        '''Does basic model work'''

        ur = UserRecipe(
            title="Milkshake",
            user_id=131315,
            ingredient_1="2 Cups Ice Cream",
            ingredient_2="1 Cup Milk",
            instructions="Blend together and enjoy!"
        )

        db.session.add(ur)
        db.session.commit()


        self.assertEqual(len(self.user2.created_recipes), 1)