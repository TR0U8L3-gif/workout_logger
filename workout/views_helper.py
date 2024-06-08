from .models import *

def get_exercises_types():
    return [
        StrengthTrainingExercise,
        EnduranceTrainingExercise,
        BalanceExercise,
        FlexibilityExercise,
    ]
    
def get_exercise_by_class_name(class_name):
    for exercise_type in get_exercises_types():
        if exercise_type.__name__ == class_name:
            return exercise_type
    return None

# todo: fixx
def get_view_by_class_name(class_name):
    for exercise_type in get_exercises_types():
        if exercise_type.__name__ == class_name:
            return exercise_type.__name__.lower()
    return None