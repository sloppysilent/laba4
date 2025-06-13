import os
import unittest
from flask import Flask
from io import StringIO
from unittest.mock import patch
from laba3 import app, ANSWERS_FILE


class SurveyAppTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

        if os.path.exists(ANSWERS_FILE):
            os.remove(ANSWERS_FILE)

    def tearDown(self):
        if os.path.exists(ANSWERS_FILE):
            os.remove(ANSWERS_FILE)

    def test_survey_page_get(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('<form', response.data.decode('utf-8'))

    def test_survey_submission_post(self):
        test_data = {
            'name': 'Тестовый Пользователь',
            'age': '25',
            'email': 'test@example.com',
            'feedback': 'Отличный опрос!',
            'rating': '5'
        }

        response = self.client.post('/', data=test_data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Спасибо за участие в опросе!', response.data.decode('utf-8'))

        self.assertTrue(os.path.exists(ANSWERS_FILE))
        with open(ANSWERS_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
            for key, value in test_data.items():
                self.assertIn(value, content)

    def test_survey_submission_missing_fields(self):
        test_data = {'name': 'Тестовый Пользователь'}

        response = self.client.post('/', data=test_data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Спасибо за участие в опросе!', response.data.decode('utf-8'))

    def test_thank_you_page(self):
        response = self.client.get('/thank-you')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Спасибо за участие в опросе!', response.data.decode('utf-8'))

    def test_file_writing(self):
        test_data = {
            'name': 'Иван Иванов',
            'age': '30',
            'email': 'ivan@example.com',
            'feedback': 'Хорошо, но можно лучше',
            'rating': '4'
        }

        self.client.post('/', data=test_data)

        with open(ANSWERS_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn(f"Имя: {test_data['name']}", content)
            self.assertIn(f"Возраст: {test_data['age']}", content)
            self.assertIn(f"Email: {test_data['email']}", content)
            self.assertIn(f"Отзыв: {test_data['feedback']}", content)
            self.assertIn(f"Оценка: {test_data['rating']}", content)
            self.assertIn("=" * 30, content)

    def test_multiple_submissions(self):
        test_data1 = {
            'name': 'Пользователь 1',
            'age': '20',
            'email': 'user1@example.com',
            'feedback': 'Первый отзыв',
            'rating': '3'
        }

        test_data2 = {
            'name': 'Пользователь 2',
            'age': '40',
            'email': 'user2@example.com',
            'feedback': 'Второй отзыв',
            'rating': '5'
        }

        self.client.post('/', data=test_data1)
        self.client.post('/', data=test_data2)

        with open(ANSWERS_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn(test_data1['name'], content)
            self.assertIn(test_data2['name'], content)
            self.assertEqual(content.count("=" * 30), 2)


if __name__ == '__main__':
    unittest.main()