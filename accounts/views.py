from django.shortcuts import render , HttpResponse
from .forms import RegistrationForm
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login , logout
from django.contrib.auth.decorators import login_required
from .forms import LoginForm, ProfileForm
from django.contrib.sites.shortcuts import get_current_site 
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth import get_user_model
from django.utils.encoding import force_str



# Create your views here.


def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            current_site = get_current_site(request)
            subject = 'Activate your account'
            message = render_to_string('accounts/activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uidb64': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),             })
            print("=== Email message to send ===")
            print(message) 
            user.email_user(subject, message)
           
            return HttpResponse('Check your email to activate your account.')
    else:
        form = RegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('profile')
            else:
                form.add_error(None, "Invalid email or password")
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


from django.contrib import messages
from django.shortcuts import redirect

def activate_account(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if not user.is_active:
            user.is_active = True
            user.is_email_verified = True  # إذا تستخدم هذا الحقل
            user.save()
            # messages.success(request, 'تم تفعيل حسابك بنجاح! يمكنك الآن تسجيل الدخول.')
        # else:
            # messages.info(request, 'حسابك مفعل مسبقًا.')
        return redirect('login')  # استبدل 'login' باسم رابط تسجيل الدخول في urls.py
    else:
        # messages.error(request, 'رابط التفعيل غير صالح أو انتهت صلاحيته.')
        return redirect('register')  # استبدل 'register' برابط صفحة التسجيل أو صفحة الخطأ

@login_required
def profile_view(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'accounts/profile.html', {'form': form})


def logout_view(req):
    logout(req)
    return redirect("login")
    