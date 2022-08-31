import json
import urllib.request
from abc import ABC, abstractmethod
from typing import Any, Generic, Sequence, TypeVar, Union

from flask import Flask, abort, request
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

T_co = TypeVar("T_co", covariant=True)
JSONType = dict[str, Any]


class QuestionService(ABC, Generic[T_co]):
    @abstractmethod
    def get_questions(self, num: int) -> T_co:
        pass


class StorageService(ABC):
    @abstractmethod
    def insert_uniq_questions(self, questions: Sequence[JSONType]) -> int:
        pass


class JSONQuestionService(QuestionService[Sequence[JSONType]]):
    def __init__(self, url: str = "https://jservice.io/api/random?count=") -> None:
        self.__url: str = url

    def get_questions(self, num: int) -> Sequence[JSONType]:
        with urllib.request.urlopen(url=f"{self.__url}{num}") as response:
            questions: Sequence[JSONType] = json.loads(response.read())
            return questions


class Questions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.TIMESTAMP(timezone=True), nullable=False)

    def __repr__(self) -> str:
        return (
                f'Questions('
                f'id={self.id!r}, '
                f'question={self.question!r}'
                f')'
        )


class PgStorageService(StorageService):
    def insert_uniq_questions(self, questions: Sequence[JSONType]) -> int:
        questions_dict = {}
        for question in questions:
            questions_dict[question['id']] = Questions(
                    id=question['id'],
                    question=question['question'],
                    answer=question['answer'],
                    created_at=question['created_at']
            )

        duplicate_questions = db.session.query(Questions.id).filter(
                Questions.id.in_(list(questions_dict))
        ).all()
        non_uniq_ids: set = set(i[0] for i in duplicate_questions)

        uniq_ids = set(questions_dict) - non_uniq_ids
        for uniq_id in uniq_ids:
            db.session.add(questions_dict[uniq_id])

        inserted_count: int = len(questions_dict) - len(non_uniq_ids)
        return inserted_count


class QAWS:
    def __init__(
            self,
            db_service: PgStorageService,
            questions_service: QuestionService[Sequence[JSONType]]):
        self.db_service: StorageService = db_service
        self.questions_service: QuestionService[Sequence[JSONType]] = questions_service

    def request_questions(self) -> Union[str, dict[None, None]]:
        questions_num: int = request.get_json().get('questions_num')
        assert isinstance(questions_num, int) and questions_num >= 0, (
            f"questions_num={questions_num}"
        )
        if questions_num == 0:
            return {}
        else:
            questions = self.questions_service.get_questions(questions_num)
            attempts: int = 100
            while attempts > 0:
                attempts -= 1
                inserted_questions_num = self.db_service.insert_uniq_questions(
                        questions=questions
                )
                remainder_questions_num = questions_num - inserted_questions_num
                if remainder_questions_num:
                    questions = self.questions_service.get_questions(remainder_questions_num)
                    questions_num = remainder_questions_num
                else:
                    question: str = questions[-1]['question']
                    return question
            abort(500)


def create_app() -> Flask:
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@db/postgres'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    db_service = PgStorageService()
    question_service = JSONQuestionService()
    qaws = QAWS(
            db_service=db_service,
            questions_service=question_service
    )

    @app.before_first_request
    def init_db() -> None:
        db.create_all()

    @app.teardown_request
    def close(e=None) -> None:
        db.session.commit()
        db.session.remove()

    app.add_url_rule(
            rule="/",
            methods=['POST'],
            view_func=qaws.request_questions)
    return app
