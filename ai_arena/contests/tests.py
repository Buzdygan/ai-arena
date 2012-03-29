from django.test import TestCase
from django.test.client import Client


class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

class WebPageTest(TestCase):

    fixtures = ['basic_fixture.json']

    def test_main(self):
        """
            Tests displaying of a main page.
        """

        client = Client()
        response = client.get('/')
        self.assertContains(response, 'Home', status_code=200)

    def test_login(self):
        """
            Tests logging into the page.
        """

        client = Client()
        client.login(username='test_user', password='test')
        response = client.get('/')
        self.assertContains(response, 'Logged as <a href="/profile/">test_user</a>.', status_code=200)

    def test_register(self):
        """
            Tests registering.
        """

        response = self.client.post('/accounts/register/', {'username': 'fred', 'password1': 'secret', 'password2': 'secret'}, follow=True)
        self.assertContains(response, 'My profile', status_code=200)
        self.assertRedirects(response, '/profile/')

    def test_launch_match(self):
        """
            Tests displaying of Launch Match page.
        """

        client = Client()
        response = client.get('/launch_match/')
        self.assertContains(response, 'Game field', status_code=200)

    def test_match_results_list(self):
        """
            Tests displaying of Match Results List page.
        """

        client = Client()
        response = client.get('/results/match_results_list/')
        self.assertContains(response, 'Match Results', status_code=200)

    def test_game_list(self):
        """
            Tests displaying of Game List page.
        """

        client = Client()
        response = client.get('/game_list/')
        self.assertContains(response, 'test_game', status_code=200)

    def test_new_game(self):
        """
            Tests displaying of Create New Game page.
        """

        client = Client()
        response = client.get('/new_game/')
        # should redirect to login page
        self.assertRedirects(response, '/accounts/login/?next=/new_game/')
        client.login(username='test_user', password='test')
        response = client.get('/new_game/', follow=True)
        self.assertContains(response, 'Game name', status_code=200)

    def test_send_bot(self):
        """
            Tests displaying of Send Bot page.
        """

        client = Client()
        response = client.get('/send_bot/')
        # should redirect to login page
        self.assertRedirects(response, '/accounts/login/?next=/send_bot/')
        client.login(username='test_user', password='test')
        response = client.get('/send_bot/', follow=True)
        self.assertContains(response, 'Bot name', status_code=200)
