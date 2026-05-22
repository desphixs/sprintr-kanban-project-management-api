# Import the serializers module from Django REST Framework (DRF)
# Serializers are like translators: they convert complex database models into simple JSON formats 
# that frontends (like React or mobile apps) can easily read, and they also validate incoming data 
# before it gets saved into the database.
from rest_framework import serializers

# Import the Project, Board, Column, and Card models we designed in models.py
# We need these models so our serializers know the structural blueprint of the data they are translating.
from kanban.models import Project, Board, Column, Card

# --- CARD SERIALIZER ---
# This class handles the translation of individual Kanban task Cards.
class CardSerializer(serializers.ModelSerializer):
    
    # The Meta class is a configuration container inside the serializer.
    # It tells Django REST Framework which database model to target and which columns to expose.
    class Meta:
        # Link this serializer directly to the Card model
        model = Card
        
        # Expose all fields from the Card model in the translated JSON output
        # This will include: 'id', 'title', 'description', 'order', 'column', and 'assignee'
        fields = '__all__'


# --- COLUMN SERIALIZER ---
# This class handles the translation of Column lists (e.g., "To Do", "Done") and nests its cards inside.
class ColumnSerializer(serializers.ModelSerializer):
    
    # We define a custom nested field called 'cards'.
    # This matches the related_name='cards' ForeignKey relationship we declared in Card model!
    # CardSerializer(many=True) tells DRF that a column can contain multiple task cards (a list).
    # read_only=True ensures that when creating/updating columns, users cannot edit cards through this endpoint,
    # keeping column updates focused and secure.
    cards = CardSerializer(many=True, read_only=True)

    class Meta:
        # Link this serializer to the Column database model
        model = Column
        
        # Explicitly declare which fields we want to output in our translated JSON.
        # We list them individually so we can safely include the nested 'cards' array field.
        fields = ['id', 'title', 'order', 'board', 'cards']


# --- BOARD SERIALIZER ---
# This class translates Boards and nests Columns (which themselves nest Cards) inside.
class BoardSerializer(serializers.ModelSerializer):
    
    # We define a nested field called 'columns'.
    # This matches the related_name='columns' ForeignKey relationship declared in Column model!
    # ColumnSerializer(many=True) tells DRF that a board can contain multiple columns.
    # read_only=True ensures columns cannot be edited through this board endpoint.
    columns = ColumnSerializer(many=True, read_only=True)

    class Meta:
        # Link this serializer to the Board database model
        model = Board
        
        # Explicitly declare fields, including the nested 'columns' list.
        # This builds a multi-level JSON structure: Board -> Columns -> Cards in a single query!
        fields = ['id', 'name', 'project', 'columns']


# --- PROJECT SERIALIZER ---
# This class translates Projects, ensuring proper read-only rules for the project owner.
class ProjectSerializer(serializers.ModelSerializer):
    
    # We explicitly define the 'owner' field as read_only=True.
    # PrimaryKeyRelatedField represents the relationship using the owner's primary key ID.
    # Marking it as read_only=True is vital for security: it ensures a user can never pass a different owner's ID
    # in the request to steal project ownership or assign someone else's project to themselves!
    owner = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        # Link this serializer to the Project database model
        model = Project
        
        # Expose these fields in the project JSON output
        fields = ['id', 'name', 'description', 'owner']
