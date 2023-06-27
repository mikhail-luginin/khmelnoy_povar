from apps.bar.models import Timetable
from apps.lk.models import Review, Employee
from core import validators


def reviews_all():
    return Review.objects.all()


def create(photo, review_date: str, storage_id: int, jobs: list):
    validators.validate_field(photo, 'фото')
    validators.validate_field(review_date, 'дата отзыва')
    validators.validate_field(storage_id, 'заведение')
    validators.validate_field(jobs, 'тип')

    review = Review.objects.create(review_date=review_date, storage_id=storage_id, photo=photo)
    review.jobs.set(jobs)
    review.save()


def link_to_employee(review_id: int) -> None:
    review = Review.objects.filter(id=review_id).first()

    if review and review.status == 1:
        employees = Employee.objects.filter(job_place__in=review.jobs.all())
        if employees.count() > 0:
            for employee in employees:
                timetable = Timetable.objects.filter(date_at=review.review_date,
                                                     employee_id=employee.id, storage_id=review.storage_id).exists()
                if timetable:
                    employee.reviews.add(review)
                    employee.save()
            review.status = 2
            review.save()
    else:
        raise Review.DoesNotExist('Отзыв с указанным идентификатором не найден.')
