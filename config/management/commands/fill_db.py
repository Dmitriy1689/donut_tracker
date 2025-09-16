import random

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
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

        with transaction.atomic():
            users_to_create = []
            for i in range(options['users']):
                user = User(
                    username=fake.user_name()[:30],
                    email=fake.email(),
                    first_name=fake.first_name(),
                    last_name=fake.last_name()
                )
                users_to_create.append(user)

            users = User.objects.bulk_create(users_to_create)
            self.stdout.write(f'Создано пользователей: {len(users)}')

            for user in users:
                user.set_password('verystrongpass999')
                user.save(update_fields=['password'])

            occasions = [
                'birthday', 'wedding', 'charity',
                'medicine', 'education', 'other'
            ]
            collects_to_create = []
            for user in users:
                for i in range(options['collects']):
                    collect = Collect(
                        author=user,
                        title=fake.sentence(nb_words=4)[:35],
                        description=fake.text(max_nb_chars=200),
                        occasion=random.choice(occasions),
                        target_amount=random.randint(1000, 10000),
                        end_datetime=fake.future_datetime(end_date='+30d'),
                        is_completed=False
                    )
                    collects_to_create.append(collect)

            collects = Collect.objects.bulk_create(collects_to_create)
            self.stdout.write(f'Создано сборов: {len(collects)}')

            payments_to_create = []
            for collect in collects:
                payments_count = random.randint(1, options['payments'])
                current_total = 0

                for i in range(payments_count):
                    donator = random.choice(users)
                    amount = random.randint(100, 1000)

                    if (
                        collect.target_amount is not None and
                        current_total + amount > collect.target_amount
                    ):
                        amount = collect.target_amount - current_total
                        payments_to_create.append(
                            Payment(
                                collect=collect,
                                donator=donator,
                                amount=amount,
                                hide_amount=random.choice([True, False])
                            )
                        )
                        break

                    payments_to_create.append(
                        Payment(
                            collect=collect,
                            donator=donator,
                            amount=amount,
                            hide_amount=random.choice([True, False])
                        )
                    )
                    current_total += amount

            payments = Payment.objects.bulk_create(payments_to_create)
            self.stdout.write(f'Создано платежей: {len(payments)}')

        self.stdout.write(
            self.style.SUCCESS('БД успешно заполнена тестовыми данными.')
        )
