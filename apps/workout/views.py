from django.shortcuts import render, redirect
from django.contrib import messages # access django's `messages` module.
from .models import *
from .views_helper import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from itertools import chain

# authentication
def login(request):
    """If GET, load login page, if POST, login user."""

    if request.method == "GET":
        return render(request, "workout/index.html")

    if request.method == "POST":
        # Validate login data:
        validated = User.objects.login(**request.POST)
        try:
            # If errors, reload login page with errors:
            if len(validated["errors"]) > 0:
                print("User could not be logged in.")
                # Loop through errors and Generate Django Message for each with custom level and tag:
                for error in validated["errors"]:
                    messages.error(request, error, extra_tags='login')
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
    """If GET, load registration page; if POST, register user."""

    if request.method == "GET":
        return render(request, "workout/register.html")

    if request.method == "POST":
        # Validate registration data:
        validated = User.objects.register(**request.POST)
        # If errors, reload register page with errors:
        try:
            if len(validated["errors"]) > 0:
                print("User could not be registered.")
                # Loop through errors and Generate Django Message for each with custom level and tag:
                for error in validated["errors"]:
                    messages.error(request, error, extra_tags='registration')
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
    """Logs out current user."""

    try:
        # Deletes session:
        del request.session['user_id']
        # Adds success message:
        messages.success(request, "You have been logged out.", extra_tags='logout')

    except KeyError:
        pass

    # Return to index page:
    return redirect("/")

# dashboard
def dashboard(request):
    """Loads dashboard."""

    try:
        # Check for valid session:
        user = User.objects.get(id=request.session["user_id"])

        # Get recent workouts for logged in user:
        recent_workouts = Workout.objects.filter(user__id=user.id).order_by('-id')[:4]

        # Gather any page data:
        data = {
            'user': user,
            'recent_workouts': recent_workouts,
        }

        # Load dashboard with data:
        return render(request, "workout/dashboard.html", data)

    except (KeyError, User.DoesNotExist) as err:
        # If existing session not found:
        messages.info(request, "You must be logged in to view this page.", extra_tags="invalid_session")
        return redirect("/")

def view_all(request):
    """Loads `View All` Workouts page."""

    try:
        # Check for valid session:
        user = User.objects.get(id=request.session["user_id"])

        workout_list = Workout.objects.filter(user__id=user.id)
        ste_list = StrengthTrainingExercise.objects.filter(user__id=user.id)
        ete_list = EnduranceTrainingExercise.objects.filter(user__id=user.id)
        be_list = BalanceExercise.objects.filter(user__id=user.id)
        fe_list = FlexibilityExercise.objects.filter(user__id=user.id)
        mg_list = MuscleGroup.objects.filter(user__id=user.id)
        
        page = request.GET.get('page', 1)
        data_list = list(chain(workout_list, ste_list,ete_list, be_list, fe_list, mg_list))
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
        return redirect("/")

# muscle group
def muscle_group(request, id):
    """View muscle group."""
    try:
        # Check for valid session:
        user = User.objects.get(id=request.session["user_id"])
        
        muscle_group = MuscleGroup.objects.get(id=id)
        
        # check if muscle group is owned by user
        if muscle_group.user != user:
            messages.error(request, "You do not have permission to view this muscle group.", extra_tags='muscle_group')
            return redirect("/musclegroup")
            
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
        return redirect("/")

def edit_muscle_group(request, id):
    """if POST, update muscle group."""
    try:
        # Check for valid session:
        user = User.objects.get(id=request.session["user_id"])

        if request.method == "POST":
            # Unpack request.POST for validation as we must add a field and cannot modify the request.POST object itself as it's a tuple:
            muscle_group = {
                "muscle_group_id": id,
                "name": request.POST["name"],
                "size": request.POST["size"],
                "user": user
            }
            
            # check if muscle group is owned by user
            if(MuscleGroup.objects.get(id=id).user != user):
                messages.error(request, "You do not have permission to edit this muscle group.", extra_tags='muscle_group')
                return redirect("/musclegroup")

            # Begin validation of a updated muscle_group:
            validated = MuscleGroup.objects.update(**muscle_group)

            # If errors, reload register page with errors:
            try:
                if len(validated["errors"]) > 0:
                    print("Muscle Group could not be edited.")
                    # Loop through errors and Generate Django Message for each with custom level and tag:
                    for error in validated["errors"]:
                        messages.error(request, error, extra_tags='muscle_group')
                    # Reload workout page:
                    return redirect("/musclegroup/" + str(muscle_group['muscle_group_id']))
            except KeyError:
                # If validation successful, load newly created workout page:
                print("Edited workout passed validation and has been updated.")

                # Load workout:
                return redirect("/musclegroup")

    except (KeyError, User.DoesNotExist) as err:
        # If existing session not found:
        messages.info(request, "You must be logged in to view this page.", extra_tags="invalid_session")
        return redirect("/")

def new_muscle_group(request):
    """If GET, load new muscle group; if POST, submit new muscle group."""
    try:
        # Check for valid session:
        user = User.objects.get(id=request.session["user_id"])
        muscle_groups = MuscleGroup.objects.filter(user__id=user.id).order_by('-updated_at')
        # Gather any page data:
        data = {
            'user': user,
            'muscle_groups': muscle_groups,
        }

        if request.method == "GET":
            # If get request, load `add muscle_group` page with data:
            return render(request, "workout/add_muscle_group.html", data)

        if request.method == "POST":
            # Unpack request.POST for validation as we must add a field and cannot modify the request.POST object itself as it's a tuple:
            muscle_group = {
                "name": request.POST["name"],
                "size": request.POST["size"],
                "user": user
            }

            # Begin validation of a new muscle_group:
            validated = MuscleGroup.objects.new(**muscle_group)

            # If errors, reload register page with errors:
            try:
                if len(validated["errors"]) > 0:
                    print("Muscle group could not be created.")
                    # Loop through errors and Generate Django Message for each with custom level and tag:
                    for error in validated["errors"]:
                        messages.error(request, error, extra_tags='muscle_group')
                    # Reload workout page:
                    return redirect("/musclegroup")
            except KeyError:
                # If validation successful, load newly created workout page:
                print("Muscle group passed validation and has been created.")


                id = str(validated['muscle_group'].id)
                
                id = str(validated['muscle_group'].id)
                # Load workout:
                return redirect('/musclegroup')

    except (KeyError, User.DoesNotExist) as err:
        # If existing session not found:
        messages.info(request, "You must be logged in to view this page.", extra_tags="invalid_session")
        return redirect("/")
    
def delete_muscle_group(request, id):
    """Delete a muscle group."""
    try:
        # Check for valid session:
        user = User.objects.get(id=request.session["user_id"])

        # check if muscle group is owned by user
        muscle_group = MuscleGroup.objects.get(id=id)
        if muscle_group.user != user:
            messages.error(request, "You do not have permission to delete this muscle group.", extra_tags='muscle_group')
            return redirect("/musclegroup")
        else:
            # Delete muscle group:
            muscle_group.delete()

        # Load muscle group:
        return redirect('/musclegroup')


    except (KeyError, User.DoesNotExist) as err:
        # If existing session not found:
        messages.info(request, "You must be logged in to view this page.", extra_tags="invalid_session")
        return redirect("/")

# exercise
def exercise(request, id):
    """View exercise."""
    exercise_type = request.GET.get('exercise_type')
    if(exercise_type == None):
        messages.error(request, "You must select an exercise type.", extra_tags='exercise')
        return redirect("/exercise")
    
    try:
        # Check for valid session:
        user = User.objects.get(id=request.session["user_id"])
        exercise_class = get_exercise_by_class_name(exercise_type)
        exercise = exercise_class.objects.get(id=id)
        
        # check if workout is owned by user
        if exercise.user != user:
            messages.error(request, "You do not have permission to view this exercise.", extra_tags='exercise')
            return redirect("/exercise")
            
        # Gather any page data:
        data = {
            'user': user,
            'exercise': exercise,
        }

        # If get request, load exercise page with data:
        return render(request, "workout/exercise.html", data)

    except (KeyError, User.DoesNotExist) as err:
        # If existing session not found:
        messages.info(request, "You must be logged in to view this page.", extra_tags="invalid_session")
        return redirect("/")

def edit_exercise(request, id):
    """If GET, load edit exercise; if POST, update exercise."""

def new_exercise(request):
    """If GET, load new exercise; if POST, submit new exercise."""
    
    exercise_type = request.GET.get('exercise_type')
    if(exercise_type == None):
        exercise_type = StrengthTrainingExercise().class_name
        
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
            'workouts': Workout.objects.filter(user__id=user.id).order_by('-updated_at'), 
            'muscle_groups': MuscleGroup.objects.filter(user = user),

        }
        
        if request.method == "GET":
            # If get request, load `add workout` page with data:
            return render(request, "workout/add_exercise.html", data)

        if request.method == "POST":
            workout_id = request.POST["workout_id"]
            muscle_group_id = request.POST["muscle_group"]
            exercise_type = request.POST["exercise_type"]
            
            
            if(exercise_type == None):
                exercise_type = StrengthTrainingExercise().class_name

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
                    print("Exercise could not be created.")

                    # Loop through errors and Generate Django Message for each with custom level and tag:
                    for error in validated["errors"]:
                        messages.error(request, error, extra_tags='exercise')

                    # Reload workout page:
                    return redirect("/exercise?exercise_type=" + exercise_type + "&current_muscle_group_id=" + muscle_group_id + "&current_workout_id=" + workout_id)
            except KeyError:
                # If validation successful, load newly created workout page:
                print("Exercise passed validation and has been created.")

                # Reload workout:
                return redirect("/exercise?exercise_type=" + exercise_type + "&current_muscle_group_id=" + muscle_group_id + "&current_workout_id=" + workout_id)
    except (KeyError, User.DoesNotExist) as err:
        # If existing session not found:
        messages.info(request, "You must be logged in to view this page.", extra_tags="invalid_session")
        return redirect("/")       
    
def delete_exercise(request, id):
    """Delete a exercise."""
    try:
        # Check for valid session:
        user = User.objects.get(id=request.session["user_id"])
        
        # check if exercise is owned by user
        exercise = Exercise.objects.get(id=id)
        if exercise.user != user:
            messages.error(request, "You do not have permission to delete this exercise.", extra_tags='exercise')
            return redirect("/exercise") 
        else:
            # Delete workout:
            exercise.delete()
        
        # Load dashboard:
        return redirect('/exercise')


    except (KeyError, User.DoesNotExist) as err:
        # If existing session not found:
        messages.info(request, "You must be logged in to view this page.", extra_tags="invalid_session")
        return redirect("/")

# workout 
def workout(request, id):
    """View workout."""
    exercise_type = request.GET.get('exercise_type')
    if(exercise_type == None):
        exercise_type = StrengthTrainingExercise().class_name
    
    try:
        # Check for valid session:
        user = User.objects.get(id=request.session["user_id"])
        workout = Workout.objects.get(id=id)
        
        # check if workout is owned by user
        if workout.user != user:
            messages.error(request, "You do not have permission to view this workout.", extra_tags='workout')
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
            'muscle_groups': MuscleGroup.objects.filter(user = user),
            'exercise_types': get_exercises_types(),
            'current_exercise': exercise_type,
        }

        # If get request, load workout page with data:
        return render(request, "workout/workout.html", data)

    except (KeyError, User.DoesNotExist) as err:
        # If existing session not found:
        messages.info(request, "You must be logged in to view this page.", extra_tags="invalid_session")
        return redirect("/")

def edit_workout(request, id):
    """If GET, load edit workout; if POST, update workout."""

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
            # If get request, load edit workout page with data:
            return render(request, "workout/edit_workout.html", data)

        if request.method == "POST":
            
            # check if workout is owned by user
            if data['workout'].user != user:
                messages.error(request, "You do not have permission to delete this workout.", extra_tags='workout')
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
                    print("Workout could not be edited.")
                    # Loop through errors and Generate Django Message for each with custom level and tag:
                    for error in validated["errors"]:
                        messages.error(request, error, extra_tags='edit')
                    # Reload workout page:
                    return redirect("/workout/" + str(data['workout'].id) + "/edit")
            except KeyError:
                # If validation successful, load newly created workout page:
                print("Edited workout passed validation and has been updated.")

                # Load workout:
                return redirect("/workout/" + str(data['workout'].id))

    except (KeyError, User.DoesNotExist) as err:
        # If existing session not found:
        messages.info(request, "You must be logged in to view this page.", extra_tags="invalid_session")
        return redirect("/")

def new_workout(request):
    """If GET, load new workout; if POST, submit new workout."""

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
            # If get request, load `add workout` page with data:
            return render(request, "workout/add_workout.html", data)

        if request.method == "POST":
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
                    print("Workout could not be created.")
                    # Loop through errors and Generate Django Message for each with custom level and tag:
                    for error in validated["errors"]:
                        messages.error(request, error, extra_tags='workout')
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
        return redirect("/")

def delete_workout(request, id):
    """Delete a workout."""

    try:
        # Check for valid session:
        user = User.objects.get(id=request.session["user_id"])
        
        # check if workout is owned by user
        workout = Workout.objects.get(id=id)
        
        if workout.user != user:
            messages.error(request, "You do not have permission to delete this workout.", extra_tags='workout')
            return redirect("/workout")
        else:
            # Delete workout:
            workout.delete()

        # Load dashboard:
        return redirect('/workout')


    except (KeyError, User.DoesNotExist) as err:
        # If existing session not found:
        messages.info(request, "You must be logged in to view this page.", extra_tags="invalid_session")
        return redirect("/")

def complete_workout(request, id):
    """If POST, complete a workout."""

    try:
        # Check for valid session:
        user = User.objects.get(id=request.session["user_id"])

        if request.method == "GET":
            # If get request, bring back to workout page.
            # Note, for now, GET request for this method not being utilized:
            return redirect("/workout/" + id)

        if request.method == "POST":

            # Update Workout.completed field for this instance:
            workout = Workout.objects.get(id=id)
            
            # check if workout is owned by user
            if workout.user != user:
                messages.error(request, "You do not have permission to complete this workout.", extra_tags='workout')
                return redirect("/workout")
            
            is_completed = workout.completed
            if is_completed:
                workout.completed = False
            else:    
                workout.completed = True 
            workout.save()

            # Return to workout:
            return redirect('/workout/' + id)

    except (KeyError, User.DoesNotExist) as err:
        # If existing session not found:
        messages.info(request, "You must be logged in to view this page.", extra_tags="invalid_session")
        return redirect("/")