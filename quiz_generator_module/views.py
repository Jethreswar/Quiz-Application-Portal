from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.contrib.auth import logout
from django.utils import timezone
import json
from django.http import JsonResponse
from django.contrib import messages
from .models import User, Questions, Quiz, QuizHistory
import random

active_user = None

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
            
        try:
            user = User.objects.get(username=username, password=password)
            global active_user
            active_user = user.username
            if user.is_admin():
                return redirect('admin_view')
            else:
                return redirect('user_view')
        except User.DoesNotExist:
            messages.error(request, "Username doesn't exist. Please contact the admin to add the user")
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def admin_view(request):
    if request.method == 'POST':
        new_question = request.POST.get('new_question')
        new_option1 = request.POST.get('new_option1')
        new_option2 = request.POST.get('new_option2')
        new_option3 = request.POST.get('new_option3')
        new_option4 = request.POST.get('new_option4')
        new_correct_answer = request.POST.get('new_correct_answer')
        new_course = request.POST.get('new_course')

        if new_question and new_option1 and new_option2 and new_option3 and new_option4 and new_correct_answer and new_course:
            # Create a new Quiz object and save it
            Questions.objects.create(
                question=new_question,
                option1=new_option1,
                option2=new_option2,
                option3=new_option3,
                option4=new_option4,
                correct_answer=new_correct_answer,
                course = new_course
            )
        else:
            pass

    questions = Questions.objects.all()
    users = User.objects.all()
    quizzes = Quiz.objects.all()
    all_quiz_history = QuizHistory.objects.all()
    for quiz in quizzes:
        user = quiz.student
        quiz.username = user.username

    for history in all_quiz_history:
        quiz = history.quiz
        user = quiz.student
        history.username = user.username
        history.course = user.courses
    quizzes = [quiz for quiz in quizzes if quiz.quizhistory_set.count() == 0]   
    distinct_courses = Questions.objects.values_list('course', flat=True).distinct()
    num_questions_choices = list(range(1, 15 + 1)) 
    quiz_duration_choices = list(range(1, 30 + 1))  
    return render(request, 'admin_page.html', {'all_quiz_history': all_quiz_history, 'quizzes': quizzes, 'users': users, 'questions': questions, 'username':active_user, 'num_questions_choices': num_questions_choices, 'quiz_duration_choices': quiz_duration_choices, 'distinct_courses': distinct_courses})

def add_user(request):
    if request.method == 'POST':
        new_username = request.POST.get('new_username')
        new_password = request.POST.get('new_password')
        new_user_role = request.POST.get('new_user_role')
        new_user_type = request.POST.get('new_user_type')
        new_user_course = request.POST.get('new_user_course')

        # Check if all required fields have values
        if new_username and new_password and new_user_role:
            # Create a new User object and save it
            User.objects.create(
                username = new_username,
                password = new_password,
                user_role = new_user_role,
                user_type = new_user_type,
                courses = new_user_course
            )
    return redirect('admin_view')

def delete_user(request, user_id):
    user = User.objects.get(pk=user_id)
    user.delete()
    return redirect('admin_view')

def modify_question(request, question_id):
    question = Questions.objects.get(pk=question_id)
    
    if request.method == 'POST':
        # Handle modification logic here
        question.question = request.POST.get('question')
        question.option1 = request.POST.get('option1')
        question.option2 = request.POST.get('option2')
        question.option3 = request.POST.get('option3')
        question.option4 = request.POST.get('option4')
        question.correct_answer = request.POST.get('correct_answer')
        question.course = request.POST.get('question_course')
        question.save()
        return redirect('admin_view')

    return render(request, 'modify_question.html', {'question': question})

def delete_question(request, question_id):
    quiz = Questions.objects.get(pk=question_id)
    quiz.delete()
    return redirect('admin_view')

def create_quiz(request):
    if request.method == 'POST':
        course_num = request.POST.get('course_number')
        num_of_question = request.POST.get('num_questions')
        quiz_duration = request.POST.get('quiz_duration')
        student = request.POST.get('student_name')
        expire_date = request.POST.get('quiz_expire_date')
        student_id = User.objects.get(pk=student)

        if course_num and num_of_question and quiz_duration and student and expire_date:
            Quiz.objects.create(
                course=course_num,
                num_questions=num_of_question,
                quiz_duration=quiz_duration,
                student=student_id,
                quiz_expire_date=expire_date
            )
        else:
            pass
    return redirect('admin_view')

def delete_quiz(request, quiz_id):
    quiz = Quiz.objects.get(pk=quiz_id)
    quiz.delete()
    return redirect('admin_view')

def user_view(request):
    user = User.objects.get(username=active_user)
    quizzes = Quiz.objects.filter(student=user)
    for quiz in quizzes:
        if quiz.quiz_expire_date < timezone.now().date():
            quiz_history_entry = QuizHistory.objects.filter(quiz=quiz).first()
            if not quiz_history_entry:
                QuizHistory.objects.create(
                    quiz=quiz,
                    quiz_date=quiz.quiz_expire_date,
                    score=0,
                    num_correct=0,
                    num_wrong=0,
                )    
    quiz_to_show = QuizHistory.objects.filter(quiz__in=quizzes)
    dates = [quiz.quiz_date.strftime('%Y-%m-%d') for quiz in quiz_to_show]
    scores = [quiz.score for quiz in quiz_to_show]

    quiz_history_data = {
        'dates': dates,
        'scores': scores,
    }


    assigned_quizzes = quizzes.exclude(id__in=quiz_to_show.values('quiz_id'))
    quiz_history_list = []
    for quiz in quizzes:
        quiz_history = QuizHistory.objects.filter(quiz=quiz).first()
        if quiz_history:
            quiz_history_list.append(quiz_history)

    return render(request, 'user_page.html', { 'quiz_history': quiz_history_list, 'quizzes': assigned_quizzes, 'username': user.username, 'quiz_history_data': json.dumps(quiz_history_data)})


def take_quiz(request, quiz_id):
    quiz = Quiz.objects.get(pk=quiz_id)
    num_questions = quiz.num_questions
    quiz_duration = quiz.quiz_duration
    course = quiz.course

    questions = Questions.objects.filter(course=course)
    selected_questions = random.sample(list(questions), num_questions)

    # quiz_questions = Quiz.objects.order_by('?')[:num_questions]

    return render(request, 'take_quiz.html', {'quiz_questions': selected_questions, 'quiz_duration': quiz_duration, 'quiz_id': quiz_id })


def submit_quiz(request, quiz_id_active):
    if request.method == 'POST':
        user_inputs = {key: request.POST[key] for key in request.POST.keys() if key.startswith('answer_')}
        quiz_ids = [int(key.replace('answer_', '')) for key in user_inputs.keys()]
        correct_answers = Questions.objects.filter(id__in=quiz_ids).values_list('id', 'correct_answer')

        num_correct = 0
        num_wrong = 0
        for quiz_id, correct_answer in correct_answers:
            user_input = user_inputs.get(f'answer_{quiz_id}')
            if user_input == correct_answer:
                num_correct += 1
            else:
                num_wrong += 1

        total_questions=num_correct+num_wrong
        if total_questions > 0:
            score = (num_correct/total_questions)*100
        else:
            score = 0  
        # Save quiz data to QuizHistory table
        quiz_date = timezone.now().date()
        quiz_instance = Quiz.objects.get(pk=quiz_id_active)
        
        QuizHistory.objects.create(
            quiz=quiz_instance,
            quiz_date=quiz_date,
            score=score,
            num_correct=num_correct,
            num_wrong=num_wrong,            
        )        
        # Display the results on submit_quiz.html
        return render(request, 'submit_quiz.html', {'score':round(score, 2), 'num_correct': num_correct, 'num_wrong': num_wrong, 'quiz_date':quiz_date})



