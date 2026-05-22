import os
import django

# Set up the Django environment settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

# Import the user model and kanban models
from django.contrib.auth import get_user_model
from kanban.models import Project, Board, Column, Card

User = get_user_model()

def seed():
    print("Starting database seeding...")
    
    # 1. Create Superuser (Admin) if it doesn't exist
    admin_email = 'admin@gmail.com'
    admin_username = 'admin'
    admin_password = 'admin'
    
    admin_user, created = User.objects.get_or_create(
        email=admin_email,
        defaults={'username': admin_username, 'is_superuser': True, 'is_staff': True}
    )
    if created:
        admin_user.set_password(admin_password)
        admin_user.save()
        print(f"Created superuser: {admin_email} / {admin_password}")
    else:
        print(f"Superuser already exists: {admin_email}")

    # 2. Create Regular User (Developer) if it doesn't exist
    dev_email = 'developer@gmail.com'
    dev_username = 'developer'
    dev_password = 'password'
    
    dev_user, created = User.objects.get_or_create(
        email=dev_email,
        defaults={'username': dev_username}
    )
    if created:
        dev_user.set_password(dev_password)
        dev_user.save()
        print(f"Created regular user: {dev_email} / {dev_password}")
    else:
        print(f"Regular user already exists: {dev_email}")

    # 3. Create a Project owned by the admin user
    project, created = Project.objects.get_or_create(
        name="Sprintr Development Project",
        defaults={
            'description': "This project tracks the software development cycle of the Sprintr Kanban Board API.",
            'owner': admin_user
        }
    )
    if created:
        print(f"Created project: {project.name}")
    else:
        print(f"Project already exists: {project.name}")

    # 4. Create a Board in the project
    board, created = Board.objects.get_or_create(
        name="Backend Kanban Board",
        project=project
    )
    if created:
        print(f"Created board: {board.name}")
    else:
        print(f"Board already exists: {board.name}")

    # 5. Create Columns for the board
    todo_col, created = Column.objects.get_or_create(
        title="To Do",
        board=board,
        defaults={'order': 0}
    )
    if created:
        print("Created Column: To Do")

    inprogress_col, created = Column.objects.get_or_create(
        title="In Progress",
        board=board,
        defaults={'order': 1}
    )
    if created:
        print("Created Column: In Progress")

    done_col, created = Column.objects.get_or_create(
        title="Done",
        board=board,
        defaults={'order': 2}
    )
    if created:
        print("Created Column: Done")

    # 6. Create Cards in columns
    # We clear existing cards if any, or only create if not seeded to prevent duplicates
    if Card.objects.filter(column__board=board).count() == 0:
        card1 = Card.objects.create(
            title="Design Database Models",
            description="Sketch the relational schema between Projects, Boards, Columns, and Cards.",
            order=0,
            column=done_col,
            assignee=admin_user
        )
        card2 = Card.objects.create(
            title="Run Database Migrations",
            description="Use Django manage.py commands to build initial tables in db.sqlite3.",
            order=1,
            column=done_col,
            assignee=admin_user
        )
        card3 = Card.objects.create(
            title="Build Nested Serializers",
            description="Implement serializers that nestedly display Columns and Cards under a Board.",
            order=0,
            column=inprogress_col,
            assignee=dev_user
        )
        card4 = Card.objects.create(
            title="Create Project Core Views",
            description="Write manual APIViews to handle creation and listing of top-level projects.",
            order=0,
            column=todo_col,
            assignee=dev_user
        )
        card5 = Card.objects.create(
            title="Implement Drag and Drop card movement",
            description="Write endpoints to dynamically update Card column and order positions.",
            order=1,
            column=todo_col,
            assignee=None
        )
        print("Seeded cards successfully!")
    else:
        print("Cards already seeded.")

    print("Database seeding completed successfully!")

if __name__ == '__main__':
    seed()
