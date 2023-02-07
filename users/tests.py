from django.contrib.auth import get_user
from users.models import CustomUser
from django.test import TestCase
from django.urls import reverse


class RegistrationTestCase(TestCase):
    def test_user_account_is_created(self):
        self.client.post(
            reverse("users:register"),
            data={
                "username":"abdulboqiy",
                "first_name":"Abdulboqiy",
                "last_name":"Anvarjonov",
                "email":"abdulboq1y@mail.ru",
                "password":"prestige",
            }
        )

        user = CustomUser.objects.get(username="abdulboqiy")

        self.assertEqual(user.first_name,"Abdulboqiy")
        self.assertEqual(user.last_name,"Anvarjonov")
        self.assertEqual(user.email,"abdulboq1y@mail.ru")
        self.assertNotEqual(user.password,"prestige")
        self.assertTrue(user.check_password("prestige"))


    def test_required_fields(self):
        response = self.client.post(
            reverse("users:register"),
            data = {
                "first_name":"Abdulboqiy",
                "email":"abdulboq1y@mail.ru"
            }
        )

        user_count = CustomUser.objects.count()

        self.assertEqual(user_count, 0)
        self.assertFormError(response, "form", "username", "This field is required.")
        self.assertFormError(response, "form", "password", "This field is required.")

    def test_invalid_email(self):
        response = self.client.post(
            reverse("users:register"),
            data={
                "username": "abdulboqiy",
                "first_name": "Abdulboqiy",
                "last_name": "Anvarjonov",
                "email": "invalid-email",
                "password": "prestige",
            }
        )

        user_count = CustomUser.objects.count()

        self.assertEqual(user_count, 0)
        self.assertFormError(response, "form", "email", "Enter a valid email address.")


    def test_unique_username(self):
        user = CustomUser.objects.create(username="abdulboqiy", first_name="Abdulboqiy")
        user.set_password("prestige")
        user.save()

        response = self.client.post(
            reverse("users:register"),
            data={
                "username": "abdulboqiy",
                "first_name": "Abdulboqiy",
                "last_name": "Anvarjonov",
                "email": "abdulboq1y@mail.ru",
                "password": "prestige",
            }
        )

        user_count = CustomUser.objects.count()
        self.assertEqual(user_count, 1)

        self.assertFormError(response, "form", "username", "A user with that username already exists.")


class LoginTestCase(TestCase):
    def setUp(self):
        self.db_user = CustomUser.objects.create(username="abdulboqiy", first_name="Abdulboqiy")
        self.db_user.set_password("prestige")
        self.db_user.save()

    def test_successful_login(self):
        self.client.post(
            reverse("users:login"),
            data={
                "username":"abdulboqiy",
                "password":"prestige"
        }
        )

        user = get_user(self.client)
        self.assertTrue(user.is_authenticated)

    def test_wrong_credentials(self):
        self.client.post(
            reverse("users:login"),
            data={
                "username": "wrong-username",
                "password": "prestige"
            }
        )

        user = get_user(self.client)
        self.assertFalse(user.is_authenticated)

        self.client.post(
            reverse("users:login"),
            data={
                "username": "abdulboqiy",
                "password": "wrong-password"
            }
        )

        user = get_user(self.client)
        self.assertFalse(user.is_authenticated)

    def test_logout(self):
        self.client.login(username="abdulboqiy", password = "prestige")
        self.client.get(reverse("users:logout"))

        user = get_user(self.client)
        self.assertFalse(user.is_authenticated)

class ProfileTestCase(TestCase):
    def test_login_required(self):
        response = self.client.get(reverse("users:profile"))

        self.assertEqual(response.url, reverse("users:login") + "?next=/users/profile/")

    def test_profile_details(self):
        user = CustomUser.objects.create(
            username="abdulboqiy", first_name="Abdulboqiy",
            last_name="Anvarjonov", email = "abdulboq1y@mail.ru"
        )
        user.set_password("prestige")
        user.save()

        self.client.login(username="abdulboqiy", password="prestige")

        response = self.client.get(reverse("users:profile"))

        self.assertContains(response, user.username)
        self.assertContains(response, user.first_name)
        self.assertContains(response, user.last_name)
        self.assertContains(response, user.email)

    def test_update_profile(self):
        user = CustomUser.objects.create(
            username="abdulboqiy", first_name="Abdulboqiy",
            last_name="Anvarjonov", email = "abdulboq1y@mail.ru"
        )
        user.set_password("prestige")
        user.save()
        self.client.login(username="abdulboqiy", password="prestige")

        response = self.client.post(
            reverse("users:profile-edit"),
            data={"username":"abdulboqiy", "first_name":"Abdulboqiy",
            "last_name":"asqarov", "email": "abdulboqiy@mail.ru"}
        )
        user.refresh_from_db()

        self.assertEqual(user.last_name, "asqarov")
        self.assertEqual(user.email, "abdulboqiy@mail.ru")
        self.assertEqual(response.url, reverse("users:profile"))


