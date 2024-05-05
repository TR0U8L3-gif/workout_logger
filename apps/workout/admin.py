from django.contrib import admin

from .models import User, Workout, MuscleGroup, StrengthTrainingExercise, EnduranceTrainingExercise, BalanceExercise, FlexibilityExercise

admin.site.register(User)
admin.site.register(Workout)
admin.site.register(MuscleGroup)
admin.site.register(FlexibilityExercise)
admin.site.register(StrengthTrainingExercise)
admin.site.register(EnduranceTrainingExercise)
admin.site.register(BalanceExercise)