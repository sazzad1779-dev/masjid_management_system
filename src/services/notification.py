from sqlmodel import Session, select
from src.crud import notification as notification_crud
from src.schemas.notification import NotificationCreate
from src.models.masjid_member import MasjidMember
from src.models.user import User

class NotificationService:
    @staticmethod
    def create_notification(
        db: Session, 
        masjid_id: str, 
        user_id: str, 
        type: str, 
        title: str, 
        body: str,
        related_entity_type: str = None,
        related_entity_id: str = None
    ):
        notification_in = NotificationCreate(
            masjid_id=masjid_id,
            user_id=user_id,
            type=type,
            title=title,
            body=body,
            related_entity_type=related_entity_type,
            related_entity_id=related_entity_id
        )
        return notification_crud.create(db, obj_in=notification_in)

    @staticmethod
    def notify_masjid_admins(
        db: Session,
        masjid_id: str,
        type: str,
        title: str,
        body: str,
        related_entity_type: str = None,
        related_entity_id: str = None
    ):
        # Get all admins and committee members for this masjid
        statement = select(MasjidMember).where(
            MasjidMember.masjid_id == masjid_id,
            MasjidMember.role.in_(["admin", "committee"])
        )
        members = db.exec(statement).all()
        
        notifications = []
        for member in members:
            notifications.append(
                NotificationService.create_notification(
                    db,
                    masjid_id=masjid_id,
                    user_id=member.user_id,
                    type=type,
                    title=title,
                    body=body,
                    related_entity_type=related_entity_type,
                    related_entity_id=related_entity_id
                )
            )
        return notifications

    @staticmethod
    def notify_user_invitation(db: Session, masjid_member: MasjidMember):
        """
        Triggered when a user is added to a masjid.
        """
        from src.models.masjid import Masjid
        masjid = db.get(Masjid, masjid_member.masjid_id)
        masjid_name = masjid.name if masjid else "a Masjid"
        
        return NotificationService.create_notification(
            db,
            masjid_id=masjid_member.masjid_id,
            user_id=masjid_member.user_id,
            type="masjid_invitation",
            title="Masjid Invitation",
            body=f"You have been invited to join {masjid_name} as {masjid_member.role}.",
            related_entity_type="masjid",
            related_entity_id=masjid_member.masjid_id
        )

    @staticmethod
    def notify_role_change(db: Session, masjid_member: MasjidMember):
        """
        Triggered when a user's role is updated.
        """
        from src.models.masjid import Masjid
        masjid = db.get(Masjid, masjid_member.masjid_id)
        masjid_name = masjid.name if masjid else "a Masjid"
        
        return NotificationService.create_notification(
            db,
            masjid_id=masjid_member.masjid_id,
            user_id=masjid_member.user_id,
            type="role_updated",
            title="Role Updated",
            body=f"Your role at {masjid_name} has been updated to {masjid_member.role}.",
            related_entity_type="masjid",
            related_entity_id=masjid_member.masjid_id
        )

    @staticmethod
    def notify_income_recorded(db: Session, masjid_id: str, income: "Income"):
        """
        Notify admins when new income is recorded.
        """
        return NotificationService.notify_masjid_admins(
            db,
            masjid_id=masjid_id,
            type="income_recorded",
            title="New Income Recorded",
            body=f"New income '{income.title}' of {income.amount} {income.currency} has been recorded.",
            related_entity_type="income",
            related_entity_id=income.id
        )

    @staticmethod
    def notify_expense_recorded(db: Session, masjid_id: str, expense: "Expense"):
        """
        Notify admins when new expense is recorded.
        """
        return NotificationService.notify_masjid_admins(
            db,
            masjid_id=masjid_id,
            type="expense_recorded",
            title="New Expense Recorded",
            body=f"New expense '{expense.title}' of {expense.amount} {expense.currency} has been recorded.",
            related_entity_type="expense",
            related_entity_id=expense.id
        )

    @staticmethod
    def notify_donation_verified(db: Session, masjid_id: str, donation: "DonationRecord"):
        """
        Notify donor and admins when a donation is verified.
        """
        from src.models.donor import Donor
        donor = db.get(Donor, donation.donor_id)
        
        # Notify Admins
        NotificationService.notify_masjid_admins(
            db,
            masjid_id=masjid_id,
            type="donation_verified",
            title="Donation Verified",
            body=f"Donation for {donation.month} from {donor.full_name} has been verified.",
            related_entity_type="donation",
            related_entity_id=donation.id
        )
        
        # Notify Donor (if they have a user account)
        if donor.user_id:
            NotificationService.create_notification(
                db,
                masjid_id=masjid_id,
                user_id=donor.user_id,
                type="donation_verified",
                title="Donation Payment Verified",
                body=f"Your donation for {donation.month} has been verified. Thank you!",
                related_entity_type="donation",
                related_entity_id=donation.id
            )

    @staticmethod
    def send_email(to_email: str, subject: str, body: str):
        """
        Placeholder for email notification logic.
        In a real application, this would use a service like SendGrid or AWS SES.
        """
        print(f"DEBUG: Sending email to {to_email} | Subject: {subject} | Body: {body}")
        return True
