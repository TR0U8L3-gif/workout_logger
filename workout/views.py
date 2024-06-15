"""
views.py

This module contains the views for the workout app.
"""
 

from django.shortcuts import render, redirect
from django.contrib import messages # access django's `messages` module.
from .models import *
from django.db.models import Q
from .views_helper import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from itertools import chain
import logging 
import datetime
from itertools import chain
from django.shortcuts import redirect
from django.utils import timezone
from datetime import timedelta


current_date = datetime.datetime.now().strftime("%Y-%m-%d")
filename = f"workout_{current_date}.log"

logging.basicConfig(level=logging.DEBUG, filename=filename, filemode="a+", format="%(asctime)s - %(levelname)s - %(message)s: ")

# authentication
def login(request):
    """
    GET - Loads login page. POST - Logs in user.

    Args:
        request: Django HttpRequest object.

    Returns:
        Django HttpResponse object.
    """

    if request.method == "GET":
        logging.debug("GET request to login")
        return render(request, "workout/index.html")

    if request.method == "POST":
        logging.debug("POST request to login")
        # Validate login data:
        validated = User.objects.login(**request.POST)
        try:
            # If errors, reload login page with errors:
            if len(validated["errors"]) > 0:
                print("User could not be logged in.")
                logging.warning("User could not be logged in.")
                # Loop through errors and Generate Django Message for each with custom level and tag:
                for error in validated["errors"]:
                    messages.error(request, error, extra_tags='login')
                    logging.error(error)
                # Reload login page:
                return redirect("/")
        except KeyError:
            # If validation successful, set session, and load dashboard based on user level:
            print("User passed validation and is logged in.")
            # Set session to validated User:
            request.session["user_id"] = validated["logged_in_user"].id
            # Fetch dashboard data and load appropriate dashboard page:
            return redirect("/dashboard")

def register(request):
    """
    GET - Load register page. POST - Register user.

    Args:
        request: Django HttpRequest object.

    Returns:
        Django HttpResponse object.
    """

    if request.method == "GET":
        logging.debug("GET request to register")
        return render(request, "workout/register.html")

    if request.method == "POST":
        logging.debug("POST request to register")
        # Validate registration data:
        validated = User.objects.register(**request.POST)
        # If errors, reload register page with errors:
        try:
            if len(validated["errors"]) > 0:
                print("User could not be registered.")
                # Loop through errors and Generate Django Message for each with custom level and tag:
                for error in validated["errors"]:
                    messages.error(request, error, extra_tags='registration')
                    logging.error(error)
                # Reload register page:
                return redirect("/user/register")
        except KeyError:
            # If validation successful, set session and load dashboard based on user level:
            print("User passed validation and has been created.")
            # Set session to validated User:
            request.session["user_id"] = validated["logged_in_user"].id
            # Load Dashboard:
            return redirect('/dashboard')

def logout(request):
    """Logs out current user"""

    try:
        # Deletes session:
        del request.session['user_id']
        # Adds success message:
        messages.success(request, "You have been logged out.", extra_tags='logout')
        logging.info("User has been logged out.")

    except KeyError:
        pass

    # Return to index page:
    return redirect("/")

# dashboard
def dashboard(request):
    """
    GET - Loads dashboard.

    Args:
        request: Django HttpRequest object.
        user: User object.
        recent_workouts: QuerySet of recent workouts.
        data: Dictionary of page data.

    Returns:
        Django HttpResponse object.
    """

    try:
        # Check for valid session:
        user = User.objects.get(id=request.session["user_id"])

        # Get recent workouts for logged in user:
        recent_workouts = Workout.objects.filter(user__id=user.id).order_by('-id')[:4]
        # user_challenges = UserChallenge.objects.filter(user__id=user.id)
        user_challenges = UserChallenge.objects.filter(user=user)
        print(user_challenges)
        # Gather any page data:
        data = {
            'user': user,
            'recent_workouts': recent_workouts,
            'user_challenges': user_challenges,
        }

        # Load dashboard with data:
        return render(request, "workout/dashboard.html", data)

    except (KeyError, User.DoesNotExist) as err:
        # If existing session not found:
        messages.info(request, "You must be logged in to view this page.", extra_tags="invalid_session")
        logging.warning("User must be logged in to view 'dashboard'.")
        return redirect("/")

def view_all(request):
    """
    GET - Loads `View All` Workouts page.

    Args:
        request: Django HttpRequest object.
        user: User object.
        workout_list: QuerySet of all workouts.
        ste_list: QuerySet of all StrengthTrainingExercises.
        ete_list: QuerySet of all EnduranceTrainingExercises.
        be_list: QuerySet of all BalanceExercises.
        fe_list: QuerySet of all FlexibilityExercises.
        page: Current page number.
        data_list: List of all exercises.
        paginator: Paginator object.
        data: Dictionary of page data.

    Returns:
        Django HttpResponse object.
    """

    try:
        # Check for valid session:
        user = User.objects.get(id=request.session["user_id"])

        workout_list = Workout.objects.filter(user__id=user.id)
        ste_list = StrengthTrainingExercise.objects.filter(user__id=user.id)
        ete_list = EnduranceTrainingExercise.objects.filter(user__id=user.id)
        be_list = BalanceExercise.objects.filter(user__id=user.id)
        fe_list = FlexibilityExercise.objects.filter(user__id=user.id)
        
        page = request.GET.get('page', 1)
        data_list = list(chain(workout_list, ste_list,ete_list, be_list, fe_list))
        paginator = Paginator(sorted(data_list, key=lambda x: x.updated_at, reverse=True), 12)
        try:
            data = paginator.page(page)
        except PageNotAnInteger:
            data = paginator.page(1)
        except EmptyPage:
            data = paginator.page(paginator.num_pages)

        # Gather any page data:
        data = {
            'user': user,
            'data': data,
        }

        # Load dashboard with data:
        return render(request, "workout/view_all.html", data)

    except (KeyError, User.DoesNotExist) as err:
        # If existing session not found:
        messages.info(request, "You must be logged in to view this page.", extra_tags="invalid_session")
        logging.warning("User must be logged in to view 'view_all'.")
        return redirect("/")

# challanges
def challenges(request):
    """
    GET - Loads `Challenges` page.
    
    Args:
        request: Django HttpRequest object.
        user: User object.
        workouts: QuerySet of all workouts.
        challenges: QuerySet of all challenges.
        data: Dictionary of page data.  
        
    Returns:
        Django HttpResponse object.
    """
    try:
        # Check if the session is valid:
        user = User.objects.get(id=request.session["user_id"])

        # Get workouts assigned to the logged-in user or shared workouts:
        challenges = Workout.objects.filter(Q(is_shared=True) & ~Q(challenge=None))
        print(challenges)

        # Get unique challenges from those workouts:
        # challenges = Challenge.objects.filter(workout__in=workouts).distinct()

        # Collect page data:
        data = {
            'user': user,
            'challenges': challenges,
        }

        # Load the page with challenges with data:
        return render(request, "workout/challenges.html", data)
    except User.DoesNotExist:
        # Handling case when the user is not logged in or does not exist
        return redirect('login')  # Redirect to login page or handle the error appropriately

def join_challenge(request, challenge_id):
    user = User.objects.get(id=request.session["user_id"])
    challenge = Challenge.objects.get(id=1)
    workout = Workout.objects.get(id=challenge_id)
    print(workout)
    print(challenge)
    
    if request.method == "GET":
        data = {
            'user': user,
            'challenge': challenge,
        }
        return render(request, "workout/join_challenge.html", data)

    if request.method == "POST":
        user_challenge, created = UserChallenge.objects.get_or_create(user=user, challenge=challenge, workout=workout)
        if created:
            messages.success(request, "Successfully joined the challenge.")
        else:
            messages.info(request, "You have already joined this challenge.")
        return redirect("challenges")
    
def view_challenge(request, id):
    """
    GET - View workout.

    Args:
        request: Django HttpRequest object.
        user: User object.
        workout: Workout object.
        data: Dictionary of page data.

    Returns:
        Django HttpResponse object.
    """
    exercise_type = request.GET.get('exercise_type')
    current_muscle_group_id = request.GET.get('current_muscle_group_id')
    if(exercise_type == None):
        exercise_type = StrengthTrainingExercise().class_name
    if(current_muscle_group_id == None):
        current_muscle_group_id = 0
    
    try:
        # Check for valid session:
        user = User.objects.get(id=request.session["user_id"])
        user_challenge = UserChallenge.objects.get(id=1)
        workout = Workout.objects.get(id=user_challenge.workout_id)
        challenge = Challenge.objects.get(id=user_challenge.challenge_id)


        # Getting all exercises for this workout: 
        ste = StrengthTrainingExercise.objects.filter(workout__id=id)
        ete = EnduranceTrainingExercise.objects.filter(workout__id=id)
        be = BalanceExercise.objects.filter(workout__id=id)
        fe = FlexibilityExercise.objects.filter(workout__id=id)
        
        exercises = list(chain(ste, ete, be, fe))

        # Gather any page data:
        data = {
            'user': user,
            'workout': workout,
            'challenge': challenge,
            'exercises': sorted(exercises, key=lambda x: x.updated_at, reverse=True),
            'muscle_groups': MuscleGroup.objects.order_by('name'),
            'exercise_types': get_exercises_types(),
            'current_exercise': exercise_type,
            'current_muscle_group_id': int(current_muscle_group_id),
        }

        # If get request, load workout page with data:
        return render(request, "workout/view_challenge.html", data)

    except (KeyError, User.DoesNotExist) as err:
        # If existing session not found:
        messages.info(request, "You must be logged in to view this page.", extra_tags="invalid_session")
        logging.warning("User must be logged in to view 'workout'.")
        return redirect("/")

# muscle group
def muscle_group(request):
    """
    GET - View muscle groups.

    Args:
        request: Django HttpRequest object.
        user: User object.
        muscle_group: QuerySet of all muscle groups.
        data: Dictionary of page data.

    Returns:
        Django HttpResponse object.
    """
    try:
        # Check for valid session:
        user = User.objects.get(id=request.session["user_id"])
        
        muscle_group = MuscleGroup.objects.all().order_by('name')

        print(muscle_group)
        
        # Gather any page data:
        data = {
            'user': user,
            'muscle_group': muscle_group,
        }

        # If get request, load workout page with data:
        return render(request, "workout/muscle_group.html", data)

    except (KeyError, User.DoesNotExist) as err:
        # If existing session not found:
        messages.info(request, "You must be logged in to view this page.", extra_tags="invalid_session")
        logging.warning("User must be logged in to view 'muscle_group'.")
        return redirect("/")

# exercise
def exercise(request, id):
    """
    GET - View exercise.

    Args:
        request: Django HttpRequest object.
        user: User object.
        exercise: Exercise object.
        data: Dictionary of page data.  

    Returns:
        Django HttpResponse object.
    """
    exercise_type = request.GET.get('exercise_type')
    if(exercise_type == None):
        messages.error(request, "You must select an exercise type.", extra_tags='exercise')
        logging.error("User must select an exercise type.")
        return redirect("/exercise")
    
    try:
        # Check for valid session:
        user = User.objects.get(id=request.session["user_id"])
        exercise_class = get_exercise_by_class_name(exercise_type)
        exercise = exercise_class.objects.get(id=id)
        redirect_url = "/exercise"
        
        # check if workout is owned by user
        if exercise.user != user:
            messages.error(request, "You do not have permission to view this exercise.", extra_tags='exercise')
            logging.error("User does not have permission to view exercise.")
            return redirect("/exercise")
            
        workout_id = None
        try:
            workout_id = request.GET["redirect_workout"]
            if(workout_id != None):
                redirect_url = "/workout/" + workout_id
        except KeyError as err:
            pass
        
        try:
            redirect_view_all = request.GET["redirect_view_all"]
            if(redirect_view_all != None and redirect_view_all == "true"):
                redirect_url = "/history"
        except KeyError as err:
            pass
        
        # Gather any page data:
        data = {
            'user': user,
            'exercise': exercise,
            'workouts': Workout.objects.filter(user__id=user.id).order_by('-updated_at'),
            'muscle_groups': MuscleGroup.objects.all().order_by('-updated_at'),
            'redirect_url': redirect_url,
            'redirect_workout': workout_id,
        }

        # If get request, load exercise page with data:
        return render(request, "workout/exercise.html", data)

    except (KeyError, User.DoesNotExist) as err:
        # If existing session not found:
        messages.info(request, "You must be logged in to view this page.", extra_tags="invalid_session")
        logging.warning("User must be logged in to view 'exercise'.")
        return redirect("/")

def edit_exercise(request, id):
    """
    GET - load edit exercise, POST - submit edit exercise

    Args:
        request: Django HttpRequest object.
        user: User object.
        exercise: Exercise object.
        data: Dictionary of page data.

    Returns:
        Django HttpResponse object. 
    """
        
    try:
        user = User.objects.get(id=request.session["user_id"])
        
        if request.method == "GET":
            logging.debug("GET request to edit exercise")

            # If get request, load edit exercise page with data:
            return redirect("/exercise/" + id)

        if request.method == "POST":
            logging.debug("POST request to edit exercise")
            workout_id = request.POST["workout_id"]
            muscle_group_id = request.POST["muscle_group"]
            exercise_type = request.POST["exercise_type"]

            try:
                redirect_url = request.POST["redirect"]
            except KeyError as err:
                pass

            exercise = get_exercise_by_class_name(exercise_type)
            
            exercise_model = {
                "exercise_id": id,
                "name": request.POST["name"],
                "description": request.POST["description"],
                "workout": Workout.objects.get(id=workout_id),
                "muscle_group": MuscleGroup.objects.get(id=muscle_group_id),
                "user": user,
            }
            
            # Add form data to exercise model:
            for form_field in exercise().form_data():
                exercise_model[form_field.name] = request.POST[form_field.name]

            # Begin validation of a new exercise:
            validated = exercise.objects.update_exercise(**exercise_model)
            
            # If errors, reload register page with errors:
            try:
                if len(validated["errors"]) > 0:
                    logging.error("Exercise could not be edited.")
                    print("Exercise could not be created.")

                    # Loop through errors and Generate Django Message for each with custom level and tag:
                    for error in validated["errors"]:
                        messages.error(request, error, extra_tags='exercise')
                        logging.error(error)
                    # Reload workout page:
                    return redirect("/exercise/" + id + "?exercise_type=" + exercise_type + "&current_muscle_group_id=" + muscle_group_id + "&current_workout_id=" + workout_id)
            except KeyError:
                # If validation successful, load newly created workout page:
                print("Exercise passed validation and has been created.")
                # Reload workout:
                return redirect("/exercise/" + id + "?exercise_type=" + exercise_type + "&current_muscle_group_id=" + muscle_group_id + "&current_workout_id=" + workout_id)
    except (KeyError, User.DoesNotExist) as err:
        # If existing session not found:
        messages.info(request, "You must be logged in to view this page.", extra_tags="invalid_session")
        logging.warning("User must be logged in to view 'edit_exercise'.")
        return redirect("/")

def new_exercise(request):
    """
    GET - load new exercise, POST - submit new exercise

    Args:
        request: Django HttpRequest object.
        user: User object.
        exercise: Exercise object.
        data: Dictionary of page data.
    
    Returns:
        Django HttpResponse object.
    """
    
    exercise_type = request.GET.get('exercise_type')
    if(exercise_type == None):
        exercise_type = StrengthTrainingExercise().class_name
    current_workout_id = request.GET.get('current_workout_id')
    if(current_workout_id == None):
        current_workout_id = -1
    current_muscle_group_id = request.GET.get('current_muscle_group_id')
    if(current_muscle_group_id == None):
        current_muscle_group_id = -1
        
    try:
        # Check for valid session:
        user = User.objects.get(id=request.session["user_id"]) 
        
        ste = StrengthTrainingExercise.objects.filter(user__id=user.id)
        ete = EnduranceTrainingExercise.objects.filter(user__id=user.id)
        be = BalanceExercise.objects.filter(user__id=user.id)
        fe = FlexibilityExercise.objects.filter(user__id=user.id)
        
        exercises = list(chain(ste, ete, be, fe))
        
        # Gather any page data:
        data = {
            'user': user,
            'exercises': sorted(exercises, key=lambda x: x.updated_at, reverse=True),
            'exercise_types': get_exercises_types(),
            'current_exercise': exercise_type,
            'current_workout_id': int(current_workout_id),
            'current_muscle_group_id': int(current_muscle_group_id),
            'workouts': Workout.objects.filter(user__id=user.id).order_by('-updated_at'), 
            'muscle_groups': MuscleGroup.objects.order_by('name'),

        }
        
        if request.method == "GET":
            logging.debug("GET request to new exercise")
            # If get request, load `add exercise` page with data:
            return render(request, "workout/add_exercise.html", data)

        if request.method == "POST":
            logging.debug("POST request to new exercise")
            workout_id = request.POST["workout_id"]
            muscle_group_id = request.POST["muscle_group"]
            exercise_type = request.POST["exercise_type"]
            redirect_url = "/exercise"
            
            
            if(exercise_type == None):
                exercise_type = StrengthTrainingExercise().class_name
            
            try:
                redirect_url = request.POST["redirect"]
            except KeyError as err:
                pass

            exercise = get_exercise_by_class_name(exercise_type)
            
            exercise_model = {
                "name": request.POST["name"],
                "description": request.POST["description"],
                "workout": Workout.objects.get(id=workout_id),
                "muscle_group": MuscleGroup.objects.get(id=muscle_group_id),
                "user": user,
            }
            
            # Add form data to exercise model:
            for form_field in exercise().form_data():
                exercise_model[form_field.name] = request.POST[form_field.name]

            # Begin validation of a new exercise:
            validated = exercise.objects.new_exercise(**exercise_model)
            
            # If errors, reload register page with errors:
            try:
                if len(validated["errors"]) > 0:
                    logging.error("Exercise could not be created.")
                    print("Exercise could not be created.")

                    # Loop through errors and Generate Django Message for each with custom level and tag:
                    for error in validated["errors"]:
                        messages.error(request, error, extra_tags='exercise')
                        logging.error(error)
                    # Reload workout page:
                    return redirect(redirect_url + "?exercise_type=" + exercise_type + "&current_muscle_group_id=" + muscle_group_id + "&current_workout_id=" + workout_id)
            except KeyError:
                # If validation successful, load newly created workout page:
                print("Exercise passed validation and has been created.")
                # Reload workout:
                return redirect( redirect_url + "?exercise_type=" + exercise_type + "&current_muscle_group_id=" + muscle_group_id + "&current_workout_id=" + workout_id)
    except (KeyError, User.DoesNotExist) as err:
        # If existing session not found:
        messages.info(request, "You must be logged in to view this page.", extra_tags="invalid_session")
        logging.warning("User must be logged in to view 'new_exercise'.")
        return redirect("/")       
    
def delete_exercise(request, id):
    """
    GET - Delete a exercise.

    Args:
        request: Django HttpRequest object.
        user: User object.
        exercise: Exercise object.
        data: Dictionary of page data.

    Returns:
        Django HttpResponse object.
    """
    try:
        # Check for valid session:
        user = User.objects.get(id=request.session["user_id"])
        
        redirect_url = "/exercise" 
        try:
            workout_id = request.GET["redirect_workout"]
            if(workout_id != None):
                redirect_url = "/workout/" + workout_id
        except KeyError as err:
            pass
        
        try:
            redirect_view_all = request.GET["redirect_view_all"]
            if(redirect_view_all != None and redirect_view_all == "true"):
                redirect_url = "/history"
        except KeyError as err:
            pass

        exercise_type = request.GET.get('exercise_type')
        if(exercise_type == None):
            messages.error(request, "You must select an exercise type.", extra_tags='exercise')
            logging.error("User must select an exercise type.")
            return redirect(redirect_url + "/" + id)
    
        # check if exercise is owned by user
        exercise_class = get_exercise_by_class_name(exercise_type)
        exercise = exercise_class.objects.get(id=id)

        if exercise.user != user:
            messages.error(request, "You do not have permission to delete this exercise.", extra_tags='exercise')
            logging.error("User does not have permission to delete exercise.")
            return redirect(redirect_url) 
        else:
            # Delete workout:
            exercise.delete()
        
        # Load dashboard:
        return redirect(redirect_url)


    except (KeyError, User.DoesNotExist) as err:
        # If existing session not found:
        messages.info(request, "You must be logged in to view this page.", extra_tags="invalid_session")
        logging.warning("User must be logged in to view 'delete_exercise'.")
        return redirect("/")

# workout 
def workout(request, id):
    """
    GET - View workout.

    Args:
        request: Django HttpRequest object.
        user: User object.
        workout: Workout object.
        data: Dictionary of page data.

    Returns:
        Django HttpResponse object.
    """
    exercise_type = request.GET.get('exercise_type')
    current_muscle_group_id = request.GET.get('current_muscle_group_id')
    if(exercise_type == None):
        exercise_type = StrengthTrainingExercise().class_name
    if(current_muscle_group_id == None):
        current_muscle_group_id = 0
    
    try:
        # Check for valid session:
        user = User.objects.get(id=request.session["user_id"])
        workout = Workout.objects.get(id=id)
        
        # check if workout is owned by user
        if workout.user != user:
            messages.error(request, "You do not have permission to view this workout.", extra_tags='workout')
            logging.error("User does not have permission to view workout.")
            return redirect("/workout")

        # Getting all exercises for this workout: 
        ste = StrengthTrainingExercise.objects.filter(workout__id=id)
        ete = EnduranceTrainingExercise.objects.filter(workout__id=id)
        be = BalanceExercise.objects.filter(workout__id=id)
        fe = FlexibilityExercise.objects.filter(workout__id=id)
        
        exercises = list(chain(ste, ete, be, fe))

        # Gather any page data:
        data = {
            'user': user,
            'workout': workout,
            'exercises': sorted(exercises, key=lambda x: x.updated_at, reverse=True),
            'muscle_groups': MuscleGroup.objects.order_by('name'),
            'exercise_types': get_exercises_types(),
            'current_exercise': exercise_type,
            'current_muscle_group_id': int(current_muscle_group_id),
        }

        # If get request, load workout page with data:
        return render(request, "workout/workout.html", data)

    except (KeyError, User.DoesNotExist) as err:
        # If existing session not found:
        messages.info(request, "You must be logged in to view this page.", extra_tags="invalid_session")
        logging.warning("User must be logged in to view 'workout'.")
        return redirect("/")

def edit_workout(request, id):
    """
    GET - load edit workout, POST - submit edit workout

    Args:
        request: Django HttpRequest object.
        user: User object.
        workout: Workout object.
        data: Dictionary of page data.  

    Returns:
        Django HttpResponse object.
    """

    try:
        # Check for valid session:
        user = User.objects.get(id=request.session["user_id"])
        
        # Getting all exercises for this workout: 
        ste = StrengthTrainingExercise.objects.filter(workout__id=id)
        ete = EnduranceTrainingExercise.objects.filter(workout__id=id)
        be = BalanceExercise.objects.filter(workout__id=id)
        fe = FlexibilityExercise.objects.filter(workout__id=id)
        
        exercises = list(chain(ste, ete, be, fe))
            
        # Gather any page data:
        data = {
            'user': user,
            'workout': Workout.objects.get(id=id),
            'exercises': sorted(exercises, key=lambda x: x.updated_at, reverse=True),
        }

        if request.method == "GET":
            logging.debug("GET request to edit workout")
            # If get request, load edit workout page with data:
            return render(request, "workout/edit_workout.html", data)
        if request.method == "POST":
            logging.debug("POST request to edit workout")
            # check if workout is owned by user
            if data['workout'].user != user:
                messages.error(request, "You do not have permission to delete this workout.", extra_tags='workout')
                logging.error("User does not have permission to delete workout.")
                return redirect("/workout") 
            # If post request, validate update workout data:
            # Unpack request object and build our custom tuple:
            workout = {
                'name': request.POST['name'],
                'description': request.POST['description'],
                'workout_id': data['workout'].id,
            }
            # Begin validation of updated workout:
            validated = Workout.objects.update(**workout)
            # If errors, reload register page with errors:
            try:
                if len(validated["errors"]) > 0:
                    logging.error("Workout could not be edited.")
                    print("Workout could not be edited.")
                    # Loop through errors and Generate Django Message for each with custom level and tag:
                    for error in validated["errors"]:
                        messages.error(request, error, extra_tags='edit')
                        logging.error(error)
                    # Reload workout page:
                    return redirect("/workout/" + str(data['workout'].id) + "/edit")
            except KeyError:
                # If validation successful, load newly created workout page:
                print("Edited workout passed validation and has been updated.")
                # Load workout:
                return redirect("/workout/" + str(data['workout'].id) + "/edit")

    except (KeyError, User.DoesNotExist) as err:
        # If existing session not found:
        messages.info(request, "You must be logged in to view this page.", extra_tags="invalid_session")
        logging.warning("User must be logged in to view 'edit_workout'.")
        return redirect("/")

def new_workout(request):
    """
    GET - load new workout, POST - submit new workout

    Args:
        request: Django HttpRequest object.
        user: User object.
        workout: Workout object.
        data: Dictionary of page data.  

    Returns:
        Django HttpResponse object.
    """

    try:
        # Check for valid session:
        user = User.objects.get(id=request.session["user_id"])
        workouts = Workout.objects.filter(user__id=user.id).order_by('-updated_at')
        # Gather any page data:
        data = {
            'user': user,
            'workouts': workouts,
        }

        if request.method == "GET":
            logging.debug("GET request to new workout")
            # If get request, load `add workout` page with data:
            return render(request, "workout/add_workout.html", data)

        if request.method == "POST":
            logging.debug("POST request to new workout")
            # Unpack request.POST for validation as we must add a field and cannot modify the request.POST object itself as it's a tuple:
            workout = {
                "name": request.POST["name"],
                "description": request.POST["description"],
                "user": user
            }

            # Begin validation of a new workout:
            validated = Workout.objects.new(**workout)

            # If errors, reload register page with errors:
            try:
                if len(validated["errors"]) > 0:
                    logging.error("Workout could not be created.")
                    print("Workout could not be created.")
                    # Loop through errors and Generate Django Message for each with custom level and tag:
                    for error in validated["errors"]:
                        messages.error(request, error, extra_tags='workout')
                        logging.error(error)
                    # Reload workout page:
                    return redirect("/workout")
            except KeyError:
                # If validation successful, load newly created workout page:
                print("Workout passed validation and has been created.")
                id = str(validated['workout'].id)
                # Load workout:
                return redirect('/workout/' + id)

    except (KeyError, User.DoesNotExist) as err:
        # If existing session not found:
        messages.info(request, "You must be logged in to view this page.", extra_tags="invalid_session")
        logging.warning("User must be logged in to view 'new_workout'.")
        return redirect("/")

def delete_workout(request, id):
    """
    GET - Delete a workout.

    Args:   
        request: Django HttpRequest object.
        user: User object.
        workout: Workout object.
        data: Dictionary of page data. 

    Returns:
        Django HttpResponse object.
    """

    try:
        # Check for valid session:
        user = User.objects.get(id=request.session["user_id"])
        
        # check if workout is owned by user
        workout = Workout.objects.get(id=id)
        
        if workout.user != user:
            messages.error(request, "You do not have permission to delete this workout.", extra_tags='workout')
            logging.error("User does not have permission to delete workout.")
            return redirect("/workout")
        else:
            # Delete workout:
            workout.delete()

        # Load dashboard:
        return redirect('/workout')


    except (KeyError, User.DoesNotExist) as err:
        # If existing session not found:
        messages.info(request, "You must be logged in to view this page.", extra_tags="invalid_session")
        logging.warning("User must be logged in to view 'delete_workout'.")
        return redirect("/")

def complete_workout(request, id):
    """
    POST - complete a workout

    Args:
        request: Django HttpRequest object.
        user: User object.
        workout: Workout object.
        data: Dictionary of page data.  

    Returns:
        Django HttpResponse object.
    """

    try:
        # Check for valid session:
        user = User.objects.get(id=request.session["user_id"])

        if request.method == "GET":
            logging.debug("GET request to complete workout")
            # If get request, bring back to workout page.
            # Note, for now, GET request for this method not being utilized:
            return redirect("/workout/" + id)

        if request.method == "POST":
            logging.debug("POST request to complete workout")
            # Update Workout.completed field for this instance:
            workout = Workout.objects.get(id=id)
            redirect_url = "/workout/" + id

            try:
                redirect_url = request.POST["redirect"]
            except KeyError as err:
                pass
            
            print("redirect_url: totoot tto ")
            print(redirect_url)

            # check if workout is owned by user
            if workout.user != user:
                messages.error(request, "You do not have permission to complete this workout.", extra_tags='workout')
                logging.error("User does not have permission to complete workout.")
                redirect_url = "/workout"
                return redirect(redirect_url)
            
            is_completed = workout.completed
            if is_completed:
                workout.completed = False
            else:    
                workout.completed = True 
            workout.save()

            # Return to workout:
            return redirect(redirect_url)

    except (KeyError, User.DoesNotExist) as err:
        # If existing session not found:
        messages.info(request, "You must be logged in to view this page.", extra_tags="invalid_session")
        logging.warning("User must be logged in to view 'complete_workout'.")
        return redirect("/")

def share_workout(request, id):
    """
    POST - share a workout

    Args:
        request: Django HttpRequest object.
        user: User object.
        workout: Workout object.

    Returns:
        Django HttpResponse object.
    """

    try:
        # Check for valid session:
        user = User.objects.get(id=request.session["user_id"])

        if request.method == "GET":
            logging.debug("GET request to share workout")
            # If get request, bring back to workout page.
            # Note, for now, GET request for this method not being utilized:
            return redirect("/workout/" + id)

        if request.method == "POST":
            logging.debug("POST request to share workout")
            # Update Workout.is_shared field for this instance:
            workout = Workout.objects.get(id=id)
            redirect_url = "/workout/" + id

            try:
                redirect_url = request.POST["redirect"]
            except KeyError as err:
                pass

            # check if workout is owned by user
            if workout.user != user:
                messages.error(request, "You do not have permission to share this workout.", extra_tags='workout')
                logging.error("User does not have permission to share workout.")
                redirect_url = "/workout"
                return redirect(redirect_url)
            
            is_shared = workout.is_shared
            if is_shared:
                workout.is_shared = False
            else:    
                workout.is_shared = True 
            workout.save()

            # Return to workout:
            return redirect(redirect_url)

    except (KeyError, User.DoesNotExist) as err:
        # If existing session not found:
        messages.info(request, "You must be logged in to view this page.", extra_tags="invalid_session")
        logging.warning("User must be logged in to view 'share_workout'.")
        return redirect("/")

#profile
def profile(request):
    """
    GET - View profile.

    Args:
        request: Django HttpRequest object.
        user: User object.
        workout: QuerySet of recent workouts.
        exercise: List of all exercises.

    Returns:
        Django HttpResponse object.
    """

    try:
        # Check for valid session:
        return profile_online(request, request.session["user_id"])

    except (KeyError, User.DoesNotExist) as err:
        # If existing session not found:
        messages.info(request, "You must be logged in to view this page.", extra_tags="invalid_session")
        logging.warning("User must be logged in to view 'profile'.")
        return redirect("/")
    
def profile_online(request, id):
    """
    GET - View profile.

    Args:
        request: Django HttpRequest object.
        user: User object.
        workout: QuerySet of recent workouts.
        exercise: List of all exercises.

    Returns:
        Django HttpResponse object.
    """

    try:
        # Check for valid session:
        user = User.objects.get(id=request.session["user_id"])
        profile = User.objects.get(id=id)
        workout = Workout.objects.filter(user__id=profile.id, is_shared=True).order_by('-updated_at')[:5]
        exercise = []

        for w in workout:
            exercise.extend(StrengthTrainingExercise.objects.filter(workout__id=w.id))
            exercise.extend(EnduranceTrainingExercise.objects.filter(workout__id=w.id))
            exercise.extend(BalanceExercise.objects.filter(workout__id=w.id))
            exercise.extend(FlexibilityExercise.objects.filter(workout__id=w.id))
        
        # Gather any page data:
        data = {
            'user': user,
            'profile': profile,
            'shared_workouts': workout,
            'shared_exercises': sorted(exercise, key=lambda x: x.updated_at, reverse=True),
        }

        # If get request, load profile page with data:
        return render(request, "workout/profile.html", data)

    except (KeyError, User.DoesNotExist) as err:
        # If existing session not found:
        messages.info(request, "You must be logged in to view this page.", extra_tags="invalid_session")
        logging.warning("User must be logged in to view 'profile'.")
        return redirect("/")

def edit_profile(request):
    
    try:
        # Check for valid session:
        user = User.objects.get(id=request.session["user_id"])
        
        # Gather any page data:
        data = {
            'profile': user,
        }

        # If get request, load profile page with data:
        if request.method == "GET":
            logging.debug("GET request to edit profile")
            # If get request, load edit workout page with data:
            return render(request, "workout/edit_profile.html", data)
        if request.method == "POST":
            logging.debug("POST request to edit profile")
            # check if 
            profile = {}
            
            # Begin validation of updated profile:
            validated = User.objects.update(**profile)
            # If errors, reload register page with errors:
            try:
                if len(validated["errors"]) > 0:
                    logging.error("Profile could not be edited.")
                    print("Profile could not be edited.")
                    # Loop through errors and Generate Django Message for each with custom level and tag:
                    for error in validated["errors"]:
                        messages.error(request, error, extra_tags='edit')
                        logging.error(error)
                    # Reload workout page:
                    return redirect("/profile/edit")
            except KeyError:
                # If validation successful, load newly created workout page:
                print("Edited profile passed validation and has been updated.")
                # Load workout:
                return redirect("/profile/edit")


    except (KeyError, User.DoesNotExist) as err:
        # If existing session not found:
        messages.info(request, "You must be logged in to view this page.", extra_tags="invalid_session")
        logging.warning("User must be logged in to view 'profile'.")
        return redirect("/")
    
#statistics     
def statistics(request):
    """
    GET - View statistics.
    
    Args:
        request: Django HttpRequest object.
        user: User object.
        data_list: List of all exercises.
        paginator: Paginator object.
        data: Dictionary of page data.
        sort_field: Field to sort by.
        sort_direction: Direction to sort by.
    
    Returns:
        Django HttpResponse object.
    """
    try:
        user = User.objects.get(id=request.session["user_id"])
        
        now = timezone.now()
        last_week = now - timedelta(weeks=1)
        last_month = now - timedelta(days=30)

        ste_list = StrengthTrainingExercise.objects.filter(user__id=user.id)
        ete_list = EnduranceTrainingExercise.objects.filter(user__id=user.id)
        be_list = BalanceExercise.objects.filter(user__id=user.id)
        fe_list = FlexibilityExercise.objects.filter(user__id=user.id)

        # Filtering data
        ste_list_week = ste_list.filter(updated_at__gte=last_week)
        ete_list_week = ete_list.filter(updated_at__gte=last_week)
        be_list_week = be_list.filter(updated_at__gte=last_week)
        fe_list_week = fe_list.filter(updated_at__gte=last_week)

        ste_list_month = ste_list.filter(updated_at__gte=last_month)
        ete_list_month = ete_list.filter(updated_at__gte=last_month)
        be_list_month = be_list.filter(updated_at__gte=last_month)
        fe_list_month = fe_list.filter(updated_at__gte=last_month)
        
        sort_field = request.GET.get('sort', 'updated_at')
        sort_direction = request.GET.get('direction', 'desc')

        data_list = list(chain(ste_list, ete_list, be_list, fe_list))

        # Add workout name attribute for sorting
        for item in data_list:
            item.workout_name = item.workout.name if hasattr(item, 'workout') else ''

        def get_sort_key(item):
            if sort_field == 'muscle_group':
                return item.muscle_group.name if hasattr(item, 'muscle_group') and item.muscle_group else ''
            if sort_field == 'workout_name':
                return item.workout_name
            value = getattr(item, sort_field, '')
            if callable(value):
                value = value()
            return value

        sorted_data_list = sorted(data_list, key=get_sort_key, reverse=(sort_direction == 'desc'))
        paginator = Paginator(sorted_data_list, 12)

        page = request.GET.get('page', 1)
        try:
            data = paginator.page(page)
        except PageNotAnInteger:
            data = paginator.page(1)
        except EmptyPage:
            data = paginator.page(paginator.num_pages)

        ste_counts = ste_list.count()
        ete_counts = ete_list.count()
        be_counts = be_list.count()
        fe_counts = fe_list.count()
        
        ste_counts_week = ste_list_week.count()
        ete_counts_week = ete_list_week.count()
        be_counts_week = be_list_week.count()
        fe_counts_week = fe_list_week.count()
        
        ste_counts_month = ste_list_month.count()
        ete_counts_month = ete_list_month.count()
        be_counts_month = be_list_month.count()
        fe_counts_month = fe_list_month.count()

        muscle_groups = MuscleGroup.objects.all()
        muscle_counts = {mg.name: 0 for mg in muscle_groups}
        muscle_counts_week = {mg.name: 0 for mg in muscle_groups}
        muscle_counts_month = {mg.name: 0 for mg in muscle_groups}

        for mg in muscle_groups:
            muscle_counts[mg.name] += ste_list.filter(muscle_group=mg).count()
            muscle_counts[mg.name] += ete_list.filter(muscle_group=mg).count()
            muscle_counts[mg.name] += be_list.filter(muscle_group=mg).count()
            muscle_counts[mg.name] += fe_list.filter(muscle_group=mg).count()

            muscle_counts_week[mg.name] += ste_list_week.filter(muscle_group=mg).count()
            muscle_counts_week[mg.name] += ete_list_week.filter(muscle_group=mg).count()
            muscle_counts_week[mg.name] += be_list_week.filter(muscle_group=mg).count()
            muscle_counts_week[mg.name] += fe_list_week.filter(muscle_group=mg).count()

            muscle_counts_month[mg.name] += ste_list_month.filter(muscle_group=mg).count()
            muscle_counts_month[mg.name] += ete_list_month.filter(muscle_group=mg).count()
            muscle_counts_month[mg.name] += be_list_month.filter(muscle_group=mg).count()
            muscle_counts_month[mg.name] += fe_list_month.filter(muscle_group=mg).count()

        chart_data = {
            'workout_labels': ['Strength', 'Endurance', 'Balance', 'Flexibility'],
            'workout_data': [ste_counts, ete_counts, be_counts, fe_counts],
            'workout_data_week': [ste_counts_week, ete_counts_week, be_counts_week, fe_counts_week],
            'workout_data_month': [ste_counts_month, ete_counts_month, be_counts_month, fe_counts_month],
            'muscle_labels': list(muscle_counts.keys()),
            'muscle_data': list(muscle_counts.values()),
            'muscle_data_week': list(muscle_counts_week.values()),
            'muscle_data_month': list(muscle_counts_month.values())
        }

        data = {
            'user': user,
            'data': data,
            'chart_data': chart_data,
            'sort_field': sort_field,
            'sort_direction': sort_direction,
        }

        return render(request, "workout/statistics.html", data)

    except (KeyError, User.DoesNotExist) as err:
        messages.info(request, "You must be logged in to view this page.", extra_tags="invalid_session")
        logging.warning("User must be logged in to view 'view_all'.")
        return redirect("/")

#other    
def redirect_to_dashboard(request):
    """
    Redirect to dashboard.
    """
    return redirect('/dashboard')