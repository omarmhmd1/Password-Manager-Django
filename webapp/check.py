import string

def state_of_password(password):
    password_criteria = [0, 0, 0, 0, 0]
    if 8 <= len(password) <= 12 or len(password) > 12:
        password_criteria[0] = 1

    for i in password:
        if i in string.ascii_lowercase:
            password_criteria[1] = 1
        elif i in string.ascii_uppercase:
            password_criteria[2] = 1
        elif i in string.digits:
            password_criteria[3] = 1
        elif i in string.punctuation:
            password_criteria[4] = 1
    
    sum_of_checks = sum(password_criteria)
    if sum_of_checks == 5:
        state = 'Strong'
    elif sum_of_checks >= 3:
        state = 'Medium'
    elif sum_of_checks >=2:
        state = 'Weak'
    else:
        state = 'Very weak'
    return state
