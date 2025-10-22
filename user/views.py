from django.shortcuts import render

# Create your views here.
from django.utils import timezone
from datetime import timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .serializers import UserSerializer
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from .serializers import KYCVerificationSerializer
from drf_spectacular.utils import extend_schema, OpenApiExample
from rest_framework import generics
from .models import User, EmailOTP
from .utils import create_and_send_email_otp
import random
import hashlib
from django.core.mail import send_mail


# Create your views here.
@extend_schema(
    tags=["User Authentication"],
    summary="To register new users and send email OTP for verification",
    description=(
        "This endpoint registers a new user and automatically sends a 6-digit OTP "
        "to the user's email for verification. The OTP is valid for 15 minutes."
    ),

    request=dict,
    responses={
        200: OpenApiExample(
            "Successful Registration",
            value={
                "message": "user registration successful. OTP sent to email for verification.",
                "email": "example@gmail.com"
            },
        ),
        400: OpenApiExample(
            "Validation Error",
            value={"message": {"email": ["This field must be unique."]}}
        ),
    },
    examples= [
        OpenApiExample(
            name="Register User",
            description="Example of request body for creating a new user.",
            value={
                "first_name": "string",
                "last_name": "string",
                "email": "example@gmail.com",
                "password": "string",
                "confirm_password": "string",
                "phone": "1234567890",
                "role": "string",
            },
            request_only=True,  # Show in request body
        ),
        OpenApiExample(
            name="Example Response with OTP notice",
            description="The response confirms OTP has been sent to email.",
            value={
                "message": "User registration successful. OTP sent to email for verification.",
                "email": "jane@example.com"
            },
            response_only=True,
        ),
    ]
)
class RegisterUsers(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Generate and send email OTP for verification
            otp = str(random.randint(100000, 999999)) # Generate a 6-digit OTP
            otp_hash = hashlib.sha256(otp.encode()).hexdigest()
            expiry = timezone.now() + timedelta(minutes=15) # OTP valid for 15 minutes
            EmailOTP.objects.create(
                user=user,
                code_hash=otp_hash,
                expires_at=expiry
            )   
            # Here, you would send the OTP to the user's email address

            subject = "Verify Your Email - FinTech Digital Bank"
            message = (
                f"Hello {user.last_name},\n\n"
                f"Your verification code is: {otp}\n\n"
                f"This code will expire in 15 minutes.\n\n"
                f"Thank you for registering!"
            )

            send_mail(subject, message, None, [user.email])
            return Response({"message": "user registration successful. OTP sent to email for verification.", "email": user.email}, status=status.HTTP_201_CREATED)
        return Response({"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
    tags=["User Authentication"],
    summary="To Login user",
    description="Authenticate users using their email and password to obtain JWT tokens for session management.",
    request=OpenApiExample(
        name="Login User Example Request",
        value={
            "email": "user@example.com",
            "password": "string"
        }
    ),
    responses={
        200: OpenApiExample(
            name="Login Successful",
            value={
                "message": "Login successful.",
                "tokens": {
                    "access": "jwt_access_token",
                    "refresh": "jwt_refresh_token"
                }
            },
        ),
        400: OpenApiExample(
            name="Missing Credentials",
            value={"error": "Email and password are required."}
        ),
        401: OpenApiExample(
            name="Invalid Credentials",
            value={"error": "Invalid credentials, please try again."}
        ),
        },
    examples= [
        OpenApiExample(
            name="Login User",
            value={
                "email": "example@gmail.com",
                "password": "string"
            }
        )
    ]
)

class LoginUsers(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response({"error": "Email and password are required."},status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, email=email, password=password)


        if user is not None:
            access = AccessToken.for_user(user)
            refresh = RefreshToken.for_user(user)

            return Response({"mesaage": "Login successful.", "user": UserSerializer(user).data, "tokens": {"access": str(access), "refresh": str(refresh)}})
        else:
            return Response({"error": "invalid credentials, please try again"}, status=status.HTTP_401_UNAUTHORIZED) 

@extend_schema(
    tags=["User Authentication"],
    summary="Upload and verify user KYC",
    request=KYCVerificationSerializer,
    responses={
        200: dict,
        400: dict
    },
    examples=[
        OpenApiExample(
            name="Verify KYC",
            value={
                "KYC_status": True
            }
        )
    ]
)

class KYCUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        user = request.user
        if user.KYC_status:
            return Response({"message": "KYC already verified"}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = KYCVerificationSerializer(user, data={"KYC_staus": True}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "KYC verification successful.", "KYC_status": True}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
    tags=["User Authentication"],
    summary="Get the currently logged-in user's profile",
    description="Returns the data of the authenticated user using the provided JWT token.",
    responses={200: UserSerializer},
)
class CurrentUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
@extend_schema(
    tags=["User Authentication"],
    summary="Admin-only: View all registered users",
    description="Returns a list of all users in the system. Only accessible by admins.",
    responses={200: UserSerializer(many=True)},
)
class AdminUserListView(generics.ListAPIView):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]


@extend_schema(
    tags=["Email Verification"],
    summary="Verify user's email using OTP",
    description="Verifies the user's email by validating the 6-digit OTP code sent to their email address.",
    request={
        "application/json": {
            "example": {
                "email": "user@example.com",
                "OTP": "123456"
            }
        }
    },

    responses={
        200: dict,
        400:dict,
        404: dict
    },
    examples=[
        OpenApiExample(
            name="Verification Successful",
            description="Response when OTP is correct and valid.",
            value={"message": "Email verified successfully."},
            response_only=True
        ),
        OpenApiExample(
            name="Invalid OTP",
            description="Response when OTP is expired or incorrect.",
            value={"error": "Invalid or expired OTP."},
            response_only=True
        ),
        OpenApiExample(
            name="OTP Not Found",
            description="Response when no OTP record exists for that email.",
            value={"error": "No OTP found or already used."},
            response_only=True
        ),
    ]
)
class VerifyEmailOTPView(APIView):
    permission_classes = [permissions.AllowAny]  # allow if used in activation flow
    def post(self, request):
        email = request.data.get("email")
        OTP = request.data.get("OTP")
        if not email or not OTP:
            return Response({"error": "Email and OTP are required"}, status=status.HTTP_400_BAD_REQUEST)
        # find latest un-used otp for this user
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        otp_instance = EmailOTP.objects.filter(user=user, used=False).order_by("-created_at").first()

        if not otp_instance:
            return Response({"error": "No OTP found or already used."}, status=status.HTTP_404_NOT_FOUND)

        if otp_instance.verify(OTP):
            otp_instance.mark_used()
            user.email_verified = True 
            user.save()
            return Response({"message": "Email verified successfully."}, status=status.HTTP_200_OK)

        return Response({"error": "Invalid or expired OTP."}, status=status.HTTP_400_BAD_REQUEST)
    
@extend_schema(
    tags=["Email Verification"],
    summary="Resend email verification OTP",
    description="Resends a new 6-digit OTP code to the user's email. This endpoint can be used if the user didn’t receive or the previous OTP expired. Limited to 1 request per minute.",
    request={
        "application/json": {
            "example": {
                "email": "user@example.com",
                "OTP": "123456"
            }
        }
    },
    responses={
        200: dict,
        400: dict,
        404: dict,
        429: dict
    },
    examples=[
        OpenApiExample(
            name="Resend OTP Example Request",
            description="Provide the registered email address.",
            value={"email": "user@example.com"},
            request_only=True
        ),
        OpenApiExample(
            name="OTP Resent",
            description="A new OTP has been sent to user's email.",
            value={"message": "A new OTP has been sent to your email."},
            response_only=True
        ),
        OpenApiExample(
            name="Rate Limit Reached",
            description="User tried to request OTP too soon.",
            value={"error": "Please wait a minute before requesting another OTP."},
            response_only=True
        ),
        OpenApiExample(
            name="User Not Found",
            description="The email address does not exist in the database.",
            value={"error": "User not found."},
            response_only=True
        ),
    ]
)   

class ResendEmailOTPView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")

        if not email:
            return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        # Check for a recent OTP (to avoid abuse)
        last_otp = EmailOTP.objects.filter(user=user).order_by("-created_at").first()
        if last_otp and timezone.now() - last_otp.created_at < timedelta(minutes=1):
            return Response(
                {"error": "Please wait a minute before requesting another OTP."},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        # Generate a new OTP
        otp = str(random.randint(100000, 999999))
        otp_hash = hashlib.sha256(otp.encode()).hexdigest()
        expiry = timezone.now() + timedelta(minutes=15) # OTP valid for 15 minutes

        EmailOTP.objects.create(
            user=user,
            code_hash=otp_hash,
            expires_at=expiry
        )

        # Send the email again
        subject = "Your New Email Verification Code"
        message = (
            f"Hello {user.last_name},\n\n"
            f"Here's your new verification code: {otp}\n\n"
            f"This code expires in 15 minutes.\n\n"
            f"If you didn't request this, please ignore this message."
        )

        send_mail(subject, message, None, [user.email])

        return Response(
            {"message": "A new OTP has been sent to your email."},
            status=status.HTTP_200_OK
        )