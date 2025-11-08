from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Password
from cryptography.fernet import Fernet
from django.conf import settings
from .check import state_of_password

fernet = Fernet(settings.FERNET_KEY)

# The home page view
def index(request):
    return render(request, 'webapp/index.html')

# Signup view, checks user input and creates a new user
def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        
        # Check for valid username
        if len(username) <= 2:
            context = {
                'message': 'Please enter a real username'
            }
            return render(request, 'webapp/signup.html', context=context)

        # Check if passwords match
        if password != password2:
            context = {
                'message': 'Passwords do not match'
            }
            return render(request, 'webapp/signup.html', context=context)

        # Check if the username or email is already taken
        if User.objects.filter(username=username).exists():
            context = {
                'message': 'Username is used,',
                'message2': ' Please change your username',
            }
            return render(request, 'webapp/signup.html', context=context)

        if User.objects.filter(email=email).exists():
            context = {
                'message': 'Email is used'
            }
            return render(request, 'webapp/signup.html', context=context)

        # Check for strong password
        if state_of_password(password) in ['Weak', 'Very weak']:
            context = {
                'message': 'Please enter a strong password containing',
                'message2': 'letters, numbers and symbols',
            }
            return render(request, 'webapp/signup.html', context=context)

        # Create user and log them in
        user = User.objects.create_user(username=username, email=email, password=password)
        return redirect('login')

    return render(request, 'webapp/signup.html')

# Login view, checks if user credentials are correct and logs them in
def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
    
        # Authenticate user
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            auth_login(request, user)  # Log the user in
            return redirect('dashboard')  # Redirect to the dashboard
        else:
            context = {
                'message': 'Incorrect username or password'
            }
            return render(request, 'webapp/login.html', context=context)

    return render(request, 'webapp/login.html')

# Logout view, logs the user out and redirects to login page
def logout_view(request):
    logout(request)
    return redirect('login')  # Redirect to the login page

# Dashboard view, shows the user's passwords
@login_required
def dashboard(request):
    passwords = Password.objects.filter(created_by=request.user)  # Get the passwords created by the logged-in user
    # Create a list of decrypted passwords
    decrypted_passwords = []
    for password in passwords:
        try:
            password_in_bytes = password.password.encode()
            decrypted_password_in_bytes = fernet.decrypt(password_in_bytes)
            decrypted_password_in_str = decrypted_password_in_bytes.decode()  # Decrypt each password
            decrypted_passwords.append(decrypted_password_in_str)
        except Exception as e:
            decrypted_passwords.append("Error decrypting password")

    passwords_with_decrypted = zip(passwords, decrypted_passwords)

    return render(request, 'webapp/dashboard.html', {'passwords_with_decrypted': passwords_with_decrypted})

# Add a new password view, creates a new password entry in the database
@login_required
def addnew(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        web_or_app = request.POST.get('web_or_app')
        note = request.POST.get('note')
        state = state_of_password(password)  # Check password strength
        created_by = request.user

        encrypted_data = fernet.encrypt(password.encode())
        encrypted_data = encrypted_data.decode()

        form = Password(username=username, password=encrypted_data,
                        email=email, web_or_app=web_or_app,
                        note=note, created_by=created_by, state=state)
        form.save()  # Save the new password to the database
        return redirect('dashboard')  # Redirect to the dashboard

    return render(request, 'webapp/addnew.html')

# View for showing a specific password details
@login_required
def view_password(request, id):
    password = get_object_or_404(Password, created_by=request.user, id=id)  # Get the password by ID
    # Create a list of decrypted passwords
    decrypted_passwords = ''
    try:
        password_in_bytes = password.password.encode()
        decrypted_password_in_bytes = fernet.decrypt(password_in_bytes)
        decrypted_password_in_str = decrypted_password_in_bytes.decode()  # Decrypt each password
        decrypted_passwords = decrypted_password_in_str
    except Exception as e:
        decrypted_passwords = 'Error decrypting password'

    return render(request, 'webapp/view.html', {'password': password, 'decrypted_passwords': decrypted_passwords})

# View for deleting a password after user confirmation
@login_required
def delete_password(request, id):
    password = get_object_or_404(Password, created_by=request.user, id=id)

    if request.method == 'POST':
        password.delete()  # Delete the password from the database
        return redirect('dashboard')  # Redirect to the dashboard
    
    return render(request, 'webapp/confirm_delete.html', {'password': password})

# Search view, allows users to search for passwords based on username or password
@login_required
def search(request):
    query = request.GET.get('query')
    passwords_result = Password.objects.filter(created_by=request.user)  # Get user's passwords
    if query:
        # Apply filters to the search query
        passwords_result = passwords_result.filter(
            Q(username__icontains=query) |
            Q(password__icontains=query)
        )
        # Create a list of decrypted passwords
        decrypted_passwords = []
        for password in passwords_result:
            try:
                password_in_bytes = password.password.encode()
                decrypted_password_in_bytes = fernet.decrypt(password_in_bytes)
                decrypted_password_in_str = decrypted_password_in_bytes.decode()  # Decrypt each password
                decrypted_passwords.append(decrypted_password_in_str)
            except Exception as e:
                decrypted_passwords.append("Error decrypting password")

        passwords_with_decrypted = zip(passwords_result, decrypted_passwords)

        if not passwords_result:
            return render(request, 'webapp/search.html', {'passwords_result': passwords_result, 'query': query})

    return render(request, 'webapp/search.html', {'passwords_with_decrypted': passwords_with_decrypted, 'query': query})

# Update an existing password view, allows the user to edit the details of a password
@login_required
def update(request, id):
    password = get_object_or_404(Password, created_by=request.user, id=id)
    # Create a list of decrypted passwords
    decrypted_passwords = ''
    try:
        password_in_bytes = password.password.encode()
        decrypted_password_in_bytes = fernet.decrypt(password_in_bytes)
        decrypted_password_in_str = decrypted_password_in_bytes.decode()  # Decrypt each password
        decrypted_passwords = decrypted_password_in_str
    except Exception as e:
        decrypted_passwords = 'Error decrypting password'

    if request.method == 'POST':
        username = request.POST.get('username')
        password_value = request.POST.get('password')
        email = request.POST.get('email')
        web_or_app = request.POST.get('web_or_app')
        note = request.POST.get('note')

        encrypted_data = fernet.encrypt(password_value.encode())
        encrypted_data = encrypted_data.decode()

        # Update the password details
        password.username = username
        password.password = encrypted_data
        password.email = email
        password.web_or_app = web_or_app
        password.note = note
        password.state = state_of_password(password_value)

        password.save()  # Save the updated password to the database
        return redirect('dashboard')  # Redirect to the dashboard

    return render(request, 'webapp/update.html', {'password': password, 'decrypted_passwords': decrypted_passwords})
