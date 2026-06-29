from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Profile, Question, ExamResult
from PIL import Image, ImageDraw, ImageFont
from django.http import HttpResponse
import io

# ---------- HOME ----------------------
def home(request):
    return render(request, 'simulator/home.html')

# ─── REGISTER ───────────────────────────────────────────
def register(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        jamb_score = request.POST.get('jamb_score')
        aspiring_course = request.POST.get('aspiring_course')
        username = request.POST.get('username')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken')
            return redirect('register')

        user = User.objects.create_user(username=username, password=password)
        Profile.objects.create(
            user=user,
            full_name=full_name,
            jamb_score=int(jamb_score),
            aspiring_course=aspiring_course
        )
        login(request, user)
        return redirect('dashboard')

    return render(request, 'simulator/register.html')


# ─── LOGIN ───────────────────────────────────────────────
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'simulator/login.html')


# ─── LOGOUT ──────────────────────────────────────────────
def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard(request):
    profile = Profile.objects.get(user=request.user)
    results = ExamResult.objects.filter(user=request.user).order_by('-date_taken')
    last_result = results.first()

    # Leaderboard — top 10 best aggregates across all users
    from django.db.models import Max

    leaderboard = (
        ExamResult.objects
        .values('user__username', 'user__profile__full_name')
        .annotate(best=Max('aggregate'))
        .order_by('-best')[:10]
    )

    context = {
        'profile': profile,
        'last_result': last_result,
        'total_attempts': results.count(),
        'results': results[:5],
        'leaderboard': leaderboard,
    }
    return render(request, 'simulator/dashboard.html', context)



# ─── EXAM ────────────────────────────────────────────────
import random
import json
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Profile, Question, ExamResult

@login_required
def exam(request):
    profile = Profile.objects.get(user=request.user)

    # ---------- SUBMIT ----------
    if request.method == "POST":
        answer_key = request.session.get("answer_key", {})
        question_data = request.session.get("question_data", {})
        score = 0
        review = []

        for qid, correct in answer_key.items():
            selected = request.POST.get(f"q{qid}", None)
            is_correct = bool(selected and selected.upper() == correct.upper())
            if is_correct:
                score += 1

            qinfo = question_data.get(qid, {})
            review.append({
                "question": qinfo.get("question_text", ""),
                "options": qinfo.get("options", []),
                "selected": selected,
                "correct": correct,
                "is_correct": is_correct,
                "subject": qinfo.get("subject", ""),
            })

        aggregate = round((profile.jamb_score / 8) + score, 2)

        result = ExamResult.objects.create(
            user=request.user,
            postutme_score=score,
            aggregate=aggregate,
            review_data=json.dumps(review)
        )

        request.session.pop("answer_key", None)
        request.session.pop("question_data", None)

        return redirect("result", result_id=result.id)

    # ---------- GET ----------
    questions = []
    answer_key = {}
    question_data = {}

    subjects = [
        "Mathematics",
        "English",
        "Chemistry",
        "Physics",
        profile.aspiring_course,
    ]

    for subject in subjects:
        qs = list(Question.objects.filter(subject=subject))
        selected = random.sample(qs, min(10, len(qs)))

        for q in selected:
            options = [
                ("A", q.option_a),
                ("B", q.option_b),
                ("C", q.option_c),
                ("D", q.option_d),
            ]

            correct_text = dict(options)[q.correct_answer.upper()]
            random.shuffle(options)

            shuffled = []
            for new_letter, (_, text) in zip(["A", "B", "C", "D"], options):
                shuffled.append((new_letter, text))
                if text == correct_text:
                    answer_key[str(q.id)] = new_letter

            q.shuffled_options = shuffled
            questions.append(q)

            # Save question info for review
            question_data[str(q.id)] = {
                "question_text": q.question_text,
                "subject": q.subject,
                "options": shuffled,
            }

    request.session["answer_key"] = answer_key
    request.session["question_data"] = question_data

    return render(request, "simulator/exam.html", {
        "questions": questions,
        "duration": 30,
    })

# ─── RESULT ──────────────────────────────────────────────
@login_required
def result(request, result_id):
    result = ExamResult.objects.get(id=result_id, user=request.user)
    profile = Profile.objects.get(user=request.user)
    return render(request, 'simulator/result.html', {
        'result': result,
        'profile': profile
    })


# ─── DOWNLOAD RESULT IMAGE ───────────────────────────────
@login_required
def download_result(request, result_id):
    result = ExamResult.objects.get(id=result_id, user=request.user)
    profile = Profile.objects.get(user=request.user)

    # Create image
    img = Image.new('RGB', (800, 500), color='#0a1628')
    draw = ImageDraw.Draw(img)

    try:
        font_large = ImageFont.truetype("arial.ttf", 40)
        font_medium = ImageFont.truetype("arial.ttf", 28)
        font_small = ImageFont.truetype("arial.ttf", 22)
    except:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # Draw content
    draw.text((400, 50), "AFIT POST-UTME RESULT", fill='#00ff88', font=font_large, anchor='mm')
    draw.text((400, 130), profile.full_name, fill='white', font=font_medium, anchor='mm')
    draw.text((400, 180), f"Aspiring Course: {profile.aspiring_course}", fill='#aaaaaa', font=font_small, anchor='mm')
    draw.text((400, 250), f"JAMB Score: {profile.jamb_score}", fill='white', font=font_medium, anchor='mm')
    draw.text((400, 300), f"Post-UTME Score: {result.postutme_score}/50", fill='white', font=font_medium, anchor='mm')
    draw.text((400, 370), f"Aggregate: {result.aggregate}/100", fill='#00ff88', font=font_large, anchor='mm')
    draw.text((400, 450), f"Date: {result.date_taken.strftime('%d %b %Y')}", fill='#aaaaaa', font=font_small, anchor='mm')

    # Return as download
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='image/png')
    response['Content-Disposition'] = f'attachment; filename="afit_result_{profile.full_name}.png"'
    return response

# ----------REVIEW-------------
import json

@login_required
def review(request, result_id):
    result = ExamResult.objects.get(id=result_id, user=request.user)
    review_data = result.get_review()
    return render(request, 'simulator/review.html', {
        'result': result,
        'review_data': review_data,
    })