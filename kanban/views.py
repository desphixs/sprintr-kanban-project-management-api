# Import the standard APIView class from DRF, which lets us build custom class-based views
from rest_framework.views import APIView

# Import the Response class, which wraps our data into standard HTTP-compliant responses
from rest_framework.response import Response

# Import the status module containing standard HTTP status code constants (e.g., HTTP_200_OK, HTTP_201_CREATED)
from rest_framework import status

# Import the IsAuthenticated permission class to act as a secure guard for our endpoints
from rest_framework.permissions import IsAuthenticated

# Import the Django built-in Http404 exception to trigger neat 404 Not Found responses easily
from django.http import Http404

# Import our Project and Board models from models.py inside the current app directory
from kanban.models import Project, Board

# Import our ProjectSerializer and BoardSerializer from serializers.py inside the current app directory
from kanban.serializers import ProjectSerializer, BoardSerializer


# --- PROJECT LIST API VIEW ---
# This class handles requests targeting the collection of projects (listing and creating them).
class ProjectListAPIView(APIView):
    # We assign [IsAuthenticated] to permission_classes to ensure that only logged-in users
    # with a valid JSON Web Token (JWT) can access this list and create endpoints!
    permission_classes = [IsAuthenticated]

    # --- GET METHOD ---
    # This method responds to HTTP GET requests. It retrieves and lists all existing projects.
    def get(self, request):
        # We query the database to fetch every single Project record currently saved.
        # Project.objects.all() executes a SELECT * FROM kanban_project query behind the scenes.
        projects = Project.objects.all()

        # We pass our list of project objects into the ProjectSerializer translator.
        # We set many=True because we are translating a list/queryset of multiple project records, not a single one.
        serializer = ProjectSerializer(projects, many=True)

        # We return the translated JSON-like data dictionary inside a Response object.
        # We explicitly set the HTTP status to 200 OK to signal a successful request.
        return Response(serializer.data, status=status.HTTP_200_OK)

    # --- POST METHOD ---
    # This method responds to HTTP POST requests. It allows logged-in users to create a brand new project.
    def post(self, request):
        # We pass the raw data sent by the client (located inside request.data) into the ProjectSerializer.
        # This prepares the serializer to validate and translate the client's inputs.
        serializer = ProjectSerializer(data=request.data)

        # We call serializer.is_valid() to check if the incoming data meets all our constraints.
        # For example, it ensures 'name' is provided and is under 100 characters, and that description is valid.
        if serializer.is_valid():
            # If the data is valid, we call serializer.save() to write the new project row into the database.
            # CRITICAL SECURITY STEP: We manually pass owner=request.user inside save().
            # Because 'owner' is marked as read-only inside ProjectSerializer, the client cannot pass an owner ID.
            # We explicitly grab the currently logged-in user from the authenticated request object and set them as owner.
            serializer.save(owner=request.user)

            # We return the newly created and saved project's serialized data back to the client.
            # We return a status code of 201 Created to signify that a resource was successfully made on the server.
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        # If serializer.is_valid() returns False, it means the client sent invalid or missing data.
        # We return the specific validation errors list so the frontend can display them to the user.
        # We set the status code to 400 Bad Request to indicate a client-side input error.
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# --- PROJECT DETAIL API VIEW ---
# This class handles requests targeting a specific individual project by its unique ID (GET, PUT, and DELETE).
class ProjectDetailAPIView(APIView):
    # We require authentication so that only registered users can view, update, or delete project details.
    permission_classes = [IsAuthenticated]

    # --- GET OBJECT HELPER ---
    # A helper method to fetch a single project by its ID primary key, or raise a 404 error if it doesn't exist.
    def get_object(self, pk):
        # We place our query inside a try-except block to handle cases where a user requests an ID that doesn't exist.
        try:
            # We look up the Project record where the primary key (pk) matches the pk variable in the URL.
            return Project.objects.get(pk=pk)
        except Project.DoesNotExist:
            # If no Project record matches the given ID, Django raises a DoesNotExist exception.
            # We intercept this and raise Http404, which Django REST Framework automatically catches
            # and translates into a uniform JSON response: {"detail": "Not found."} with status 404.
            raise Http404

    # --- GET METHOD ---
    # This method responds to HTTP GET requests for a single project (e.g., GET /api/projects/5/).
    def get(self, request, pk):
        # We call our get_object helper to fetch the project or raise a 404 if it is missing.
        project = self.get_object(pk)

        # We pass the single project record to our ProjectSerializer.
        # We do NOT pass many=True here, because we are translating exactly one project object.
        serializer = ProjectSerializer(project)

        # We return the translated JSON project data to the client with a standard 200 OK status.
        return Response(serializer.data, status=status.HTTP_200_OK)

    # --- PUT METHOD ---
    # This method responds to HTTP PUT requests to update an existing project (e.g., PUT /api/projects/5/).
    def put(self, request, pk):
        # We fetch the specific project we want to edit or fail with a 404 if it does not exist.
        project = self.get_object(pk)

        # SECURITY CHECK: We verify if the project's owner matches the currently logged-in user.
        # We compare the project.owner object with request.user from our token.
        if project.owner != request.user:
            # If they don't match, we block the request! This prevents User A from editing User B's project.
            # We return a 403 Forbidden status signifying that they are authenticated but lack permissions for this item.
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN
            )

        # We feed the existing project object AND the new request data into our serializer.
        # partial=True is a extremely useful flag: it allows the client to send only the fields they want to change,
        # rather than being forced to supply every single field on the model!
        serializer = ProjectSerializer(project, data=request.data, partial=True)

        # We check if the updated data is valid.
        if serializer.is_valid():
            # If valid, we save the changes to the database.
            serializer.save()
            # Return the updated serialized project data with a 200 OK status.
            return Response(serializer.data, status=status.HTTP_200_OK)

        # If validation fails, return the error details with a 400 Bad Request status.
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # --- DELETE METHOD ---
    # This method responds to HTTP DELETE requests to delete a project (e.g., DELETE /api/projects/5/).
    def delete(self, request, pk):
        # We fetch the project or raise a 404 Not Found if the project ID does not exist in our database.
        project = self.get_object(pk)

        # SECURITY CHECK: We verify if the project's owner matches the currently logged-in user.
        if project.owner != request.user:
            # If a different user attempts to delete this project, we block the action instantly.
            # We return a 403 Forbidden status with a descriptive error detail dictionary.
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN
            )

        # If security checks pass, we call the model's delete() method to remove the project row from our database.
        # Note: Thanks to models.CASCADE we defined, deleting this project will also delete all of its boards, columns, and cards!
        project.delete()

        # We return a Response with an HTTP 204 No Content status.
        # 204 is the standard status code indicating a successful deletion with no body content returned.
        return Response(status=status.HTTP_204_NO_CONTENT)


# --- BOARD LIST API VIEW ---
# This class handles requests targeting the collection of boards (listing them and creating a new one).
class BoardListAPIView(APIView):
    # We assign [IsAuthenticated] to permission_classes to ensure that only logged-in users
    # with a valid JSON Web Token (JWT) can access this endpoint!
    permission_classes = [IsAuthenticated]

    # --- GET METHOD ---
    # This method responds to HTTP GET requests. It retrieves and lists all existing boards.
    def get(self, request):
        # We query the database to fetch every single Board record currently saved.
        # Board.objects.all() executes a SELECT * FROM kanban_board query.
        boards = Board.objects.all()

        # We pass our list of board objects into the BoardSerializer translator.
        # We set many=True because we are translating a list of multiple board records, not a single one.
        serializer = BoardSerializer(boards, many=True)

        # We return the translated JSON data inside a Response object with status 200 OK.
        return Response(serializer.data, status=status.HTTP_200_OK)

    # --- POST METHOD ---
    # This method responds to HTTP POST requests. It allows logged-in users to create a brand new board.
    def post(self, request):
        # We extract the project ID value from the client's request data payload.
        # This ID specifies which parent Project this new board should belong to.
        project_id = request.data.get('project')

        # We manually verify if a 'project' field was even sent in the request payload.
        if not project_id:
            # If the project field is missing, return a validation error with status 400 Bad Request.
            return Response(
                {"project": ["This field is required to create a board."]},
                status=status.HTTP_400_BAD_REQUEST
            )

        # We verify that the specified project ID actually exists in our Project database table.
        try:
            project = Project.objects.get(pk=project_id)
        except Project.DoesNotExist:
            # If the query fails, it means the project ID is invalid or doesn't exist.
            # We return a clear error response explaining that the parent project wasn't found.
            return Response(
                {"project": ["The specified parent project does not exist."]},
                status=status.HTTP_400_BAD_REQUEST
            )

        # We pass the raw data sent by the client into the BoardSerializer.
        # This prepares the serializer to validate and translate the client's inputs.
        serializer = BoardSerializer(data=request.data)

        # We call serializer.is_valid() to check if the incoming data meets all our constraints (e.g., name is provided).
        if serializer.is_valid():
            # If the data is valid, we call serializer.save() to write the new board record into the database.
            serializer.save()

            # We return the newly created and saved board's serialized data back to the client.
            # We return a status code of 201 Created to signify a successful resource creation.
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        # If validation fails, return the error details with a 400 Bad Request status.
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# --- BOARD DETAIL API VIEW ---
# This class handles requests targeting a specific individual board by its unique ID (GET, PUT, and DELETE).
class BoardDetailAPIView(APIView):
    # We require authentication so that only registered users can view, update, or delete board details.
    permission_classes = [IsAuthenticated]

    # --- GET OBJECT HELPER ---
    # A helper method to fetch a single board by its ID primary key, or raise a 404 error if it doesn't exist.
    def get_object(self, pk):
        # We place our query inside a try-except block to handle cases where a user requests an ID that doesn't exist.
        try:
            # We look up the Board record where the primary key (pk) matches the pk variable in the URL.
            return Board.objects.get(pk=pk)
        except Board.DoesNotExist:
            # If no Board record matches the given ID, Django raises a DoesNotExist exception.
            # We intercept this and raise Http404, which DRF automatically translates to a 404 response.
            raise Http404

    # --- GET METHOD ---
    # This method responds to HTTP GET requests for a single board (e.g., GET /api/boards/5/).
    # Note: When returning the board, the nested BoardSerializer will automatically list the columns and cards!
    def get(self, request, pk):
        # We call our get_object helper to fetch the board or raise a 404 if it is missing.
        board = self.get_object(pk)

        # We pass the single board record to our BoardSerializer.
        # This will output a beautiful nested JSON payload: Board -> Columns -> Cards!
        serializer = BoardSerializer(board)

        # We return the translated JSON board data with a standard 200 OK status.
        return Response(serializer.data, status=status.HTTP_200_OK)

    # --- PUT METHOD ---
    # This method responds to HTTP PUT requests to update an existing board (e.g., PUT /api/boards/5/).
    def put(self, request, pk):
        # We fetch the specific board we want to edit or fail with a 404 if it does not exist.
        board = self.get_object(pk)

        # We feed the existing board object AND the new request data into our serializer.
        # partial=True allows the client to send only the fields they want to change.
        serializer = BoardSerializer(board, data=request.data, partial=True)

        # We check if the updated data is valid.
        if serializer.is_valid():
            # If valid, we save the changes to the database.
            serializer.save()
            # Return the updated serialized board data with a 200 OK status.
            return Response(serializer.data, status=status.HTTP_200_OK)

        # If validation fails, return the error details with a 400 Bad Request status.
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # --- DELETE METHOD ---
    # This method responds to HTTP DELETE requests to delete a board (e.g., DELETE /api/boards/5/).
    def delete(self, request, pk):
        # We fetch the board or raise a 404 Not Found if the board ID does not exist in our database.
        board = self.get_object(pk)

        # We call the model's delete() method to remove the board row from our database.
        # Note: Thanks to models.CASCADE we defined, deleting this board will also delete all of its columns and cards!
        board.delete()

        # We return a Response with an HTTP 204 No Content status.
        return Response(status=status.HTTP_204_NO_CONTENT)

