import csv
from django.core.management.base import BaseCommand
from simulator.models import Question

class Command(BaseCommand):
    help = 'Bulk upload questions from CSV'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str)

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']
        created = 0
        errors = 0

        with open(file_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    Question.objects.create(
                        subject=row['subject'].strip(),
                        question_text=row['question_text'].strip(),
                        option_a=row['option_a'].strip(),
                        option_b=row['option_b'].strip(),
                        option_c=row['option_c'].strip(),
                        option_d=row['option_d'].strip(),
                        correct_answer=row['correct_answer'].strip().upper(),
                        order=int(row.get('order', 0)),
                    )
                    created += 1
                except Exception as e:
                    self.stdout.write(f'Error: {row} — {e}')
                    errors += 1

        self.stdout.write(self.style.SUCCESS(
            f'{created} questions uploaded, {errors} errors.'
        ))