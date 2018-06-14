from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import authentication
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.serializers import VerifyJSONWebTokenSerializer

# Based on http://getblimp.github.io/django-rest-framework-jwt/#creating-a-new-token-manually

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER


class SessionObtainJSONWebTokenAPIView(APIView):
    """
    Allow session-authenticated users to get a JSON web token
    """
    permission_classes = (IsAuthenticated,)
    authentication_classes = (authentication.SessionAuthentication,)

    def post(self, request, format=None):
        payload = jwt_payload_handler(request.user)
        token = jwt_encode_handler(payload)
        # This returned token is already json encoded, use the verifyJSONWebTokenSerializer to serialize it
        serializer = VerifyJSONWebTokenSerializer(data={'token': token})
        serializer.is_valid()
        return Response(serializer.data)


session_jwt_token = SessionObtainJSONWebTokenAPIView.as_view()
