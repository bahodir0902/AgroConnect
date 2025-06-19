from django.contrib import admin
from accounts.models import User, EmailVerification, CodeEmail, CodePassword

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass

@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    pass

@admin.register(CodeEmail)
class CodeEmailAdmin(admin.ModelAdmin):
    pass

@admin.register(CodePassword)
class CodePasswordAdmin(admin.ModelAdmin):
    pass