from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, or_
from ..db.models import FriendActivity, User, Friendship

class ActivityService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def log_activity(self, user_id: int, activity_type: str, details: str = None):
        activity = FriendActivity(
            user_id=user_id,
            activity_type=activity_type,
            details=details
        )
        self.db.add(activity)
        # We flush to ensure it has an ID, but let the caller handle the commit 
        # to maintain transaction integrity (e.g., in WorkoutService.process_workout)
        await self.db.flush() 
        return activity

    async def get_friend_feed(self, user_id: int, limit: int = 20):
        # 1. Get friend IDs
        # Friends where user is sender
        stmt_sent = select(Friendship.receiver_id).where(
            Friendship.sender_id == user_id,
            Friendship.status == "accepted"
        )
        # Friends where user is receiver
        stmt_received = select(Friendship.sender_id).where(
            Friendship.receiver_id == user_id,
            Friendship.status == "accepted"
        )
        
        sent_result = await self.db.execute(stmt_sent)
        received_result = await self.db.execute(stmt_received)
        
        friend_ids = [row[0] for row in sent_result.all()] + [row[0] for row in received_result.all()]
        
        if not friend_ids:
            return []

        # 2. Query activities
        stmt = select(FriendActivity, User).join(User).where(
            FriendActivity.user_id.in_(friend_ids)
        ).order_by(desc(FriendActivity.created_at)).limit(limit)
        
        result = await self.db.execute(stmt)
        
        activities = []
        for activity, user in result:
            activities.append({
                "id": activity.id,
                "user_id": user.id,
                "username": user.username,
                "profile_image": user.profile_image,
                "type": activity.activity_type,
                "details": activity.details,
                "created_at": activity.created_at
            })
            
        return activities
