from .models import Profile


# https://stackoverflow.com/questions/29575713/retrieving-profile-picture-from-google-and-facebook-in-python-social-auth
def save_profile(backend, user, response, is_new=False, *args, **kwargs):
    if backend.name == 'google-oauth2':
        if is_new and response.get('picture'):
            Profile.objects.filter(owner=user).update(imageUrl=response['picture'])
