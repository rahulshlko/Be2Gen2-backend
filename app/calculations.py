ACTIVITY = {"sedentary":1.2,"light":1.375,"moderate":1.55,"high":1.725,"athlete":1.9}

def bmi(height_cm, weight_kg):
    h = height_cm / 100
    return round(weight_kg / (h*h), 1)

def bmr(age, sex, height_cm, weight_kg):
    # Mifflin-St Jeor; the historical Mentzer source has a different practical BMR method.
    if sex.lower() == "female":
        return round(10*weight_kg + 6.25*height_cm - 5*age - 161)
    return round(10*weight_kg + 6.25*height_cm - 5*age + 5)

def targets(age, sex, height_cm, weight_kg, activity, goal):
    b = bmr(age, sex, height_cm, weight_kg)
    tdee = round(b * ACTIVITY.get(activity, 1.55))
    delta = {"cut":-400,"recomp":-100,"maintain":0,"bulk":300}.get(goal, 0)
    calories = max(1200, tdee + delta)
    protein = round(weight_kg * 1.6)
    fat = round(weight_kg * 0.7)
    carbs = max(0, round((calories - protein*4 - fat*9) / 4))
    return {"bmi":bmi(height_cm,weight_kg),"bmr":b,"tdee":tdee,"calories":calories,"protein_g":protein,"carbs_g":carbs,"fat_g":fat}
