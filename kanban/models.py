# Import the standard models module from django.db
# This module gives us all the database building blocks (like CharField, IntegerField, ForeignKey, etc.)
from django.db import models

# Import the settings object from django.conf
# We use this to retrieve settings.AUTH_USER_MODEL so we can link models to our custom User class safely
from django.conf import settings

# --- PROJECT MODEL ---
# A Project is the top-level container in our application (like a workspace in Slack or Jira).
# It will group together all our boards, columns, and cards.
class Project(models.Model):
    # 'name' represents the short, descriptive title of the project (e.g., "Build mobile app").
    # CharField creates a standard VARCHAR column in the SQL database.
    # max_length=100 sets a strict limit of 100 characters so people don't write endless essays in the title.
    name = models.CharField(max_length=100)

    # 'description' is a text field that holds longer descriptive paragraphs explaining the project.
    # TextField creates a TEXT column in the database, allowing for long paragraphs.
    # blank=True means this field is optional in forms, so projects can be created without a description.
    description = models.TextField(blank=True)

    # 'owner' links this project to the User model (the person who created the project).
    # ForeignKey creates a "Many-to-One" relationship, meaning one user can own many projects.
    # settings.AUTH_USER_MODEL points to our custom email-based User model.
    # on_delete=models.CASCADE means if a user account is deleted, all their projects are deleted too!
    # related_name='projects' allows us to easily get all projects owned by a user (e.g., user.projects.all()).
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='projects'
    )

    # The __str__ method defines the human-readable string representation of this object.
    # When this object is printed in logs or the Django admin panel, it will display the project's name.
    def __str__(self):
        # Return the project's name as the string representation
        return self.name


# --- BOARD MODEL ---
# A Board represents a specific workflow workspace inside a project (like a "Frontend Development" or "Marketing" board).
class Board(models.Model):
    # 'name' represents the display title of the Board (e.g., "Sprint 1 Board").
    # CharField creates a standard VARCHAR column with a limit of 100 characters.
    name = models.CharField(max_length=100)

    # 'project' links this board to its parent Project container.
    # ForeignKey establishes a "Many-to-One" relationship (a project can have many boards).
    # on_delete=models.CASCADE means if the project is deleted, this board is deleted too.
    # related_name='boards' allows us to retrieve all boards for a project (e.g., project.boards.all()).
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='boards'
    )

    # The __str__ method defines the human-readable string representation of this Board.
    # When displayed, it will output the board name, helping admins identify it easily.
    def __str__(self):
        # Return the board's name as the string representation
        return self.name


# --- COLUMN MODEL ---
# A Column represents a list or workflow phase on a Board (e.g., "To Do", "In Progress", "Done").
class Column(models.Model):
    # 'title' represents the display title of the column (e.g., "To Do").
    # CharField creates a VARCHAR column in the database with a limit of 100 characters.
    title = models.CharField(max_length=100)

    # 'order' is an integer used to define the horizontal order of columns on the board.
    # IntegerField creates a standard INT column in the database.
    # This allows us to sort columns (e.g., 0 for "To Do", 1 for "In Progress", 2 for "Done").
    order = models.IntegerField()

    # 'board' links this column to its parent Board.
    # ForeignKey establishes a "Many-to-One" relationship (a board can have many columns).
    # on_delete=models.CASCADE means if the board is deleted, all its columns are deleted as well.
    # related_name='columns' allows us to retrieve all columns on a board (e.g., board.columns.all()).
    board = models.ForeignKey(
        Board,
        on_delete=models.CASCADE,
        related_name='columns'
    )

    # The __str__ method defines the human-readable string representation of this Column.
    # It shows both the column's title and its parent board's name to provide clear context.
    def __str__(self):
        # Return the column title and its parent board name as the string representation
        return f"{self.title} ({self.board.name})"


# --- CARD MODEL ---
# A Card represents an individual task or ticket (e.g., "Fix navbar login button").
# Cards sit inside columns and can be moved from column to column or assigned to users.
class Card(models.Model):
    # 'title' represents the short summary of the task.
    # CharField creates a VARCHAR column with a limit of 100 characters.
    title = models.CharField(max_length=100)

    # 'description' holds detailed notes, instructions, or subtasks for this card.
    # TextField creates a TEXT column in the database, allowing for long paragraphs.
    # blank=True and null=True mean this field is completely optional; a task card can exist without a description.
    description = models.TextField(blank=True, null=True)

    # 'order' is an integer used to define the vertical ordering of cards within a single column.
    # IntegerField creates an INT column, so we can display cards in the correct sequence (e.g., card 0, card 1).
    order = models.IntegerField()

    # 'column' links this card to its parent Column list.
    # ForeignKey establishes a "Many-to-One" relationship (a column can hold many cards).
    # on_delete=models.CASCADE means if a column is deleted, all cards in it are deleted too.
    # related_name='cards' allows us to retrieve all cards inside a column (e.g., column.cards.all()).
    column = models.ForeignKey(
        Column,
        on_delete=models.CASCADE,
        related_name='cards'
    )

    # 'assignee' links this card to the User who is responsible for doing the work.
    # ForeignKey establishes a relationship (a user can be assigned many cards).
    # settings.AUTH_USER_MODEL points to our custom email-based User model.
    # on_delete=models.SET_NULL means if the assignee user account is deleted, the card is NOT deleted.
    # Instead, the assignee field is set to NULL (unassigned).
    # null=True allows the database to store NULL (no user).
    # blank=True allows serializers/forms to submit this field as empty/blank.
    # related_name='assigned_cards' allows us to easily get all cards assigned to a user (e.g., user.assigned_cards.all()).
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_cards'
    )

    # The __str__ method defines the human-readable string representation of this Card.
    # Displaying the title of the card makes it easy to identify.
    def __str__(self):
        # Return the card's title as the string representation
        return self.title
