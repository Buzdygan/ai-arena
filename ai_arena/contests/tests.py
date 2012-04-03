from django.test import TestCase
from django.test.client import Client

from ai_arena.contests.models import *

#from StringIO import StringIO
#import Image



class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

class WebPageTest(TestCase):

    fixtures = ['test_fixture.json']

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

        self.client.login(username='test_user', password='test')
        response = self.client.get('/')
        self.assertContains(response, 'Logged as <a href="/profile/">test_user</a>.', status_code=200)

    def test_register(self):
        """
            Tests registering.
        """

        response = self.client.post('/accounts/register/', {'username': 'fred', 'password1': 'secret', 'password2': 'secret'}, follow=True)
        self.assertContains(response, 'My profile', status_code=200)
        self.assertRedirects(response, '/profile/')

    def test_show_profile(self):
        """
            Tests showing profile.
        """

        self.client.login(username='test_user', password='test')
        response = self.client.get('/profile/')
        self.assertContains(response, 'My profile', status_code=200)

    def test_show_profile_of_user(self):
        """
            Tests showing profile for specified user.
        """

        self.client.login(username='test_user', password='test')
        response = self.client.get('/profile/test_user/')
        self.assertContains(response, 'My profile', status_code=200)

    def test_show_contests_of_user(self):
        """
            Tests showing contests of specified user.
        """

        self.client.login(username='test_user', password='test')
        response = self.client.get('/profile/test_user/contests/')
        self.assertContains(response, 'Contests:', status_code=200)
        self.assertContains(response, 'test_contest', status_code=200)

#TODO zrobic bardziej konkretny test dla bazy zawierajacej newsy
    def test_show_news_of_user(self):
        """
            Tests showing news of specified user.
        """

        self.client.login(username='test_user', password='test')
        response = self.client.get('/profile/test_user/news/')
        self.assertContains(response, 'My profile', status_code=200)

    def test_edit_profile(self):
        """
            Tests profile edition.
        """

        self.client.login(username='test_user', password='test')

        response = self.client.get('/profile_edit/')
        self.assertContains(response, 'Photo:', status_code=200)

        photo_file = open('media/profiles/photos/default_avatar.jpg', "rb").read()
        """
        file = StringIO()
        image = Image.new("RGBA", size=(50,50), color=(256,0,0))
        image.save(file, 'png')
        file.name = 'test.png'
        file.seek(0)
        """

        post_data = {
            'city': 'Africa',
            'country': 'Poland',
            'interests': None,
            'about': None,
            'university': None,
            'photo': photo_file
        }
        response = self.client.post('/profile_edit/', post_data, follow=True)

        photo_file.close()

        print response.content
        print response.redirect_chain
        self.assertContains(response, 'Country:', status_code=200)
        self.assertContains(response, 'Africa', status_code=200)
        self.assertContains(response, 'News:', status_code=200)

    def test_create_game(self):
        """
            Tests creating new Game.
        """

        self.client.login(username='test_user', password='test')
        rules_file = open('../files/testing/kk/kk_desc.txt')
        judge_file = open('../files/testing/kk/kk_judge.cpp')

        post_data = {
            'game_name': 'new_game',
            'game_rules': rules_file,
            'game_judge': judge_file,
            'judge_language': 'CPP'
        }

        response = self.client.post('/new_game/', post_data, follow=True)

        rules_file.close()
        judge_file.close()

        self.assertContains(response, 'new_game', status_code=200)
        self.assertContains(response, 'gra w kolko i krzyzyk', status_code=200)
        self.assertContains(response, 'Delete this game', status_code=200)

    def test_game_list(self):
        """
            Tests displaying of Game List page.
        """

        client = Client()
        response = client.get('/game_list/')
        self.assertContains(response, 'test_game', status_code=200)

    def test_game_details(self):
        """
            Tests displaying of Game details page.
        """

        response = self.client.get('/game_details/13/')
        self.assertContains(response, 'test_game_kk', status_code=200)

    def test_game_source(self):
        """
            Tests displaying of Game source.
        """

        response = self.client.get('/game_details/13/source/')
        self.assertContains(response, '#include', status_code=200)

    def test_game_edit(self):
        """
            Tests displaying of Game edition page.
        """

        self.client.login(username='test_user', password='test')

        response = self.client.get('/game_details/14/edit/')
        self.assertContains(response, 'KOMUNIKACJA Z SEDZIA', status_code=200)

#TODO test_delete_game

    def test_add_comment(self):
        """
            Tests adding comments to Game.
        """

        self.client.login(username='test_user', password='test')

        response = self.client.post('/game_details/add_comment/13/', {'comment': 'test_comment'}, follow=True)

        self.assertContains(response, 'test_comment', status_code=200)
        self.assertContains(response, 'test_game_kk', status_code=200)
        self.assertContains(response, 'test_user', status_code=200)

    def test_delete_comment(self):
        """
            Tests deleting comments to Game.
        """

        self.client.login(username='test_user', password='test')

        response = self.client.post('/game_details/add_comment/13/', {'comment': 'test_comment'}, follow=True)
        response = self.client.post('/game_details/del_comment/13/1/', follow=True)

        self.assertNotContains(response, 'test_comment', status_code=200)

    def test_edit_comment(self):
        """
            Tests editing comments to Game.
        """

        self.client.login(username='test_user', password='test')

        response = self.client.post('/game_details/add_comment/13/', {'comment': 'test_comment'}, follow=True)
        response = self.client.post('/game_details/edit_comment/13/1/', {'comment': 'edited_test_comment'}, follow=True)

        self.assertContains(response, 'edited_test_comment', status_code=200)
        self.assertContains(response, 'test_game_kk', status_code=200)
        self.assertContains(response, 'test_user', status_code=200)

    def test_send_bot(self):
        """
            Tests sending bot.
        """

        self.client.login(username='test_user', password='test')

        bot_file = open('../files/testing/kk/kk_bot.cpp')

        post_data = {
            'game': '13',
            'bot_name': 'test_bot',
            'bot_source': bot_file,
            'bot_language': 'CPP'
        }

        response = self.client.post('/send_bot/', post_data, follow=True)

        bot_file.close()

        self.assertContains(response, 'this is index content block', status_code=200)

    def test_send_game_bot(self):
        """
            Tests sending bot for specified game.
        """

        self.client.login(username='test_user', password='test')

        bot_file = open('../files/testing/kk/kk_bot.cpp')

        post_data = {
            'bot_name': 'test_bot',
            'bot_source': bot_file,
            'bot_language': 'CPP'
        }

        response = self.client.post('/send_bot/13/', post_data, follow=True)

        bot_file.close()

        self.assertContains(response, 'this is index content block', status_code=200)

    def test_match_results_list(self):
        """
            Tests displaying of Match Results List page.
        """

        client = Client()
        response = client.get('/results/match_results_list/')
        self.assertContains(response, 'Match Results', status_code=200)
        self.assertContains(response, 'test_game_kk', status_code=200)

    def test_match_result(self):
        """
            Tests displaying of particular Match Result.
        """

        response = self.client.get('/results/show_match_result/50/')
        self.assertContains(response, 'Match log:', status_code=200)
        self.assertContains(response, 'dummy', status_code=200)
        self.assertContains(response, 'test_game_kk', status_code=200)

#TODO czy testowac odpalanie meczu?

    def test_launch_match(self):
        """
            Tests displaying of Launch Match page.
        """

        client = Client()
        response = client.get('/launch_match/')
        self.assertContains(response, 'Game field', status_code=200)

    def test_contests_list(self):
        """
            Tests displaying Contests List.
        """

        response = self.client.get('/contests/contests_list/')
        self.assertContains(response, 'Contest name', status_code=200)
        self.assertContains(response, 'test_contest', status_code=200)
        self.assertContains(response, 'test_game_kk', status_code=200)

    def test_show_contest(self):
        """
            Tests displaying Contests details.
        """

        response = self.client.get('/contests/show_contest/3/')
        self.assertContains(response, 'Owner', status_code=200)
        self.assertContains(response, 'test_contest', status_code=200)
        self.assertContains(response, 'test_bot_kk1', status_code=200)

    def test_add_contestant(self):
        """
            Tests displaying Add Contestant page.
        """

        response = self.client.get('/contests/add_contestant/3/')
        self.assertContains(response, 'Bot field', status_code=200)

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

    def test_send_bot_page(self):
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


class ModelsTest(TestCase):

    def test_game_path(self):
        """
            Tests path method of Game model.
        """

        b = Bot(name='bot')
        print b
