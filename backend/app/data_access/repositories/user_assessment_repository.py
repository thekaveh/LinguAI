from sqlalchemy.orm import Session

from app.data_access.models.user import UserAssessment
from app.schema.user_assessment import UserAssessmentCreate

class UserAssessmentRepository:
    """
    Repository class for managing user assessments in the database.
    """

    def __init__(self, session: Session):
        """
        Initializes a new instance of the UserAssessmentRepository class.

        Args:
            session (Session): The database session object.
        """
        self.session = session

    def create_user_assessment(self, assessment_data: UserAssessmentCreate):
        """
        Creates a new user assessment in the database.

        Args:
            assessment_data (UserAssessmentCreate): The data for creating the user assessment.

        Returns:
            UserAssessment: The created user assessment object.
        """
        db_user_assessment = UserAssessment(**assessment_data.dict())
        self.session.add(db_user_assessment)
        self.session.commit()
        self.session.refresh(db_user_assessment)
        return db_user_assessment

    def get_user_assessment(self, assessment_id: int):
        """
        Retrieves a user assessment from the database.

        Args:
            assessment_id (int): The ID of the user assessment.

        Returns:
            UserAssessment: The retrieved user assessment object.
        """
        return self.session.query(UserAssessment).filter(UserAssessment.assessment_id == assessment_id).first()

    def update_user_assessment(self, assessment_id: int, assessment_data: UserAssessmentCreate):
        """
        Updates a user assessment in the database.

        Args:
            assessment_id (int): The ID of the user assessment.
            assessment_data (UserAssessmentCreate): The updated data for the user assessment.

        Returns:
            UserAssessment: The updated user assessment object.
        """
        db_user_assessment = self.get_user_assessment(assessment_id)
        for key, value in assessment_data.dict().items():
            setattr(db_user_assessment, key, value)
        self.session.commit()
        self.session.refresh(db_user_assessment)
        return db_user_assessment

    def delete_user_assessment(self, assessment_id: int):
        """
        Deletes a user assessment from the database.

        Args:
            assessment_id (int): The ID of the user assessment.
        """
        db_user_assessment = self.get_user_assessment(assessment_id)
        self.session.delete(db_user_assessment)
        self.session.commit()