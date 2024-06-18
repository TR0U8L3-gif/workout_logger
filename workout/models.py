from django.db import models
import re # regex for email validation
import bcrypt # bcrypt for password encryption/decryption
from decimal import * # for decimal number purposes

class UserManager(models.Manager):
    """Additional instance method functions for `User`"""

    def register(self, **kwargs):
        """
        Validates and registers a new user.

        Parameters:
        - `self` - Instance to whom this method belongs.
        - `**kwargs` - Dictionary object of registration values from controller to be validated.

        Validations:
        - Username - Required; No fewer than 2 characters; letters only
        - Email - Required, Valid Format, Not Taken
        - Password - Required; Min 8 char, Matches Password Confirmation
        """

        # Create empty errors list, which we'll return to generate django messages back in our controller:
        errors = []

        #---------------#
        #-- USERNAME: --#
        #---------------#
        # Check if username is less than 2 characters:
        if len(kwargs["username"][0]) < 2:
            errors.append('Username is required and must be at least 2 characters long.')

        # Check if username contains letters, numbers and basic characters only:
        USERNAME_REGEX = re.compile(r'^[a-zA-Z0-9!@#$%^&*()?]*$') # Create regex object
        # Test username against regex object:
        if not USERNAME_REGEX.match(kwargs["username"][0]):
            errors.append('Username must contain letters, numbers and basic characters only.')

        #---------------#
        #-- EXISTING: --#
        #---------------#
        # Check for existing User via username:
        if len(User.objects.filter(username=kwargs["username"][0])) > 0:
            errors.append('Username is already registered to another user.')

        #------------#
        #-- EMAIL: --#
        #------------#
        # Check if email field is empty:
        if len(kwargs["email"][0]) < 5:
            errors.append('Email field must be at least 5 characters.')

        # Else if email is greater than 5 characters:
        else:
            # Check if email is in valid format (using regex):
            EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9\.\+_-]+@[a-zA-Z0-9\._-]+\.[a-zA-Z]*$')
            if not EMAIL_REGEX.match(kwargs["email"][0]):
                errors.append('Email field is not a valid email format.')
            else:
                #---------------#
                #-- EXISTING: --#
                #---------------#
                # Check for existing User via email:
                if len(User.objects.filter(email=kwargs["email"][0])) > 0:
                    errors.append('Email address is already registered to another user.')

        #---------------#
        #-- PASSWORD: --#
        #---------------#
        # Check if password is less than 8 characters:
        if len(kwargs["password"][0]) < 8 or len(kwargs["password_confirmation"][0]) < 8:
            errors.append('Password fields are required and must be at least 8 characters.')
        else:
            # Check if password matches confirmation password:
            if kwargs["password"][0] != kwargs["password_confirmation"][0]:
                errors.append('Password and confirmation must match.')

        # Check for validation errors:
        # If none, hash password, create user and send new user back:
        if len(errors) == 0:
            kwargs["password"][0] = bcrypt.hashpw((kwargs["password"][0]).encode(), bcrypt.gensalt(14))
            # Create new validated User:
            validated_user = {
                "logged_in_user": User(username=kwargs["username"][0], email=kwargs["email"][0], password=kwargs["password"][0]),
            }
            # Save new User:
            validated_user["logged_in_user"].save()
            # Return created User:
            return validated_user
        else:
            # Else, if validation fails, print errors to console and return errors object:
            for error in errors:
                print("Validation Error: ", error)
            # Prepare data for controller:
            errors = {
                "errors": errors,
            }
            return errors

    def login(self, **kwargs):
        """
        Validates and logs in a new user.

        Parameters:
        - `self` - Instance to whom this method belongs.
        - `**kwargs` - Dictionary object of login values from controller.

        Validations:
        - All fields required.
        - Existing User is found.
        - Password matches User's stored password.
        """

        # Create empty errors list:
        errors = []

        #------------------#
        #--- ALL FIELDS ---#
        #------------------#
        # Check that all fields are required:
        if len(kwargs["username"][0]) < 1 or len(kwargs["password"][0]) < 1:
            errors.append('All fields are required.')
        else:
            #------------------#
            #---- EXISTING ----#
            #------------------#
            # Look for existing User to login by username:
            try:
                logged_in_user = User.objects.get(username=kwargs["username"][0])

                #------------------#
                #---- PASSWORD ----#
                #------------------#
                # Compare passwords with bcrypt:
                # Note: We must encode both prior to testing
                try:

                    password = kwargs["password"][0].encode()
                    hashed = logged_in_user.password.encode()

                    if not (bcrypt.checkpw(password, hashed)):
                        print("ERROR: PASSWORD IS INCORRECT")
                        # Note: We send back a general error that does not specify what credential is invalid: this is for security purposes and is admittedly a slight inconvenience to our user, but makes it harder to gather information from the server during brute for attempts
                        errors.append("Username or password is incorrect.")

                except ValueError:
                    # If user's stored password is unable to be used by bcrypt (likely b/c password is not hashed):
                    errors.append('This user is corrupt. Please contact the administrator.')

            # If existing User is not found:
            except User.DoesNotExist:
                print("ERROR: USERNAME IS INVALID")
                # Note: See password validation note above:
                errors.append('Username or password is incorrect.')

        # If no validation errors, return logged in user:
        if len(errors) == 0:
            # Prepare data for controller:
            validated_user = {
                "logged_in_user": logged_in_user,
            }
            # Send back validated logged in User:
            return validated_user
        # Else, if validation fails print errors and return errors to controller:
        else:
            for error in errors:
                print("Validation Error: ", error)
            # Prepare data for controller:
            errors = {
                "errors": errors,
            }
            return errors

    def update(self, **kwargs):
        """
        Validates and updates a user.

        Parameters:
        - `self` - Instance to whom this method belongs.
        - `**kwargs` - Dictionary object of user values from controller to be validated.

        Validations:
        - Username - Required; No fewer than 2 characters; letters only
        - Email - Required, Valid Format, Not Taken
        - Password - Required; Min 8 char, Matches Password Confirmation
        """

        # Create empty errors list, which we'll return to generate django messages back in our controller:
        errors = []

        #---------------#
        #-- USERNAME: --#
        #---------------#
        # Check if username is less than 2 characters:
        if len(kwargs["username"]) < 2:
            errors.append('Username is required and must be at least 2 characters long.')

        # Check if username contains letters, numbers and basic characters only:
        USERNAME_REGEX = re.compile(r'^[a-zA-Z0-9!@#$%^&*()?]*$')
        # Test username against regex object:
        if not USERNAME_REGEX.match(kwargs["username"]):
            errors.append('Username must contain letters, numbers and basic characters only.')
            
        # Check for existing User via username:
        if (kwargs["old_username"] != kwargs["username"]) and len(User.objects.filter(username=kwargs["username"])) > 0:
            errors.append('Username is already registered to another user.')
        
        #------------#
        #-- EMAIL: --#
        #------------#
        # Check if email field is empty:
        if len(kwargs["email"]) < 5:
            errors.append('Email field must be at least 5 characters.')
            
        # Else if email is greater than 5 characters:
        else:
            # Check if email is in valid format (using regex):
            EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9\.\+_-]+@[a-zA-Z0-9\._-]+\.[a-zA-Z]*$')
            if not EMAIL_REGEX.match(kwargs["email"]):
                errors.append('Email field is not a valid email format.')
            else:
                # Check for existing User via email:
                if (kwargs["old_email"] != kwargs["email"]) and len(User.objects.filter(email=kwargs["email"])) > 0:
                    errors.append('Email address is already registered to another user.')
        
        #-----------------#
        #-- PROFILEPIC: --#
        #-----------------#
        
        profile_photo_url = None
        if(len(kwargs["profile_photo_url"]) > 0):
            profile_photo_url = kwargs["profile_photo_url"]
        
        #------------#
        #-- BGPIC: --#
        #------------#
        
        background_photo_url = None
        if(len(kwargs["background_photo_url"]) > 0):
            background_photo_url = kwargs["background_photo_url"]
        
        # Check for validation errors:
        # If none, update user and return new user:
        if len(errors) == 0:
            # Update user:
            user = User.objects.filter(id=kwargs['user_id']).update(username=kwargs['username'], email=kwargs['email'], profile_photo_url=profile_photo_url, background_photo_url=background_photo_url)
            
            # Return updated User:
            updated_user = {
                "updated_user": user
            }
            print(updated_user)
            return updated_user
        else:
            # Else, if validation fails, print errors to console and return errors object:
            for error in errors:
                print("Validation Error: ", error)
            # Prepare data for controller:
            errors = {
                "errors": errors,
            }
            print(errors)
            return errors

    def update_password(self, **kwargs):
        """
        Validates and updates a user's password.

        Parameters:
        - `self` - Instance to whom this method belongs.
        - `**kwargs` - Dictionary object of user values from controller to be validated.

        Validations:
        - Password - Required; Min 8 char, Matches Password Confirmation
        """

        # Create empty errors list, which we'll return to generate django messages back in our controller:
        errors = []

        #---------------#
        #-- PASSWORD: --#
        #---------------#
        # Check if password is less than 8 characters:
        if len(kwargs["new_password"]) < 8 or len(kwargs["repeat_password"]) < 8:
            errors.append('Password fields are required and must be at least 8 characters.')
        else:
            # Check if password matches confirmation password:
            if kwargs["new_password"] != kwargs["repeat_password"]:
                errors.append('Password and confirmation must match.')
        
        # Compare passwords with bcrypt:
        password = kwargs["current_password"].encode()
        hashed = kwargs["old_password"].encode()

        if not (bcrypt.checkpw(password, hashed)):
            print("ERROR: PASSWORD IS INCORRECT")
            # Note: We send back a general error that does not specify what credential is invalid: this is for security purposes and is admittedly a slight inconvenience to our user, but makes it harder to gather information from the server during brute for attempts
            errors.append("Current Password is incorrect.")


        # Check for validation errors:
        # If none, hash password, update user and return new user:
        if len(errors) == 0:
            kwargs["new_password"] = bcrypt.hashpw((kwargs["new_password"]).encode(), bcrypt.gensalt(14))
            # Update user:
            user = User.objects.filter(id=kwargs['user_id']).update(password=kwargs['new_password'])

            # Return updated User:
            updated_user = {
                "updated_user": user
            }
            print(updated_user)
            return updated_user
        else:
            # Else, if validation fails, print errors to console and return errors object:
            for error in errors:
                print("Validation Error: ", error)
            # Prepare data for controller:
            errors = {
                "errors": errors,
            }
            print(errors)
            return errors
class WorkoutManager(models.Manager):
    """Additional instance method functions for `Workout`"""

    def new(self, **kwargs):
        """
        Validates and registers a new workout.

        Parameters:
        - `self` - Instance to whom this method belongs.
        - `**kwargs` - Dictionary object of workout values from controller to be validated.

        Validations:
        - Name - Required; No fewer than 2 characters; letters, basic characters, numbers only
        - Description - Required; letters, basic characters, numbers only
        """

        # Create empty errors list, which we'll return to generate django messages back in our controller:
        errors = []

        #-----------#
        #-- NAME: --#
        #-----------#
        # Check if name is less than 2 characters:
        if len(kwargs["name"]) < 2:
            errors.append('Name is required and must be at least 2 characters long.')

        # Check if name contains letters, numbers and basic characters only:
        '''
        Note: The following regex pattern matches for strings which start or do not start with spaces, whom contain letters, numbers and some basic character sequences, followed by either more spaces or more characters. This prevents empty string submissions.
        '''
        WORKOUT_REGEX = re.compile(r'^\s*[A-Za-z0-9!@#$%^&*\"\':;\/?,<.>()-_=+\]\[~`]+(?:\s+[A-Za-z0-9!@#$%^&*\"\':;\/?,<.>()-_=+\]\[~`]+)*\s*$')

        # Test name against regex object:
        if not WORKOUT_REGEX.match(kwargs["name"]):
            errors.append('Name must contain letters, numbers and basic characters only.')

        #------------------#
        #-- DESCRIPTION: --#
        #------------------#
        # Check if description is less than 2 characters:
        if len(kwargs["description"]) < 2:
            errors.append('Description is required and must be at least 2 characters long.')

        # Check if description contains letters, numbers and basic characters only:
        # Test description against regex object (we'll just use WORKOUT_REGEX again since the pattern has not changed):
        if not WORKOUT_REGEX.match(kwargs["description"]):
            errors.append('Description must contain letters, numbers and basic characters only.')

        # Check for validation errors:
        # If none, create workout and return new workout:
        if len(errors) == 0:
            # Create new validated workout:
            validated_workout = {
                "workout": Workout(name=kwargs["name"], description=kwargs["description"], user=kwargs["user"]),
            }
            # Save new Workout:
            validated_workout["workout"].save()
            # Return created Workout:
            return validated_workout
        else:
            # Else, if validation fails, print errors to console and return errors object:
            for error in errors:
                print("Validation Error: ", error)
            # Prepare data for controller:
            errors = {
                "errors": errors,
            }
            return errors

    def update(self, **kwargs):
        """
        Validates and updates a workout.

        Parameters:
        - `self` - Instance to whom this method belongs.
        - `**kwargs` - Dictionary object of workout values from controller to be validated.

        Validations:
        - Name - Required; No fewer than 2 characters; letters, basic characters, numbers only
        - Description - Required; letters, basic characters, numbers only

        Developer Note:
        - This section utilizes essentially the exact same validations as the `new()` method above (in this same WorkoutManager class). However, in this particular case, we're updating a record rather than creating one. At a later point, it might be good to refactor this section/these validations.
        """

        # Create empty errors list, which we'll return to generate django messages back in our controller:
        errors = []

        #-----------#
        #-- NAME: --#
        #-----------#
        # Check if name is less than 2 characters:
        if len(kwargs["name"]) < 2:
            errors.append('Name is required and must be at least 2 characters long.')

        # Check if name contains letters, numbers and basic characters only:
        '''
        Note: The following regex pattern matches for strings which start or do not start with spaces, whom contain letters, numbers and some basic character sequences, followed by either more spaces or more characters. This prevents empty string submissions.
        '''
        WORKOUT_REGEX = re.compile(r'^\s*[A-Za-z0-9!@#$%^&*\"\':;\/?,<.>()-_=+\]\[~`]+(?:\s+[A-Za-z0-9!@#$%^&*\"\':;\/?,<.>()-_=+\]\[~`]+)*\s*$')

        # Test name against regex object:
        if not WORKOUT_REGEX.match(kwargs["name"]):
            errors.append('Name must contain letters, numbers and basic characters only.')

        #------------------#
        #-- DESCRIPTION: --#
        #------------------#
        # Check if description is less than 2 characters:
        if len(kwargs["description"]) < 2:
            errors.append('Description is required and must be at least 2 characters long.')

        # Check if description contains letters, numbers and basic characters only:
        # Test description against regex object (we'll just use WORKOUT_REGEX again since the pattern has not changed):
        if not WORKOUT_REGEX.match(kwargs["description"]):
            errors.append('Description must contain letters, numbers and basic characters only.')

        # Check for validation errors:
        # If none, create workout and return new workout:
        if len(errors) == 0:
            # Update workout:
            workout = Workout.objects.filter(id=kwargs['workout_id']).update(name=kwargs['name'], description=kwargs["description"])

            # Return updated Workout:
            updated_workout = {
                "updated_workout": workout
            }
            print(updated_workout)
            return updated_workout
        else:
            # Else, if validation fails, print errors to console and return errors object:
            for error in errors:
                print("Validation Error: ", error)
            # Prepare data for controller:
            errors = {
                "errors": errors,
            }
            print(errors)
            return errors

class ExerciseManager(models.Manager):
    """Additional instance method functions for `Exercise`"""

    def new(self, **kwargs):
        """
        Validates and registers a new exercise.

        Parameters:
        - `self` - Instance to whom this method belongs.
        - `**kwargs` - Dictionary object of exercise values from controller to be validated.

        Validations:
        - Name - Required; No fewer than 2 characters; letters, basic characters, numbers only
        - Description - Required; No fewer than 2 characters; letters, basic characters, numbers only
        """

        # Create empty errors list, which we'll return to generate django messages back in our controller:
        errors = []

        #---------------#
        #-- REQUIRED: --#
        #---------------#
        # Check if all required fields are present:
        if not kwargs['name'] or not kwargs['description'] or not kwargs['workout'] or not kwargs['muscle_group']:
            errors.append('All required fields are mandatory.')

        #-----------#
        #-- NAME: --#
        #-----------#
        # Check if name is less than 2 characters:
        if len(kwargs["name"]) < 2:
            errors.append('Name is required and must be at least 2 characters long.')

        #------------------#
        #-- DESCRIPTION: --#
        #------------------#
        # Check if description is less than 2 characters:
        if len(kwargs["description"]) < 2:
            errors.append('Description is required and must be at least 2 characters long.')

        # Check for validation errors:
        # If none, create exercise and return created exercise:
        if len(errors) == 0:
            # Create new validated exercise:
            validated_exercise = {
                "name": kwargs["name"],
                "description": kwargs["description"],
                "workout": kwargs["workout"],
                "muscle_group": kwargs["muscle_group"],
            }
            # Return created Workout:
            return validated_exercise
        else:
            # Else, if validation fails, print errors to console and return errors object:
            for error in errors:
                print("Validation Error: ", error)
            # Prepare data for controller:
            errors = {
                "errors": errors,
            }
            return errors

    class Meta:
        abstract = True

class StrengthTrainingExerciseManager(ExerciseManager):
    """Additional instance method functions for `StrengthTrainingExercise`"""
    
    def new_exercise(self, **kwargs):
        """
        Validates and registers a new strength training exercise.

        Parameters:
        - `self` - Instance to whom this method belongs.
        - `**kwargs` - Dictionary object of strength training exercise values from controller to be validated.

        Validations:
        - Name - Required; No fewer than 2 characters; letters, basic characters, numbers only
        - Description - Required; No fewer than 2 characters; letters, basic characters, numbers only
        - Weight - Required; No fewer than 1; decimal number only
        - Repetitions - Required; No fewer than 1; integer number only
        """
        validated_exercise = super().new(**kwargs)
        
        # Create empty errors list, which we'll return to generate django messages back in our controller:
        errors = []

        
        if "errors" in validated_exercise:
            errors = validated_exercise["errors"]

        #---------------#
        #-- REQUIRED: --#
        #---------------#
        # Check if all required fields are present:
        if not kwargs['weight'] or not kwargs['repetitions']:
            errors.append('All required fields are mandatory.')
        else:

            #------------#
            #-- WEIGHT: --#
            #------------#
            # Check if weight is less than 1:
            if float(kwargs["weight"]) < 1:
                errors.append('Weight is required and must be at least 1.')

            if float(kwargs["weight"]) > 9999:
                errors.append('Weight is required and must be smaller than 9999.')
            #-------------------#
            #-- REPETITIONS: --#
            #-------------------#
            # Check if repetitions is less than 1:
            if float(kwargs["repetitions"]) < 1:
                errors.append('Repetitions is required and must be at least 1.')
            
            if float(kwargs["repetitions"]) > 9999:
                errors.append('Repetitions is required and must be smaller than 9999')
        # Check for validation errors:
        # If none, create strength training exercise and return created strength training exercise:  

        if len(errors) == 0:
            # Create new validated exercise:
            st_exercise = {
                "exercise" : StrengthTrainingExercise(name=validated_exercise["name"], description=validated_exercise["description"], workout=validated_exercise["workout"], muscle_group=validated_exercise["muscle_group"], user=kwargs["user"], weight=kwargs["weight"], repetitions=kwargs["repetitions"]),
            }
            # save 
            st_exercise["exercise"].save()
            # Return created Workout:
            return st_exercise
        else:
            # Else, if validation fails, print errors to console and return errors object:
            for error in errors:
                print("Validation Error: ", error)
            # Prepare data for controller:
            errors = {
                "errors": errors,
            }
            return errors

    def update_exercise(self, **kwargs):
        """
        Validates and registers a updated strength training exercise.

        Parameters:
        - `self` - Instance to whom this method belongs.
        - `**kwargs` - Dictionary object of strength training exercise values from controller to be validated.

        Validations:
        - Name - Required; No fewer than 2 characters; letters, basic characters, numbers only
        - Description - Required; No fewer than 2 characters; letters, basic characters, numbers only
        - Weight - Required; No fewer than 1; decimal number only
        - Repetitions - Required; No fewer than 1; integer number only
        """
        validated_exercise = super().new(**kwargs)
        
        # Create empty errors list, which we'll return to generate django messages back in our controller:
        errors = []

        
        if "errors" in validated_exercise:
            errors = validated_exercise["errors"]

        #---------------#
        #-- REQUIRED: --#
        #---------------#
        # Check if all required fields are present:
        if not kwargs['weight'] or not kwargs['repetitions'] or not kwargs['exercise_id']:
            errors.append('All required fields are mandatory.')
        else:

            #------------#
            #-- WEIGHT: --#
            #------------#
            # Check if weight is less than 1:
            if float(kwargs["weight"]) < 1:
                errors.append('Weight is required and must be at least 1.')

            #-------------------#
            #-- REPETITIONS: --#
            #-------------------#
            # Check if repetitions is less than 1:
            if float(kwargs["repetitions"]) < 1:
                errors.append('Repetitions is required and must be at least 1.')

        # Check for validation errors:
        # If none, create strength training exercise and return created strength training exercise:  

        if len(errors) == 0:
            # Create new validated exercise:
            st_exercise = StrengthTrainingExercise.objects.filter(id=kwargs['exercise_id']).update(name=validated_exercise["name"], description=validated_exercise["description"], workout=validated_exercise["workout"], muscle_group=validated_exercise["muscle_group"], user=kwargs["user"], weight=kwargs["weight"], repetitions=kwargs["repetitions"])

            updated_exercise = {
                "exercise": st_exercise
            }

            # Return created Workout:
            return updated_exercise
        else:
            # Else, if validation fails, print errors to console and return errors object:
            for error in errors:
                print("Validation Error: ", error)
            # Prepare data for controller:
            errors = {
                "errors": errors,
            }
            return errors
        
class EnduranceTrainingExerciseManager(ExerciseManager):
    """Additional instance method functions for `EnduranceTrainingExercise`"""
    
    def new_exercise(self, **kwargs):
        """
        Validates and registers a new endurance training exercise.

        Parameters:
        - `self` - Instance to whom this method belongs.
        - `**kwargs` - Dictionary object of endurance training exercise values from controller to be validated.

        Validations:
        - Name - Required; No fewer than 2 characters; letters, basic characters, numbers only
        - Description - Required; No fewer than 2 characters; letters, basic characters, numbers only
        - Duration - Required; No fewer than 1; integer number only
        - Distance - Required; No fewer than 1; decimal number only
        """
        validated_exercise = super().new(**kwargs)
        
        # Create empty errors list, which we'll return to generate django messages back in our controller:
        errors = []

        if "errors" in validated_exercise:
            errors = validated_exercise["errors"]
            
        #---------------#
        #-- REQUIRED: --#
        #---------------#
        # Check if all required fields are present:
        if not kwargs['duration_minutes'] or not kwargs['distance_km']:
            errors.append('All required fields are mandatory.')
        else:

            #------------------#
            #-- DURATION: --#
            #------------------#
            # Check if duration is less than 1:
            if float(kwargs["duration_minutes"]) < 1:
                errors.append('Duration is required and must be at least 1.')

            #------------------#
            #-- DISTANCE: --#
            #------------------#
            # Check if distance is less than 1:
            if float(kwargs["distance_km"]) < 1:
                errors.append('Distance is required and must be at least 1.')

        # Check for validation errors:
        # If none, create endurance training exercise and return created endurance training exercise:  

        if len(errors) == 0:
            # Create new validated exercise:
            et_exercise = {
                "exercise" : EnduranceTrainingExercise(name=kwargs["name"], description=kwargs["description"], workout=kwargs["workout"], muscle_group=kwargs["muscle_group"], user=kwargs["user"], duration_minutes=kwargs["duration_minutes"], distance_km=kwargs["distance_km"]),
            }
            # save 
            et_exercise["exercise"].save()
            # Return created Workout
            return et_exercise
        else:
            # Else, if validation fails, print errors to console and return errors object:
            for error in errors:
                print("Validation Error: ", error)
            # Prepare data for controller:
            errors = {
                "errors": errors,
            }
            return errors
      
    def update_exercise(self, **kwargs):
        """
        Validates and registers a updated endurance training exercise.

        Parameters:
        - `self` - Instance to whom this method belongs.
        - `**kwargs` - Dictionary object of endurance training exercise values from controller to be validated.

        Validations:
        - Name - Required; No fewer than 2 characters; letters, basic characters, numbers only
        - Description - Required; No fewer than 2 characters; letters, basic characters, numbers only
        - Duration - Required; No fewer than 1; integer number only
        - Distance - Required; No fewer than 1; decimal number only
        """
        validated_exercise = super().new(**kwargs)
        
        # Create empty errors list, which we'll return to generate django messages back in our controller:
        errors = []

        if "errors" in validated_exercise:
            errors = validated_exercise["errors"]
            
        #---------------#
        #-- REQUIRED: --#
        #---------------#
        # Check if all required fields are present:
        if not kwargs['duration_minutes'] or not kwargs['distance_km'] or not kwargs['exercise_id']:
            errors.append('All required fields are mandatory.')
        else:

            #------------------#
            #-- DURATION: --#
            #------------------#
            # Check if duration is less than 1:
            if float(kwargs["duration_minutes"]) < 1:
                errors.append('Duration is required and must be at least 1.')

            #------------------#
            #-- DISTANCE: --#
            #------------------#
            # Check if distance is less than 1:
            if float(kwargs["distance_km"]) < 1:
                errors.append('Distance is required and must be at least 1.')

        # Check for validation errors:
        # If none, create endurance training exercise and return created endurance training exercise:  

        if len(errors) == 0:
            # Create new validated exercise:
            et_exercise = EnduranceTrainingExercise.objects.filter(id=kwargs['exercise_id']).update(name=kwargs["name"], description=kwargs["description"], workout=kwargs["workout"], muscle_group=kwargs["muscle_group"], user=kwargs["user"], duration_minutes=kwargs["duration_minutes"], distance_km=kwargs["distance_km"])
            
            updated_exercise = {
                "exercise": et_exercise
            }
            
            # Return created Workout
            return updated_exercise
        else:
            # Else, if validation fails, print errors to console and return errors object:
            for error in errors:
                print("Validation Error: ", error)
            # Prepare data for controller:
            errors = {
                "errors": errors,
            }
            return errors               
      
class BalanceExerciseManager(ExerciseManager):
    """Additional instance method functions for `BalanceExercise`"""
    
    def new_exercise(self, **kwargs):
        """
        Validates and registers a new balance exercise.

        Parameters:
        - `self` - Instance to whom this method belongs.
        - `**kwargs` - Dictionary object of balance exercise values from controller to be validated.

        Validations:
        - Name - Required; No fewer than 2 characters; letters, basic characters, numbers only
        - Description - Required; No fewer than 2 characters; letters, basic characters, numbers only
        - Difficulty Level - Required; No fewer than 1; letters, basic characters, numbers only
        """
        validated_exercise = super().new(**kwargs)
        
        # Create empty errors list, which we'll return to generate django messages back in our controller:
        errors = []

        if "errors" in validated_exercise:
            errors = validated_exercise["errors"]
            
        #---------------#
        #-- REQUIRED: --#
        #---------------#
        # Check if all required fields are present:
        if not kwargs['difficulty_level']:
            errors.append('All required fields are mandatory.')
        else:
            #------------------#
            #-- DIFFICULTY LEVEL: --#
            #------------------#
            # Check if difficulty level is less than 1:
            if len(kwargs["difficulty_level"]) < 1:
                errors.append('Difficulty level is required and must be at least 1.')

        # Check for validation errors:
        # If none, create balance exercise and return created balance exercise:  

        if len(errors) == 0:
            # Create new validated exercise:
            b_exercise = {
                "exercise" : BalanceExercise(name=kwargs["name"], description=kwargs["description"], workout=kwargs["workout"], muscle_group=kwargs["muscle_group"], user=kwargs["user"], difficulty_level=kwargs["difficulty_level"]),
            }
            # save 
            b_exercise["exercise"].save()
            # Return created Workout
            return b_exercise
        else:
            # Else, if validation fails, print errors to console and return errors object:
            for error in errors:
                print("Validation Error: ", error)
            # Prepare data for controller:
            errors = {
                "errors": errors,
            }
            return errors
        
    def update_exercise(self, **kwargs):
        """
        Validates and registers a updated balance exercise.

        Parameters:
        - `self` - Instance to whom this method belongs.
        - `**kwargs` - Dictionary object of balance exercise values from controller to be validated.

        Validations:
        - Name - Required; No fewer than 2 characters; letters, basic characters, numbers only
        - Description - Required; No fewer than 2 characters; letters, basic characters, numbers only
        - Difficulty Level - Required; No fewer than 1; letters, basic characters, numbers only
        """
        validated_exercise = super().new(**kwargs)
        
        # Create empty errors list, which we'll return to generate django messages back in our controller:
        errors = []

        if "errors" in validated_exercise:
            errors = validated_exercise["errors"]
            
        #---------------#
        #-- REQUIRED: --#
        #---------------#
        # Check if all required fields are present:
        if not kwargs['difficulty_level'] or not kwargs['exercise_id']:
            errors.append('All required fields are mandatory.')
        else:
            #------------------#
            #-- DIFFICULTY LEVEL: --#
            #------------------#
            # Check if difficulty level is less than 1:
            if len(kwargs["difficulty_level"]) < 1:
                errors.append('Difficulty level is required and must be at least 1.')

        # Check for validation errors:
        # If none, create balance exercise and return created balance exercise:  

        if len(errors) == 0:
            # Create new validated exercise:
            b_exercise = BalanceExercise.objects.filter(id=kwargs['exercise_id']).update(name=kwargs["name"], description=kwargs["description"], workout=kwargs["workout"], muscle_group=kwargs["muscle_group"], user=kwargs["user"], difficulty_level=kwargs["difficulty_level"])
            
            updated_exercise = {
                "exercise": b_exercise
            }
            
            # Return created Workout
            return updated_exercise
        else:
            # Else, if validation fails, print errors to console and return errors object:
            for error in errors:
                print("Validation Error: ", error)
            # Prepare data for controller:
            errors = {
                "errors": errors,
            }
            return errors

class FlexibilityExerciseManager(ExerciseManager):
    """Additional instance method functions for `FlexibilityExercise`"""
    
    def new_exercise(self, **kwargs):
        """
        Validates and registers a new flexibility exercise.

        Parameters:
        - `self` - Instance to whom this method belongs.
        - `**kwargs` - Dictionary object of flexibility exercise values from controller to be validated.

        Validations:
        - Name - Required; No fewer than 2 characters; letters, basic characters, numbers only
        - Description - Required; No fewer than 2 characters; letters, basic characters, numbers only
        - Stretch Type - Required; No fewer than 1; letters, basic characters, numbers only
        """
        validated_exercise = super().new(**kwargs)
        
        # Create empty errors list, which we'll return to generate django messages back in our controller:
        errors = []

        if "errors" in validated_exercise:
            errors = validated_exercise["errors"]
            
        #---------------#
        #-- REQUIRED: --#
        #---------------#
        # Check if all required fields are present:
        if not kwargs['stretch_type']:
            errors.append('All required fields are mandatory.')
        else:
            #------------------#
            #-- STRETCH TYPE: --#
            #------------------#
            # Check if stretch type is less than 1:
            if len(kwargs["stretch_type"]) < 1:
                errors.append('Stretch type is required and must be at least 1.')

        # Check for validation errors:
        # If none, create flexibility exercise and return created flexibility exercise:  

        if len(errors) == 0:
            # Create new validated exercise:
            f_exercise = {
                "exercise" : FlexibilityExercise(name=kwargs["name"], description=kwargs["description"], workout=kwargs["workout"], muscle_group=kwargs["muscle_group"], user=kwargs["user"], stretch_type=kwargs["stretch_type"]),
            }
            
            # save 
            f_exercise["exercise"].save()
            # Return created Workout
            return f_exercise
        else:
            # Else, if validation fails, print errors to console and return errors object:
            for error in errors:
                print("Validation Error: ", error)
            # Prepare data for controller:
            errors = {
                "errors": errors,
            }
            return errors
        
    def update_exercise(self, **kwargs):
        """
        Validates and registers a updated flexibility exercise.

        Parameters:
        - `self` - Instance to whom this method belongs.
        - `**kwargs` - Dictionary object of flexibility exercise values from controller to be validated.

        Validations:
        - Name - Required; No fewer than 2 characters; letters, basic characters, numbers only
        - Description - Required; No fewer than 2 characters; letters, basic characters, numbers only
        - Stretch Type - Required; No fewer than 1; letters, basic characters, numbers only
        """
        
        validated_exercise = super().new(**kwargs)
        
        # Create empty errors list, which we'll return to generate django messages back in our controller:
        errors = []
        


        if "errors" in validated_exercise:
            errors = validated_exercise["errors"]
            
        print("git gut")
            
        #---------------#
        #-- REQUIRED: --#
        #---------------#
        # Check if all required fields are present:
        if not kwargs['stretch_type'] or not kwargs['exercise_id']:
            errors.append('All required fields are mandatory.')
        else:
            #------------------#
            #-- STRETCH TYPE: --#
            #------------------#
            # Check if stretch type is less than 1:
            if len(kwargs["stretch_type"]) < 1:
                errors.append('Stretch type is required and must be at least 1.')
        
        # Check for validation errors:
        # If none, create flexibility exercise and return created flexibility exercise:  

        if len(errors) == 0:
            # Create new validated exercise:
            f_exercise = FlexibilityExercise.objects.filter(id=kwargs['exercise_id']).update(name=kwargs["name"], description=kwargs["description"], workout=kwargs["workout"], muscle_group=kwargs["muscle_group"], user=kwargs["user"], stretch_type=kwargs["stretch_type"])
            
            updated_exercise = {
                "exercise": f_exercise
            }
            
            # Return created Workout
            return updated_exercise
        else:
            # Else, if validation fails, print errors to console and return errors object:
            for error in errors:
                print("Validation Error: ", error)
            # Prepare data for controller:
            errors = {
                "errors": errors,
            }
            return errors
     
class User(models.Model):
    """Creates instances of `User`."""
    username = models.CharField(max_length=20)
    email = models.CharField(max_length=50)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    profile_photo_url = models.CharField(max_length=255, blank=True, null=True)
    background_photo_url = models.CharField(max_length=255, blank=True, null=True)
    objects = UserManager() 
    
    def __str__(self):
        return self.username

class Challenge(models.Model):
    """Creates instances of `Challenge`."""
    name = models.CharField(max_length=50)
    level = models.IntegerField(default=1)
    description = models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    def class_name(self):
        return self.__class__.__name__

class Workout(models.Model):
    """Creates instances of `Workout`."""
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=150)
    completed = models.BooleanField(default=False)
    is_shared = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, default=None, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    def class_name(self):
        return self.__class__.__name__
    
class UserChallenge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, null=True, blank=True)
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE, null=True, blank=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    exercise_status = models.JSONField(default=list)


    class Meta:
        unique_together = ['user', 'challenge']
        
    def __str__(self):
        return self.challenge.name
    
    # def save(self, *args, **kwargs):
    #     if not self.pk:
    #         exercises_count = self.workout.exercise_set.count()
    #         self.exercise_status = [False] * exercises_count
    #     super(UserChallenge, self).save(*args, **kwargs)


class MuscleGroup(models.Model):
    """Creates instances of `MuscleGroup`."""
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    def class_name(self):
        return self.__class__.__name__

class Exercise(models.Model):
    """Creates instances of `Exercise`."""
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=150)
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE, related_name='%(class)s', default=None)
    muscle_group = models.ForeignKey(MuscleGroup, on_delete=models.CASCADE, default=None)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = ExerciseManager()
    
    class Meta:
        ordering = ('name', 'muscle_group')
        abstract = True
    
    def __str__(self):
        return self.name
    
    def class_name(self):
        return self.__class__.__name__

class StrengthTrainingExercise(Exercise):
    """Creates instances of `StrengthTrainingExercise`."""
    weight = models.DecimalField(max_digits=6, decimal_places=2)
    repetitions = models.PositiveIntegerField()
    objects = StrengthTrainingExerciseManager()
    def __str__(self):
        return self.name
    
    def data(self):
        return [
            "Weight: " + str(self.weight) + "kg",
            "Repetitions: x" + str(self.repetitions)
        ]
    
    def form_data(self):
        return [
            FormData("weight", "number", "Weight (kg)", self.weight),
            FormData("repetitions", "number", "Repetitions", self.repetitions)
        ]

    def exercise_name(self):
        return "Strength Training"

class EnduranceTrainingExercise(Exercise):
    """Creates instances of `EnduranceTrainingExercise`."""
    duration_minutes = models.PositiveIntegerField()
    distance_km = models.DecimalField(max_digits=6, decimal_places=2)
    objects = EnduranceTrainingExerciseManager()
    
    def __str__(self): 
        return self.name
    
    def data(self):
        return [
            "Duration: " + str(self.duration_minutes) + "m",
            "Distance: " + str(self.distance_km) + "km"
            ]

    def form_data(self):
        return [
            FormData("duration_minutes", "number", "Duration (minutes)", self.duration_minutes),
            FormData("distance_km", "number", "Distance (km)", self.distance_km)
        ]
    def exercise_name(self):
        return "Endurance Training"

class BalanceExercise(Exercise):
    """Creates instances of `BalanceExercise`."""
    difficulty_level = models.CharField(max_length=50)
    objects = BalanceExerciseManager()
    
    def __str__(self):
        return self.name
    
    def data(self):
        return ["Difficulty: " + self.difficulty_level, '']
    
    def form_data(self):
        return [
            FormData("difficulty_level", "text", "Difficulty Level", self.difficulty_level)
        ]

    def exercise_name(self):
        return "Balance"

class FlexibilityExercise(Exercise):
    """Creates instances of `FlexibilityExercise`."""
    stretch_type = models.CharField(max_length=50) 
    objects = FlexibilityExerciseManager()
    
    def __str__(self):
        return self.name
    
    def data(self):
        return ["Stretch type: "+ self.stretch_type, '']
    
    def form_data(self):
        return [
            FormData("stretch_type", "text", "Stretch Type", self.stretch_type)
        ]
    
    def exercise_name(self):
        return "Flexibility"

class FormData: 
    """Creates instances of `FormData`."""
    def __init__(self, name, type, placeholder, value):
        self.name = name
        self.type = type
        self.placeholder = placeholder
        self.value = value