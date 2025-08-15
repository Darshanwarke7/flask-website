from flask import Flask, render_template, request
import requests
import random

app = Flask(__name__)

# ===================== API Nutrition Info (Edamam) =====================
EDAMAM_APP_ID = '1b294015'
EDAMAM_APP_KEY = 'af1d30ca1ae20dc47834a695572a7aec'

# Predefined nutrition data for common foods (in grams)
NUTRITION_DATA = {
    'Oats': {'portion': 50, 'calories': 194, 'protein': 6.7, 'carbs': 33.5, 'fats': 3.6},
    'Almonds': {'portion': 30, 'calories': 174, 'protein': 6.4, 'carbs': 6.1, 'fats': 15.0},
    'Boiled Eggs': {'portion': 100, 'calories': 155, 'protein': 13, 'carbs': 1.1, 'fats': 11},
    'Grilled Chicken Salad': {'portion': 200, 'calories': 330, 'protein': 62, 'carbs': 6, 'fats': 7},
    'Brown Rice': {'portion': 150, 'calories': 218, 'protein': 4.5, 'carbs': 46, 'fats': 1.6},
    'Apple': {'portion': 150, 'calories': 78, 'protein': 0.4, 'carbs': 21, 'fats': 0.3},
    'Peanut Butter': {'portion': 30, 'calories': 188, 'protein': 8, 'carbs': 6, 'fats': 16},
    'Steamed Veggies': {'portion': 150, 'calories': 75, 'protein': 3, 'carbs': 15, 'fats': 0.5},
    'Paneer': {'portion': 100, 'calories': 265, 'protein': 18, 'carbs': 4, 'fats': 20},
    'Tofu': {'portion': 150, 'calories': 117, 'protein': 14, 'carbs': 3, 'fats': 7},
    'Quinoa': {'portion': 150, 'calories': 222, 'protein': 8, 'carbs': 39, 'fats': 4},
    'Banana': {'portion': 120, 'calories': 105, 'protein': 1.3, 'carbs': 27, 'fats': 0.4},
    'Milk': {'portion': 250, 'calories': 155, 'protein': 8, 'carbs': 12, 'fats': 8},
    'Rice': {'portion': 150, 'calories': 205, 'protein': 4.3, 'carbs': 45, 'fats': 0.4},
    'Dal': {'portion': 200, 'calories': 230, 'protein': 18, 'carbs': 40, 'fats': 0.8},
    'Mixed Veg': {'portion': 150, 'calories': 75, 'protein': 3, 'carbs': 15, 'fats': 0.5},
    'Curd': {'portion': 150, 'calories': 150, 'protein': 8, 'carbs': 11, 'fats': 8},
    'Smoothie': {'portion': 300, 'calories': 200, 'protein': 5, 'carbs': 35, 'fats': 5},
    'Dry Fruits': {'portion': 40, 'calories': 120, 'protein': 1.5, 'carbs': 28, 'fats': 0.5},
    'Chapati': {'portion': 60, 'calories': 180, 'protein': 6, 'carbs': 30, 'fats': 3},
    'Sabzi': {'portion': 200, 'calories': 150, 'protein': 4, 'carbs': 20, 'fats': 6},
    'Egg Curry': {'portion': 200, 'calories': 300, 'protein': 20, 'carbs': 10, 'fats': 20},
    'Peanut Butter Toast': {'portion': 100, 'calories': 350, 'protein': 12, 'carbs': 30, 'fats': 20},
    'Milkshake': {'portion': 300, 'calories': 400, 'protein': 12, 'carbs': 50, 'fats': 15},
    'Chicken Curry': {'portion': 200, 'calories': 400, 'protein': 35, 'carbs': 15, 'fats': 25},
    'Roti': {'portion': 60, 'calories': 180, 'protein': 6, 'carbs': 30, 'fats': 3},
    'Protein Shake': {'portion': 300, 'calories': 250, 'protein': 30, 'carbs': 15, 'fats': 5},
    'Nuts': {'portion': 30, 'calories': 180, 'protein': 6, 'carbs': 6, 'fats': 16},
    'Paneer Bhurji': {'portion': 200, 'calories': 350, 'protein': 25, 'carbs': 10, 'fats': 25},
    'Sweet Potato': {'portion': 150, 'calories': 180, 'protein': 4, 'carbs': 41, 'fats': 0.3}
}

# Categorize foods by meal type and goal
FOOD_CATEGORIES = {
    'lose': {
        'Breakfast': ['Oats', 'Almonds', 'Boiled Eggs', 'Tofu', 'Banana'],
        'Lunch': ['Grilled Chicken Salad', 'Brown Rice', 'Steamed Veggies', 'Paneer', 'Quinoa'],
        'Snack': ['Apple', 'Peanut Butter', 'Dry Fruits', 'Nuts', 'Protein Shake'],
        'Dinner': ['Steamed Veggies', 'Paneer', 'Tofu', 'Quinoa', 'Egg Curry']
    },
    'maintain': {
        'Breakfast': ['Oats', 'Banana', 'Milk', 'Peanut Butter Toast', 'Chapati'],
        'Lunch': ['Rice', 'Dal', 'Mixed Veg', 'Curd', 'Chicken Curry'],
        'Snack': ['Smoothie', 'Dry Fruits', 'Milkshake', 'Nuts', 'Protein Shake'],
        'Dinner': ['Chapati', 'Sabzi', 'Egg Curry', 'Paneer Bhurji', 'Sweet Potato']
    },
    'gain': {
        'Breakfast': ['Peanut Butter Toast', 'Banana', 'Milkshake', 'Oats with Nuts', 'Eggs with Toast'],
        'Lunch': ['Chicken Curry', 'Rice', 'Roti', 'Paneer Bhurji', 'Dal with Rice'],
        'Snack': ['Protein Shake', 'Nuts', 'Dry Fruits', 'Milkshake', 'Peanut Butter Sandwich'],
        'Dinner': ['Paneer Bhurji', 'Chapati', 'Sweet Potato', 'Chicken Curry', 'Egg Curry']
    }
}

def get_nutrition_info(food_name):
    # First try our predefined data
    if food_name in NUTRITION_DATA:
        return {
            'name': food_name,
            'portion': NUTRITION_DATA[food_name]['portion'],
            'calories': NUTRITION_DATA[food_name]['calories'],
            'protein': NUTRITION_DATA[food_name]['protein'],
            'carbs': NUTRITION_DATA[food_name]['carbs'],
            'fats': NUTRITION_DATA[food_name]['fats']
        }
    
    # Fallback to API if not in our predefined data
    url = "https://api.edamam.com/api/nutrition-data"
    params = {
        'app_id': EDAMAM_APP_ID,
        'app_key': EDAMAM_APP_KEY,
        'ingr': food_name
    }
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        return {
            'name': food_name,
            'portion': 100,  # Default portion if not in our data
            'calories': round(data.get('calories', 0)),
            'protein': round(data.get('totalNutrients', {}).get('PROCNT', {}).get('quantity', 0), 2),
            'carbs': round(data.get('totalNutrients', {}).get('CHOCDF', {}).get('quantity', 0), 2),
            'fats': round(data.get('totalNutrients', {}).get('FAT', {}).get('quantity', 0), 2)
        }
    else:
        return {
            'name': food_name,
            'portion': 100,
            'calories': 0,
            'protein': 0,
            'carbs': 0,
            'fats': 0
        }

# ===================== Workout API Setup =====================
EXERCISE_API_URL = "https://exercisedb.p.rapidapi.com/exercises/bodyPart/"
HEADERS = {
    "X-RapidAPI-Key": "5428ac2972mshc00f2251613a944p19c5a3jsn309cefb1c0be",
    "X-RapidAPI-Host": "exercisedb.p.rapidapi.com"
}

def fetch_workouts_from_api(body_part):
    try:
        response = requests.get(EXERCISE_API_URL + body_part, headers=HEADERS)
        data = response.json()

        workouts = [{
            'name': ex['name'].title(),
            'sets': 3,
            'reps': '10-12',
            'gifUrl': ex.get('gifUrl', '')
        } for ex in data[:5]]

        return workouts
    except Exception as e:
        print(f"API fetch error: {e}")
        return []

# ===================== Constants =====================
activity_multipliers = {
    'sedentary': 1.2,
    'light': 1.375,
    'moderate': 1.55,
    'active': 1.725
}

goal_adjustment = {
    'lose': -500,
    'maintain': 0,
    'gain': 500
}

# ===================== Routes =====================
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/meal-plan')
def meal_plan():
    return render_template('meal_plan.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    height = float(request.form['height'])
    weight = float(request.form['weight'])
    age = int(request.form['age'])
    gender = request.form['gender']
    activity = request.form['activity']
    goal = request.form['goal']

    bmr = 10 * weight + 6.25 * height - 5 * age + (5 if gender == 'male' else -161)
    tdee = bmr * activity_multipliers[activity]
    daily_calories = tdee + goal_adjustment[goal]

    protein = round((0.3 * daily_calories) / 4)
    carbs = round((0.4 * daily_calories) / 4)
    fats = round((0.3 * daily_calories) / 9)

    # Generate random meal plan based on goal
    plan = {}
    for meal in ['Breakfast', 'Lunch', 'Snack', 'Dinner']:
        # Select 2-3 random foods for each meal
        num_items = random.randint(2, 3)
        selected_foods = random.sample(FOOD_CATEGORIES[goal][meal], num_items)
        plan[meal] = " + ".join(selected_foods)

    detailed_nutrition = {}
    for meal, items in plan.items():
        item_list = [i.strip() for i in items.split('+')]
        detailed_nutrition[meal] = [get_nutrition_info(item) for item in item_list]

    # Calculate totals
    totals = {
        'calories': sum(food['calories'] for meal in detailed_nutrition.values() for food in meal),
        'protein': round(sum(food['protein'] for meal in detailed_nutrition.values() for food in meal), 2),
        'carbs': round(sum(food['carbs'] for meal in detailed_nutrition.values() for food in meal), 2),
        'fats': round(sum(food['fats'] for meal in detailed_nutrition.values() for food in meal), 2)
    }

    return render_template('result.html',
                         calories=round(daily_calories),
                         protein=protein,
                         carbs=carbs,
                         fats=fats,
                         plan=plan,
                         nutrition_info=detailed_nutrition,
                         totals=totals)

@app.route('/workout', methods=['GET', 'POST'])
def generate_workout():
    if request.method == 'POST':
        home_workouts = [
            {'name': 'Push-Ups', 'target': 'Chest/Arms', 'duration': 8, 'sets_reps': '4 sets of 12', 'video_url': 'https://www.youtube.com/embed/IODxDxX7oi4'},
            {'name': 'Bodyweight Squats', 'target': 'Legs', 'duration': 10, 'sets_reps': '4 sets of 15', 'video_url': 'https://www.youtube.com/embed/aclHkVaku9U'},
            {'name': 'Plank Hold', 'target': 'Core', 'duration': 5, 'sets_reps': '3 x 60 seconds', 'video_url': 'https://www.youtube.com/embed/pSHjTRCQxIw'},
            {'name': 'Burpees', 'target': 'Full Body', 'duration': 8, 'sets_reps': '3 sets of 10', 'video_url': 'https://www.youtube.com/embed/TU8QYVW0gDU'},
            {'name': 'Mountain Climbers', 'target': 'Core/Cardio', 'duration': 6, 'sets_reps': '3 sets of 40 secs', 'video_url': 'https://www.youtube.com/embed/nmwgirgXLYM'},
        ]

        gym_workouts = [
            {'name': 'Bench Press', 'target': 'Chest', 'duration': 10, 'sets_reps': '4 sets of 10', 'video_url': 'https://www.youtube.com/embed/gRVjAtPip0Y'},
            {'name': 'Lat Pulldown', 'target': 'Back', 'duration': 8, 'sets_reps': '3 sets of 12', 'video_url': 'https://www.youtube.com/embed/CAwf7n6Luuc'},
            {'name': 'Leg Press', 'target': 'Legs', 'duration': 10, 'sets_reps': '4 sets of 12', 'video_url': 'https://www.youtube.com/embed/IZxyjW7MPJQ'},
            {'name': 'Cable Triceps Pushdown', 'target': 'Arms', 'duration': 6, 'sets_reps': '3 sets of 15', 'video_url': 'https://www.youtube.com/embed/2-LAMcpzODU'},
            {'name': 'Treadmill Intervals', 'target': 'Cardio', 'duration': 15, 'sets_reps': '3 rounds of 2 mins', 'video_url': 'https://www.youtube.com/embed/yZHYuKaXg5s'},
        ]

        all_workouts = home_workouts + gym_workouts
        random.shuffle(all_workouts)
        workouts = random.sample(all_workouts, 5)

        return render_template('workout.html', workouts=workouts)

    return render_template('workout.html', workouts=[])

@app.route('/gym-workout', methods=['GET', 'POST'])
def gym_workout():
    workouts = []
    day = ""
    body_type = ""
    weight_category = ""

    if request.method == 'POST':
        body_type = request.form['body_type']
        weight_category = request.form['weight_category']
        day = request.form['day']

        # Map days to body parts
        part_map = {
            'monday': 'chest',
            'tuesday': 'back',
            'wednesday': 'lower legs',  # More specific for API
            'thursday': 'shoulders',
            'friday': 'upper arms',    # More specific for API
            'saturday': 'cardio',       # Will handle specially
            'sunday': 'waist'          # API term for core
        }

        body_part = part_map.get(day.lower(), 'cardio')
        
        try:
            # Fetch exercises from API
            response = requests.get(EXERCISE_API_URL + body_part, headers=HEADERS)
            data = response.json()
            
            # Process API data and add randomness
            all_exercises = [{
                'name': ex['name'].title(),
                'target': ex.get('target', '').title(),
                'equipment': ex.get('equipment', '').title(),
                'gifUrl': ex.get('gifUrl', ''),
                'sets': random.randint(3, 4),
                'reps': f"{random.randint(8, 12)}-{random.randint(12, 15)}" if body_part != 'cardio' else f"{random.randint(30, 45)} secs"
            } for ex in data]

            # Filter based on body type and weight category
            filtered_exercises = []
            for ex in all_exercises:
                # Adjust for weight category
                if weight_category == 'underweight':
                    ex['sets'] = max(2, ex['sets'] - 1)
                    ex['reps'] = f"{random.randint(10, 12)}-{random.randint(12, 14)}"
                elif weight_category == 'overweight':
                    ex['sets'] = ex['sets'] + 1
                    ex['reps'] = f"{random.randint(12, 15)}-{random.randint(15, 20)}"
                
                # Adjust for body type
                if body_type == 'ectomorph' and 'cardio' not in body_part:
                    ex['sets'] = ex['sets'] + 1
                elif body_type == 'endomorph' and 'cardio' in body_part:
                    ex['reps'] = f"{random.randint(45, 60)} secs"
                
                filtered_exercises.append(ex)

            # Randomly select 4-6 exercises
            workouts = random.sample(filtered_exercises, min(len(filtered_exercises), random.randint(4, 6)))

        except Exception as e:
            print(f"Error fetching workouts: {e}")
            # Fallback to predefined workouts if API fails
            workouts = [{
                'name': 'Push-Ups',
                'target': 'Chest',
                'sets': 3,
                'reps': '10-12',
                'gifUrl': 'https://example.com/pushup.gif'
            }]

    return render_template('gym_workout.html',
                         workouts=workouts,
                         day=day,
                         body_type=body_type,
                         weight_category=weight_category)
@app.route('/recipes')
def recipes():
    return render_template('recipes.html')

@app.route('/result')
def result():
    return render_template('result.html')

@app.route('/tips')
def tips():
    return render_template('tips.html')


# ===================== Run =====================
if __name__ == '__main__':
    app.run(debug=True)