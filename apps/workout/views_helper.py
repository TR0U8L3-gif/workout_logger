from .models import *

def get_exercises_types():
    return [
        StrengthTrainingExercise,
        EnduranceTrainingExercise,
        BalanceExercise,
        FlexibilityExercise,
    ]