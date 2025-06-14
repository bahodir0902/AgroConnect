import requests
from decouple import config
from django.shortcuts import redirect
from rest_framework.response import Response
from rest_framework.views import APIView
from accounts.serializers import *
from accounts.models import User, CodeEmail, CodePassword, EmailVerification
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from django.utils import timezone
from accounts.utils import generate_random_code
from accounts.service import send_email_verification, send_password_verification, send_email_to_verify_email
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        re_password = request.data.get("re_password", None)
        if not re_password:
            return Response({"message": "re_password didn\'t provided"})

        if serializer.is_valid():
            serializer.validated_data.pop("re_password", None)
            email = serializer.validated_data.get('email')
            TemporaryUser.objects.filter(email=email).delete()
            temp_user = TemporaryUser.objects.create(
                **serializer.validated_data,
                re_password=request.data.get("re_password")
            )

            code = generate_random_code()
            CodeEmail.objects.update_or_create(
                email=email,
                code=code
            )
            send_email_verification(email, serializer.validated_data.get('first_name'), code)
            return Response({
                "message": "Verification code sent to your email. Please verify to complete registration.",
                "email": email
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyRegistration(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        pending_user_data = TemporaryUser.objects.filter(email=email).values().first()
        code = request.data.get('code', None)
        if not code:
            return Response(
                {"message": "Verification code is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not pending_user_data:
            return Response(
                {"message": "No pending registration found. Please start registration again."},
                status=status.HTTP_400_BAD_REQUEST
            )

        code_db = CodeEmail.objects.filter(email=email).first()
        if not code_db:
            return Response(
                {"message": "Verification code not found. Please request a new code."},
                status=status.HTTP_404_NOT_FOUND
            )

        if code_db.expire_date < timezone.now():
            return Response(
                {"message": "Verification code has expired. Please request a new code."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if str(code_db.code) != str(code):
            return Response(
                {"message": "Invalid verification code."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            serializer = RegisterSerializer(data=pending_user_data)
            if serializer.is_valid():
                user = serializer.save()

                # Clean up
                code_db.delete()

                refresh = RefreshToken.for_user(user)
                return Response({
                    "message": "Registration completed successfully",
                    "user": UserSerializer(user).data,
                    "tokens": {
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                    }
                }, status=status.HTTP_201_CREATED)
            else:
                return Response(
                    {"message": "Error creating user", "errors": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )

        except Exception as e:
            return Response(
                {"message": f"Error creating user: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    # @method_decorator(ratelimit(key='user_or_ip', rate='6/m', block=True))
    # @method_decorator(transaction.atomic)
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.get(email=email)  # We know it exists from validation

            code = generate_random_code()

            CodePassword.objects.update_or_create(
                user=user,
                code=code
            )

            send_password_verification(email, user.first_name, code)

            return Response({
                "message": "Password reset code has been sent to your email.",
                "email": email
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyPasswordResetView(APIView):
    permission_classes = [AllowAny]

    # @method_decorator(ratelimit(key='user_or_ip', rate='6/m', block=True))
    def post(self, request):
        serializer = VerifyPasswordResetSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        code = serializer.validated_data.get('code')
        email = serializer.validated_data.get('email', None)

        if not email:
            return Response({
                "message": "Email session not found. Please request password reset again."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({
                "message": "User not found."
            }, status=status.HTTP_404_NOT_FOUND)

        try:
            code_db = CodePassword.objects.get(user=user)
        except CodePassword.DoesNotExist:
            return Response({
                "message": "Invalid verification code. Please try again."
            }, status=status.HTTP_400_BAD_REQUEST)

        if code_db.expire_date < timezone.now():
            return Response({
                "message": "Your code has expired. Request a new one."
            }, status=status.HTTP_400_BAD_REQUEST)

        if str(code_db.code) != str(code):
            return Response({
                "message": "Incorrect code. Please enter the correct code."
            }, status=status.HTTP_400_BAD_REQUEST)

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        return Response({
            "message": "Code verified successfully. You can now reset your password.",
            "uid": uid,
            "token": token
        }, status=status.HTTP_200_OK)


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    # @method_decorator(ratelimit(key='user_or_ip', rate='6/m', block=True))
    # @method_decorator(transaction.atomic)
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        uidb64 = serializer.validated_data.get('uid')
        token = serializer.validated_data.get('token')
        new_password = serializer.validated_data.get('new_password')

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({"message": "Invalid user."}, status=status.HTTP_400_BAD_REQUEST)

        if not default_token_generator.check_token(user, token):
            return Response({"message": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        CodePassword.objects.filter(user=user).delete()

        return Response({
            "message": "Password has been reset successfully."
        }, status=status.HTTP_200_OK)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        return Response({
            "message": "Login successful",
            "tokens": {
                "refresh": serializer.validated_data['refresh'],
                "access": serializer.validated_data['access'],
            },
            "user": serializer.validated_data['user'],

        }, status=status.HTTP_200_OK)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        print(request.data)
        try:
            refresh_token = request.data.get("refresh_token")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
                return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Refresh token is required'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        print(serializer.data)
        return Response(serializer.data)

    def put(self, request):
        serializer = UpdateUserSerializer(instance=request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class RequestEmailChange(APIView):
    def post(self, request):
        new_email = request.data.get("new_email")
        user_id = request.data.get("user_id")
        user = User.objects.filter(pk=user_id).first()
        if not user:
            return Response({"message": f"User with {user_id} id not found"})
        if not new_email:
            return Response({"message": f"New email didn\'t provided."})
        if User.objects.filter(email=new_email).exists():
            return Response({"message": f"User with {new_email} email already exists."})

        code = generate_random_code()
        send_email_to_verify_email(new_email, user.first_name, code)

        EmailVerification.objects.filter(user=user).delete()
        EmailVerification.objects.filter(new_email=new_email).delete()
        EmailVerification.objects.update_or_create(
            user=user,
            new_email=new_email,
            code=code
        )
        return Response({"message": f"Successfully sent verification code to {new_email}"})


class ConfirmEmailChange(APIView):
    def post(self, request):
        new_email = request.data.get("new_email")
        code = request.data.get("code")
        code_db = EmailVerification.objects.filter(new_email=new_email).first()
        user = User.objects.filter(pk=code_db.user.pk).first()

        if not code or not new_email:
            return Response({"message": "new_email or code didn\'t provided"})

        if not user:
            return Response({"message": "user not found in database"})

        if code_db.expire_date < timezone.now():
            return Response({
                "message": "Your code has expired. Request a new one."
            }, status=status.HTTP_400_BAD_REQUEST)

        if str(code_db.code) != str(code):
            return Response({
                "message": "Incorrect code. Please enter the correct code."
            }, status=status.HTTP_400_BAD_REQUEST)

        user.email = new_email
        user.save()
        return Response({"message": "Successfully changed to new email"})


class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            response.data['message'] = 'Token refreshed successfully'
        return response


class DeleteAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user = request.user
        user.delete()
        return Response({"message": "Account deletion was successful."})


class GoogleLoginView(APIView):
    permission_classes = [AllowAny]

    # @method_decorator(ratelimit(key='user_or_ip', rate='10/m', block=True))
    def get(self, request):
        auth_url = (
            f"{config("GOOGLE_AUTH_URL")}"
            f"?client_id={config("GOOGLE_CLIENT_ID")}"
            f"&redirect_uri={config("GOOGLE_REDIRECT_URI")}"
            f"&response_type=code"
            f"&scope=openid email profile"
        )

        return redirect(auth_url)


class GoogleCallBackView(APIView):
    permission_classes = [AllowAny]

    # @method_decorator(transaction.atomic)
    def get(self, request):
        code = request.GET.get('code')
        token_data = {
            "code": code,
            "client_id": config("GOOGLE_CLIENT_ID"),
            "client_secret": config("GOOGLE_CLIENT_SECRET"),
            "redirect_uri": config("GOOGLE_REDIRECT_URI"),
            "grant_type": "authorization_code",
        }

        token_response = requests.post(config("GOOGLE_TOKEN_URL"), data=token_data)
        token_json = token_response.json()
        access_token = token_json.get("access_token")

        user_info_response = requests.get(
            config("GOOGLE_USER_INFO_URL"),
            headers={"Authorization": f"Bearer {access_token}"}
        )

        user_info = user_info_response.json()

        google_user_id = user_info.get('sub')
        first_name = user_info.get('name', None)
        last_name = user_info.get('given_name', None)
        email = user_info.get('email')

        if User.objects.filter(email=email, google_id__isnull=True).exists():
            return Response({"You already in the system. Please login in a standard way."})

        user, created = User.objects.get_or_create(
            google_id=google_user_id,
            defaults={
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
            }
        )

        if created:
            user.set_unusable_password()
            user.save()
            return Response({"message": "Registration completed successfully", "email": email},
                            status=status.HTTP_201_CREATED)

        refresh = RefreshToken.for_user(user)
        return Response({
            "message": "Login completed successfully",
            "user": UserSerializer(user).data,
            "tokens": {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)
