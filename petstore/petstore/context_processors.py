from .models import Profile


def profile_status(request):
    if request.user.is_authenticated:
        return {'profile_exists':Profile.objects.filter(user = request.user).exists()}
    return {'profile_exists': False}

