# Import the standard admin module from django.contrib
# This module allows us to customize the built-in Django Administration interface
from django.contrib import admin

# Import our custom Kanban database models
# We import Project, Board, Column, and Card so we can register them with the admin dashboard
from kanban.models import Project, Board, Column, Card

# --- PROJECT ADMIN CONFIGURATION ---
# We create a custom ModelAdmin class for the Project model.
# This allows us to control how projects are displayed and searched in the admin portal.
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    # 'list_display' defines which columns are shown in the projects list table.
    # We want to see the ID, the name of the project, and the owner.
    list_display = ('id', 'name', 'owner')
    
    # 'search_fields' allows administrators to quickly search projects.
    # It adds a search bar that checks the project's name and the owner's email.
    search_fields = ('name', 'owner__email')
    
    # 'list_filter' adds a sidebar filter on the right.
    # This lets admins filter projects by their owners.
    list_filter = ('owner',)


# --- BOARD ADMIN CONFIGURATION ---
# We customize how Boards are managed inside the admin panel.
@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    # Displays the ID, the Board's name, and the parent Project it belongs to.
    list_display = ('id', 'name', 'project')
    
    # Adds a search box targeting the board's name and the parent project's name.
    search_fields = ('name', 'project__name')
    
    # Adds a sidebar filter to quickly view boards belonging to a specific project.
    list_filter = ('project',)


# --- COLUMN ADMIN CONFIGURATION ---
# We customize the display configuration for the Columns (Workflow phases).
@admin.register(Column)
class ColumnAdmin(admin.ModelAdmin):
    # Displays the ID, Column title, parent Board, and the horizontal order position.
    list_display = ('id', 'title', 'board', 'order')
    
    # Search box targets column titles and parent board names.
    search_fields = ('title', 'board__name')
    
    # Filter columns by their parent boards.
    list_filter = ('board',)


# --- CARD ADMIN CONFIGURATION ---
# We customize how individual task Cards are managed.
@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    # Displays the ID, Card title, parent Column list, vertical order position, and the assignee.
    list_display = ('id', 'title', 'column', 'order', 'assignee')
    
    # Search box targets card titles, descriptions, and assignee emails.
    search_fields = ('title', 'description', 'assignee__email')
    
    # Filters cards by their parent column list and assigned users.
    list_filter = ('column', 'assignee')
