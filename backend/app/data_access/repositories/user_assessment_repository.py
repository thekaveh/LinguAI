from sqlalchemy.orm import Session

from app.data_access.models.user import UserAssessment
from app.schema.user_assessment import UserAssessmentCreate

class UserAssessmentRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_user_assessment(self, assessment_data: UserAssessmentCreate):
        db_user_assessment = UserAssessment(**assessment_data.dict())
        self.session.add(db_user_assessment)
        self.session.commit()
        self.session.refresh(db_user_assessment)
        return db_user_assessment

    def get_user_assessment(self, assessment_id: int):
        return self.session.query(UserAssessment).filter(UserAssessment.assessment_id == assessment_id).first()

    def update_user_assessment(self, assessment_id: int, assessment_data: UserAssessmentCreate):
        db_user_assessment = self.get_user_assessment(assessment_id)
        for key, value in assessment_data.dict().items():
            setattr(db_user_assessment, key, value)
        self.session.commit()
        self.session.refresh(db_user_assessment)
        return db_user_assessment

    def delete_user_assessment(self, assessment_id: int):
        db_user_assessment = self.get_user_assessment(assessment_id)
        self.session.delete(db_user_assessment)
        self.session.commit()