from .models import RecommendationTemplate
from django.core.exceptions import ObjectDoesNotExist

def calculate_calories(profile, training_level):
    """Рассчитывает дневную норму калорий с учетом возраста, цели и уровня тренировок"""
    age_category = get_age_category(profile.age)

    # Основной обмен веществ (BMR) для мужчин 
    if profile.gender == 'male':
        bmr = (10 * profile.weight) + (6.25 * profile.height) - (5 * profile.age) + 5
    else:  # Для женщин
        bmr = (10 * profile.weight) + (6.25 * profile.height) - (5 * profile.age) - 165

    # Коэффициенты для разных целей и возрастных групп (для мужчин)
    male_factors = {
        "Подростки (10-18 лет)": {"gain_weight": 1.35, "maintain_weight": 1.2, "lose_weight": 1.05},
        "Молодые (19-30 лет)": {"gain_weight": 1.3, "maintain_weight": 1.125, "lose_weight": 0.975},
        "Взрослые (31-59 лет)": {"gain_weight": 1.25, "maintain_weight": 1.075, "lose_weight": 0.9},
        "Пожилые (60+ лет)": {"gain_weight": 1.175, "maintain_weight": 1, "lose_weight": 0.85}
    }

    # Коэффициенты для разных целей и возрастных групп (для женщин)
    female_factors = {
        "Подростки (10-18 лет)": {"gain_weight": 1.25, "maintain_weight": 1.1, "lose_weight": 1},
        "Молодые (19-30 лет)": {"gain_weight": 1.2, "maintain_weight": 1.05, "lose_weight": 0.95},
        "Взрослые (31-59 лет)": {"gain_weight": 1.125, "maintain_weight": 1, "lose_weight": 0.875},
        "Пожилые (60+ лет)": {"gain_weight": 1.05, "maintain_weight": 0.95, "lose_weight": 0.8}
    }

    # Коэффициенты уровня активности (тренировки)
    training_factors = {
        "1": 1.15,
        "2-3": 1.35,
        "4-5": 1.50,
        "6+": 1.60
    }


    if profile.gender == 'male':
        goal_factor = male_factors[age_category].get(profile.goal, 1.2)
    else:
        goal_factor = female_factors[age_category].get(profile.goal, 1.2)

    training_factor = training_factors.get(training_level, 1.2)

    # Итоговый расчет
    return round(bmr * goal_factor * training_factor, 2)


def calculate_macros(weight, age_category, goal, gender):
    """Рассчитывает БЖУ на основе возраста, пола и фитнес-цели"""

    if gender == 'male':
        if age_category in ["Подростки (10-18 лет)", "Молодые (19-30 лет)"]:
            if goal == "gain_weight":
                protein_ratio = 2.5
                fat_ratio = 1.5
                carb_ratio = 3.5
            elif goal == "maintain_weight":
                protein_ratio = 2.25
                fat_ratio = 1.2
                carb_ratio = 2.9
            else:
                protein_ratio = 2.0
                fat_ratio = 1.0
                carb_ratio = 2.2

        elif age_category == "Взрослые (31-59 лет)":
            if goal == "gain_weight":
                protein_ratio = 2.2
                fat_ratio = 1.25
                carb_ratio = 2.2
            elif goal == "maintain_weight":
                protein_ratio = 1.95
                fat_ratio = 1.0
                carb_ratio = 2.0
            else:
                protein_ratio = 1.65
                fat_ratio = 0.85
                carb_ratio = 1.6

        else:
            if goal == "gain_weight":
                protein_ratio = 1.6
                fat_ratio = 1.1
                carb_ratio = 2.05
            elif goal == "maintain_weight":
                protein_ratio = 1.35
                fat_ratio = 1.0
                carb_ratio = 1.85
            else:
                protein_ratio = 1.05
                fat_ratio = 0.8
                carb_ratio = 1.4

    else:
        if age_category in ["Подростки (10-18 лет)", "Молодые (19-30 лет)"]:
            if goal == "gain_weight":
                protein_ratio = 1.3
                fat_ratio = 1.25
                carb_ratio = 1.8
            elif goal == "maintain_weight":
                protein_ratio = 1.2
                fat_ratio = 1.05
                carb_ratio = 1.4
            else:
                protein_ratio = 1.1
                fat_ratio = 0.9
                carb_ratio = 1.2

        elif age_category == "Взрослые (31-59 лет)":
            if goal == "gain_weight":
                protein_ratio = 1.25
                fat_ratio = 1.2
                carb_ratio = 1.65
            elif goal == "maintain_weight":
                protein_ratio = 1.1
                fat_ratio = 1.0
                carb_ratio = 1.15
            else:
                protein_ratio = 1.05
                fat_ratio = 0.95
                carb_ratio = 1.15

        else:
            if goal == "gain_weight":
                protein_ratio = 1.2
                fat_ratio = 1.15
                carb_ratio = 1.6
            elif goal == "maintain_weight":
                protein_ratio = 1.05
                fat_ratio = 0.85
                carb_ratio = 1.1
            else:
                protein_ratio = 1
                fat_ratio = 0.8
                carb_ratio = 1.1

    # Рассчитываем БЖУ
    proteins = round(weight * protein_ratio, 2)
    fats = round(weight * fat_ratio, 2)
    carbs = round(weight * carb_ratio, 2)

    return {
        "proteins": proteins, "fats": fats, "carbs": carbs,
        "protein_ratio": protein_ratio, "fat_ratio": fat_ratio, "carb_ratio": carb_ratio
    }


def get_age_category(age):
    """Определяет возрастную группу пользователя"""
    if age <= 18:
        return "Подростки (10-18 лет)"
    elif 19 <= age <= 30:
        return "Молодые (19-30 лет)"
    elif 31 <= age <= 59:
        return "Взрослые (31-59 лет)"
    else:
        return "Пожилые (60+ лет)"


def get_training_recommendations(gender: str, age_category: str, goal: str) -> dict:
    """
    Возвращает рекомендации по тренировкам:
    1) Сначала пытаемся взять шаблон из БД (RecommendationTemplate + WorkoutTemplate).
    2) Если шаблона нет — используем «жёстко прописанный» запасной набор.
    """
    # 1) Попытка из БД
    try:
        tpl = RecommendationTemplate.objects.get(
            gender=gender,
            age_category=age_category,
            goal=goal
        )
        return {
            'description': tpl.description,
            'workouts': [wt.name for wt in tpl.workouts.all()]
        }
    except ObjectDoesNotExist:
        pass

    recommendations = {}

    if gender == 'male':
        if age_category == "Подростки (10-18 лет)":
            if goal == "gain_weight":
                recommendations['description'] = "Силовые тренировки с упором на базовые упражнения, 3-4 раза в неделю."
                recommendations['workouts'] = [
                    "Жим штанги лежа — 3 подхода по 8-10 повторений",
                    "Приседания со штангой — 3 подхода по 8-10 повторений",
                    "Становая тяга — 3 подхода по 8-10 повторений"
                ]
            elif goal == "maintain":
                recommendations['description'] = "Смешанный режим: кардио и силовые упражнения, 3-4 раза в неделю."
                recommendations['workouts'] = [
                    "Кроссфит-тренировка — 20 минут",
                    "Силовые упражнения с собственным весом — 3 подхода по 12 повторений",
                    "Интервальное кардио — 15 минут"
                ]
            else:  # lose_weight
                recommendations['description'] = "Интенсивное кардио с функциональным тренингом, 4-5 раз в неделю."
                recommendations['workouts'] = [
                    "Бег — 30 минут",
                    "Функциональный тренинг с весом собственного тела — 3 подхода по 15 повторений"
                ]
        elif age_category == "Молодые (19-30 лет)":
            if goal == "gain_weight":
                recommendations['description'] = "Силовые тренировки с умеренной нагрузкой, 4-5 раз в неделю."
                recommendations['workouts'] = [
                    "Жим штанги лежа — 4 подхода по 8 повторений",
                    "Становая тяга — 4 подхода по 8 повторений",
                    "Приседания со штангой — 4 подхода по 8 повторений"
                ]
            elif goal == "maintain":
                recommendations['description'] = "Комбинированный режим: кардио + силовые, 4-5 раз в неделю."
                recommendations['workouts'] = [
                    "Кардио-тренировка (бег или велотренажер) — 30 минут",
                    "Комплекс базовых силовых упражнений — 3 подхода по 10 повторений"
                ]
            else:
                recommendations['description'] = "Кардио с интервальными тренировками, 4-5 раз в неделю."
                recommendations['workouts'] = [
                    "Интервальный бег — 25 минут (интервалы: 1 минута с 1-минутным отдыхом)"
                ]
        elif age_category == "Взрослые (31-59 лет)":
            if goal == "gain_weight":
                recommendations['description'] = "Силовые тренировки с акцентом на сохранение мышечной массы, 3-4 раза в неделю."
                recommendations['workouts'] = [
                    "Жим штанги лежа — 3 подхода по 8 повторений",
                    "Тяга блока к груди — 3 подхода по 10 повторений"
                ]
            elif goal == "maintain":
                recommendations['description'] = "Сбалансированные тренировки с упором на восстановление, 3-4 раза в неделю."
                recommendations['workouts'] = [
                    "Легкое кардио — 20 минут",
                    "Комплекс упражнений на растяжку и легкие силовые упражнения — 3 подхода"
                ]
            else:
                recommendations['description'] = "Легкое кардио с силовыми элементами, 3-4 раза в неделю."
                recommendations['workouts'] = [
                    "Ходьба или эллиптический тренажер — 30 минут"
                ]
        else:  # Пожилые (60+ лет)
            if goal == "gain_weight":
                recommendations['description'] = "Силовые тренировки с низкой нагрузкой и поддержанием баланса, 2-3 раза в неделю."
                recommendations['workouts'] = [
                    "Упражнения с эспандером — 2 подхода по 10 повторений",
                    "Легкие приседания с опорой — 2 подхода по 10 повторений"
                ]
            elif goal == "maintain":
                recommendations['description'] = "Умеренные тренировки с акцентом на подвижность, 2-3 раза в неделю."
                recommendations['workouts'] = [
                    "Ходьба — 20-30 минут",
                    "Легкие упражнения на растяжку — 2 подхода по 10 повторений"
                ]
            else:
                recommendations['description'] = "Легкие упражнения, ходьба, растяжка, 2-3 раза в неделю."
                recommendations['workouts'] = [
                    "Ходьба — 20-30 минут",
                    "Упражнения на гибкость и равновесие"
                ]
    else:  # Для женщин
        if age_category == "Подростки (10-18 лет)":
            if goal == "gain_weight":
                recommendations['description'] = "Умеренные силовые тренировки, 3-4 раза в неделю с акцентом на технику."
                recommendations['workouts'] = [
                    "Отжимания от стены или колен — 3 подхода по 10 повторений",
                    "Приседания с собственным весом — 3 подхода по 12 повторений",
                    "Планка — 3 подхода по 30 секунд"
                ]
            elif goal == "maintain":
                recommendations['description'] = "Комбинированные тренировки с кардио, 3-4 раза в неделю."
                recommendations['workouts'] = [
                    "Быстрая ходьба — 20 минут",
                    "Легкие упражнения с собственным весом — 2 подхода по 12 повторений",
                    "Упражнения на растяжку — 2 подхода по 10 повторений"
                ]
            else:
                recommendations['description'] = "Кардио и функциональный тренинг, 4-5 раз в неделю."
                recommendations['workouts'] = [
                    "Интервальный бег на месте — 15 минут",
                    "Комплекс упражнений на баланс и гибкость — 2 подхода по 10 повторений"
                ]
        elif age_category == "Молодые (19-30 лет)":
            if goal == "gain_weight":
                recommendations['description'] = "Силовые тренировки с умеренной нагрузкой, 4 раза в неделю."
                recommendations['workouts'] = [
                    "Жим гантелей — 3 подхода по 10 повторений",
                    "Приседания с гантелями — 3 подхода по 10 повторений",
                    "Тяга блока к груди — 3 подхода по 10 повторений"
                ]
            elif goal == "maintain":
                recommendations['description'] = "Комбинированный режим: силовые тренировки + кардио, 4 раза в неделю."
                recommendations['workouts'] = [
                    "Бег или велотренажер — 20 минут",
                    "Комплекс упражнений с гантелями — 3 подхода по 10 повторений"
                ]
            else:
                recommendations['description'] = "Интенсивное кардио и интервальные тренировки, 4-5 раз в неделю."
                recommendations['workouts'] = [
                    "Интервальный бег — 20 минут",
                    "Упражнения на функциональную подготовку — 2 подхода по 12 повторений"
                ]
        elif age_category == "Взрослые (31-59 лет)":
            if goal == "gain_weight":
                recommendations['description'] = "Силовые тренировки с низкой нагрузкой, 3-4 раза в неделю."
                recommendations['workouts'] = [
                    "Жим гантелей сидя — 3 подхода по 8-10 повторений",
                    "Тяга горизонтального блока — 3 подхода по 10 повторений"
                ]
            elif goal == "maintain":
                recommendations['description'] = "Сбалансированные тренировки, 3-4 раза в неделю."
                recommendations['workouts'] = [
                    "Бег или велотренажер — 20-25 минут",
                    "Легкие силовые упражнения с собственным весом — 2 подхода по 10 повторений"
                ]
            else:
                recommendations['description'] = "Легкий кардио режим с функциональными упражнениями, 3-4 раза в неделю."
                recommendations['workouts'] = [
                    "Быстрая ходьба — 30 минут",
                    "Упражнения на гибкость и баланс — 2 подхода по 10 повторений"
                ]
        else:  # Пожилые (60+ лет)
            if goal == "gain_weight":
                recommendations['description'] = "Легкие силовые тренировки, 2-3 раза в неделю с акцентом на стабильность и баланс."
                recommendations['workouts'] = [
                    "Упражнения с собственным весом (сидячие приседания, отжимания от стены) — 2 подхода по 10 повторений",
                    "Легкие упражнения с эспандером — 2 подхода по 10 повторений"
                ]
            elif goal == "maintain":
                recommendations['description'] = "Умеренные тренировки с растяжкой, 2-3 раза в неделю."
                recommendations['workouts'] = [
                    "Ходьба — 20 минут",
                    "Легкие упражнения на растяжку — 2 подхода по 10 повторений",
                    "Дыхательные упражнения — 5 минут"
                ]
            else:
                recommendations['description'] = "Ходьба, растяжка и легкие упражнения, 2-3 раза в неделю."
                recommendations['workouts'] = [
                    "Легкая ходьба — 20 минут",
                    "Упражнения на гибкость и равновесие — 2 подхода по 10 повторений"
                ]
    return recommendations
