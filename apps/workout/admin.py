from django.contrib import admin

from .models import User, Workout, MuscleGroup, StrengthTrainingExercise, EnduranceTrainingExercise, BalanceExercise, \
    FlexibilityExercise, Exercise

admin.site.register(User)
admin.site.register(Workout)
admin.site.register(MuscleGroup)



# class AllExercisesAdminView(admin.ModelAdmin):
#     all_exercises_template = "admin/all_exercises_list.html"
#
#     def changelist_view(self, request, extra_context=None):
#         # Query all models
#         data_a = FlexibilityExercise.objects.all()
#         data_b = StrengthTrainingExercise.objects.all()
#         data_c = EnduranceTrainingExercise.objects.all()
#         data_d = BalanceExercise.objects.all()
#
#         # Combine data into a context
#         extra_context = extra_context or {}
#         extra_context['data_a'] = data_a
#         extra_context['data_b'] = data_b
#         extra_context['data_c'] = data_c
#         extra_context['data_d'] = data_d
#
#         return super().changelist_view(request, extra_context=extra_context)
#
#
# admin.site.register(FlexibilityExercise, AllExercisesAdminView)


class FlexibilityExerciseAdmin(admin.ModelAdmin):
    list_display = [field.name for field in FlexibilityExercise._meta.fields]
    list_filter = ["muscle_group__size"]
    search_fields = ["name"]

class StrengthTrainingExerciseAdmin(admin.ModelAdmin):
    list_display = [field.name for field in StrengthTrainingExercise._meta.fields]
    list_filter = ["muscle_group__size"]
    search_fields = ["name"]
class EnduranceTrainingExerciseAdmin(admin.ModelAdmin):
    list_display = [field.name for field in EnduranceTrainingExercise._meta.fields]
    list_filter = ["muscle_group__size"]
    search_fields = ["name"]
class BalanceExerciseAdmin(admin.ModelAdmin):
    list_display = [field.name for field in BalanceExercise._meta.fields]
    list_filter = ["muscle_group__size"]
    search_fields = ["name"]


admin.site.register(FlexibilityExercise, FlexibilityExerciseAdmin)
admin.site.register(StrengthTrainingExercise, StrengthTrainingExerciseAdmin)
admin.site.register(EnduranceTrainingExercise, EnduranceTrainingExerciseAdmin)
admin.site.register(BalanceExercise, BalanceExerciseAdmin)
