from django.shortcuts import render

# Create your views here.
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponseRedirect
from EvtronCharging import settings
from .models import Usermaster_table
from .models import Useractivity_table
from django.contrib.auth.hashers import make_password
from django.utils.encoding import force_bytes, force_str
from .tokens import generate_token
from host import views
from django.core.mail import send_mail, EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from .forms import Myform
from django.contrib.auth.hashers import check_password
import datetime

# Create your views here.


def signup(request):
    if request.method == 'POST':
       
        username = request.POST.get('username')
        email = request.POST.get('email')
        pass1 = request.POST.get('pass1')
        pass2 = request.POST.get('pass2')

        myuser = Usermaster_table(username=username, email=email,
                          pass1=pass1)

        # validation

        if myuser.usernameisExist():
            messages.error(request, "Username Already Registered!!")
            return HttpResponseRedirect('#')

        if myuser.mailisExist():
            messages.error(request, "Email Already Registered!!")
            return HttpResponseRedirect('#')

        if pass1 != pass2:
            messages.error(request, "Passwords didn't matched!!")
            return HttpResponseRedirect('#')

        else:
            myuser.pass1 = make_password(myuser.pass1)
            myuser.verified = False
            myuser.status = "inactive"
            myuser.register()

            messages.success(
                request, "Your Account has been created succesfully!! Please check your email to confirm your email address.")

            # Welcome Email
            subject = "Welcome to our website!!"

            message = "Hello " + str(myuser.username) + "!! \n" + \
                      "Welcome to our website! \nThank you for visiting us.\n \n\nThanking You\n-Team SASTRA"

            from_email = settings.EMAIL_HOST_USER
            to_list = [myuser.email]
            send_mail(subject, message, from_email,
                      to_list, fail_silently=True)

            # email confirmation

            current_site = get_current_site(request)
            email_subject = "confirm your mail @ AZ django login!!"
            message2 = render_to_string('login/email_confirmation.html', {
                'name': myuser.username,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(myuser.pk)),
                'token': generate_token.make_token(myuser)
            })

            email = EmailMessage(
                email_subject,
                message2,
                settings.EMAIL_HOST_USER, [myuser.email],
            )
            email.fail_silently = True
            email.send()

            return render (request, 'login/check.html')
    else:
        return render(request, 'login/host_signup.html')

# account activation


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = Usermaster_table.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, user.DoesNotExist):
        user = None

    if user is not None and generate_token.check_token(user, token):
        user.verified = True
        user.status = "Active"
        user.save()
        views.signin(request)
        return redirect('host_signin')

    else:
        return render(request, 'login/activation_failed.html')



def signin(request):

    global customer

    cap = Myform(request.POST)

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        customer = Usermaster_table.get_customer_by_email(email)
        #customer2 = Useractivity_table.get_loginlogout_by_email(email)
        print(customer.email)
       
        if customer:

        
             if customer.verified == 'True':  # verified email
                flag = check_password(password, customer.pass1)

                if flag:
                    if cap.is_valid():
                        customer2 = Useractivity_table(login_time = datetime.datetime.now(), logout_time = None)
                        
                        customer2.email = customer.email
                        customer2.save()
                        return render(request, 'login/check.html', {'uname': customer.fname})
                    else:
                        messages.error(request, "Invalid Captcha")
                        return HttpResponseRedirect('#')
                else:
                    messages.error(request, "Invalid email or Password!!")
                    return HttpResponseRedirect('#')
             else:
                messages.error(
                    request, "User not verified!! Please check your mail and verify!")
                return HttpResponseRedirect('#')
        else:
            messages.error(request, "Invalid email!")
            return HttpResponseRedirect('#')
    else:
        return render(request, 'login/host_signin.html', {"cap": cap})
        