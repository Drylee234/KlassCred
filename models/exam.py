from extensions import db


class Exam(db.Model):
    __tablename__ = "exam"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    subject = db.Column(
        db.String(100),
        nullable=False
    )

    questions = db.Column(
        db.JSON,
        nullable=False
    )

    time_limit = db.Column(
        db.Integer,
        nullable=False
    )
    
    max_attempts = db.Column(
        db.Integer
    ) 


    attempts = db.relationship(
        "ExamAttempt",
        back_populates="exam",
        cascade="all, delete-orphan"
    )
    
    def attempts_left(self, teacher_id):
        if self.max_attempts is None:
            return float('inf') # Unlimited attempts
            
        used_attempts = ExamAttempt.query.filter_by(
            exam_id=self.id, 
            teacher_id=teacher_id
        ).count()
        
        return max(0, self.max_attempts - used_attempts)


class ExamAttempt(db.Model):
    __tablename__ = "exam_attempt"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    teacher_id = db.Column(
        db.Integer,
        db.ForeignKey("teacher.id"),
        nullable=False,
        index=True
    )

    exam_id = db.Column(
        db.Integer,
        db.ForeignKey("exam.id"),
        nullable=False,
        index=True
    )

    score = db.Column(
        db.Float
    )

    started_at = db.Column(
        db.DateTime
    )

    submitted_at = db.Column(
        db.DateTime
    )

    answers = db.Column(
        db.JSON
    )

    completed = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    teacher = db.relationship(
        "Teacher",
        back_populates="exam_attempts"
    )

    exam = db.relationship(
        "Exam",
        back_populates="attempts"
    )