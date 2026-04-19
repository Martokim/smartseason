from django.core.management.base import BaseCommand
from django.utils import timezone
from users.models import User
from fields.models import Field, FieldUpdate
from datetime import date, timedelta


class Command(BaseCommand):
    help = 'Seed the database with demo users and fields'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding data...')

        # Clean slate — remove existing non-superuser demo data
        User.objects.filter(username__in=['agent_john', 'agent_sara']).delete()
        Field.objects.all().delete()

        # ── Create demo agents ────────────────────────────────────────────
        john = User.objects.create_user(
            username='agent_john',
            password='agent123',
            first_name='John',
            last_name='Kamau',
            role='AGENT'
        )
        sara = User.objects.create_user(
            username='agent_sara',
            password='agent123',
            first_name='Sara',
            last_name='Wanjiku',
            role='AGENT'
        )

        # ── Create fields ─────────────────────────────────────────────────
        f1 = Field.objects.create(
            name='North Block',
            crop_type='Maize',
            planting_date=date.today() - timedelta(days=45),
            stage='GROWING',
            assigned_agent=john
        )
        f2 = Field.objects.create(
            name='South Plot',
            crop_type='Wheat',
            planting_date=date.today() - timedelta(days=90),
            stage='READY',
            assigned_agent=john
        )
        f3 = Field.objects.create(
            name='East Ridge',
            crop_type='Sorghum',
            planting_date=date.today() - timedelta(days=120),
            stage='HARVESTED',
            assigned_agent=sara
        )
        f4 = Field.objects.create(
            name='West Paddock',
            crop_type='Beans',
            planting_date=date.today() - timedelta(days=10),
            stage='PLANTED',
            assigned_agent=sara
        )

        # ── Create some updates ───────────────────────────────────────────
        FieldUpdate.objects.create(
            field=f1, agent=john, stage='GROWING',
            notes='Good germination, soil moisture adequate.'
        )
        FieldUpdate.objects.create(
            field=f2, agent=john, stage='READY',
            notes='Crop is ready for harvest. Awaiting equipment.'
        )
        FieldUpdate.objects.create(
            field=f3, agent=sara, stage='HARVESTED',
            notes='Harvest complete. Yield was above average.'
        )
        FieldUpdate.objects.create(
            field=f4, agent=sara, stage='PLANTED',
            notes='Seeds planted. Expecting germination in 7 days.'
        )

        self.stdout.write(self.style.SUCCESS(
            '\nDemo data created successfully.'
            '\n\nDemo credentials:'
            '\n  Admin  → username: Marto      password: (your superuser password)'
            '\n  Agent  → username: agent_john  password: agent123'
            '\n  Agent  → username: agent_sara  password: agent123'
        ))
