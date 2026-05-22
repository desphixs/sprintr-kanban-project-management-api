# Import the path function from django.urls to define individual endpoint routes
from django.urls import path

# Import our view classes from views.py in the current folder
from kanban.views import (
    ProjectListAPIView, 
    ProjectDetailAPIView,
    BoardListAPIView,
    BoardDetailAPIView
)

# Define a list of URL routing patterns specific to the kanban application.
# Every route in this list will map an incoming URL path pattern to a specific class-based view.
urlpatterns = [
    # --- PROJECTS LIST & CREATE ROUTE ---
    # When a client hits 'projects/', DRF routes the request to ProjectListAPIView.
    # We call .as_view() because Django's routing system expects a callable function, and as_view()
    # acts as the entry point that converts our class-based view into that callable function.
    # We define name='project-list' as a unique label so we can reference this route dynamically elsewhere.
    path('projects/', ProjectListAPIView.as_view(), name='project-list'),

    # --- SPECIFIC PROJECT DETAIL ROUTE ---
    # This route contains a dynamic URL parameter: <int:pk>.
    # - '<int:pk>' tells Django to capture whatever integer is written in that segment of the URL
    #   (e.g., /api/projects/15/) and pass it to our view method as a keyword argument named 'pk'.
    # DRF routes requests with this format to ProjectDetailAPIView.as_view() so it can handle single records.
    # We set name='project-detail' as the unique label for this specific detail route.
    path('projects/<int:pk>/', ProjectDetailAPIView.as_view(), name='project-detail'),

    # --- BOARDS LIST & CREATE ROUTE ---
    # When a client hits 'boards/', DRF routes the request to BoardListAPIView.
    # .as_view() registers the class-based view so it receives standard GET and POST requests.
    # We label this route as name='board-list' for easy dynamic lookup.
    path('boards/', BoardListAPIView.as_view(), name='board-list'),

    # --- SPECIFIC BOARD DETAIL ROUTE ---
    # This route contains the dynamic URL parameter: <int:pk>.
    # Any GET, PUT, or DELETE request targeting a single board (e.g. /api/boards/3/)
    # will automatically parse the number 3 and pass it to BoardDetailAPIView as the 'pk' argument.
    # We label this route as name='board-detail' for dynamic URL reversing.
    path('boards/<int:pk>/', BoardDetailAPIView.as_view(), name='board-detail'),
]

