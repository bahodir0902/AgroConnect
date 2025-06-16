from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils import timezone
from rest_framework import serializers
from accounts.models import User, RecentActivity
from django.contrib.auth import authenticate
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.models import Group

class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'phone_number', 'date_joined', 'region', 'role']

    def get_role(self, obj):
        groups = obj.groups.all()
        if groups.exists:
            return groups.first().name
        return None


class RegisterSerializer(serializers.ModelSerializer):
    re_password = serializers.CharField(write_only=True, max_length=255)
    password = serializers.CharField(write_only=True, max_length=255)
    role = serializers.CharField(max_length=20)

    class Meta:
        model = User
        fields = ['email', 'phone_number', 'first_name', 'last_name', 'password', 're_password', 'region', 'role']

    def validate(self, attrs):
        if str(attrs['password']) != str(attrs['re_password']):
            raise serializers.ValidationError("Passwords don\'t match")

        email = attrs.get('email', None)
        phone_number = attrs.get('phone_number', None)

        if not email and not phone_number:
            raise serializers.ValidationError("No email and phone number provided.")

        return attrs

    def create(self, validated_data):
        validated_data.pop('re_password')
        password = validated_data.pop('password')
        role = validated_data.pop("role", None)

        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        if role and role == 'Farmers':
            user_group, _ = Group.objects.get_or_create(name='Farmers')
            user.groups.add(user_group)
        if role and role == 'Exporters':
            user_group, _ = Group.objects.get_or_create(name='Exporters')
            user.groups.add(user_group)
        if role and role == 'Analysts':
            user_group, _ = Group.objects.get_or_create(name='Analysts')
            user.groups.add(user_group)

        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'login_field'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['login_field'] = serializers.CharField()
        self.fields.pop('email', None)  # Remove email field if it exists

    def validate(self, attrs):
        login_field = attrs.get('login_field')
        password = attrs.get('password')

        if not login_field or not password:
            raise serializers.ValidationError('Must include login field and password')

        # Determine if login_field is email or phone number
        try:
            validate_email(login_field)
            is_email = True
        except ValidationError:
            is_email = False

        if is_email:
            email_to_authenticate = login_field
        else:
            try:
                user_db = User.objects.get(phone_number=login_field)
                email_to_authenticate = user_db.email
            except User.DoesNotExist:
                raise serializers.ValidationError("Invalid credentials")

        # Authenticate user
        user = authenticate(
            request=self.context.get('request'),
            username=email_to_authenticate,
            password=password
        )

        if not user:
            raise serializers.ValidationError("Invalid credentials")

        if not user.is_active:
            raise serializers.ValidationError("User account is not active")

        # Generate tokens
        refresh = self.get_token(user)

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data
        }


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email doesn't exist.")
        return value


class VerifyPasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6, min_length=4)


class ResetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True, required=True)
    re_new_password = serializers.CharField(write_only=True, required=True)
    uid = serializers.CharField(write_only=True, required=True)
    token = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        password = attrs.get('new_password')
        re_password = attrs.get('re_new_password')

        if password != re_password:
            raise serializers.ValidationError("Passwords don't match.")

        return attrs

class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'phone_number', 'region']

    def update(self, instance: User, validated_data: dict):
        new_email = validated_data.get('email', None)
        if instance.email != new_email:
            validated_data.pop('email', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class RecentActivitySerializer(serializers.ModelSerializer):
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    time_ago = serializers.SerializerMethodField()

    class Meta:
        model = RecentActivity
        fields = [
            'id',
            'action',
            'action_display',
            'model_name',
            'object_name',
            'timestamp',
            'time_ago'
        ]

    def get_time_ago(self, obj):
        """Return human-readable time difference"""
        now = timezone.now()
        diff = now - obj.timestamp

        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return "Just now"