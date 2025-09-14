import random

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from faker import Faker

from collects.models import Collect
from payments.models import Payment


User = get_user_model()
fake = Faker('ru_RU')


class Command(BaseCommand):
    help = 'Заполняет базу данных тестовыми данными.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=10,
            help='Количество пользователей для создания',
        )
        parser.add_argument(
            '--collects',
            type=int,
            default=5,
            help='Количество сборов на пользователя',
        )
        parser.add_argument(
            '--payments',
            type=int,
            default=20,
            help='Количество платежей на пользователя',
        )

    def handle(self, *args, **options):
        self.stdout.write('Создание тестовых данных')

        users = []
        for i in range(options['users']):
            user = User.objects.create_user(
                username=fake.user_name()[:30],
                email=fake.email(),
                password='verystrongpass999',
                first_name=fake.first_name(),
                last_name=fake.last_name()
            )
            users.append(user)
            self.stdout.write(f'Пользователь создан: {user.username}')

        occasions = [
            'birthday', 'wedding', 'charity', 'medicine', 'education', 'other'
        ]
        collects = []
        for user in users:
            for i in range(options['collects']):
                collect = Collect.objects.create(
                    author=user,
                    title=fake.sentence(nb_words=4)[:35],
                    description=fake.text(max_nb_chars=200),
                    occasion=random.choice(occasions),
                    target_amount=random.randint(1000, 10000),
                    current_amount=0,
                    donators_count=0,
                    end_datetime=fake.future_datetime(end_date='+30d'),
                    is_completed=False
                )
                collects.append(collect)
                self.stdout.write(f'Создан сбор: {collect.title}')

        for collect in collects:
            for i in range(options['payments']):
                donator = random.choice(users)
                amount = random.randint(100, 1000)
                Payment.objects.create(
                    collect=collect,
                    donator=donator,
                    amount=amount,
                    hide_amount=random.choice([True, False])
                )
                self.stdout.write(
                    (
                        f'Создан платеж: {amount} от {donator.username} '
                        f'в сбор {collect.title}'
                    )
                )
        self.stdout.write(
            self.style.SUCCESS('БД успешно заполнена тестовыми данными.')
        )
