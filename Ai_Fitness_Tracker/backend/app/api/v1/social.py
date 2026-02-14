from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, or_, and_, update
from typing import List
import logging

from ..dependencies import get_db, get_current_user
from ...db.models import User, Friendship, ChatMessage
from ...schemas.schemas import LeaderboardUser, FriendResponse, UserResponse, ActivityFeedItem, ChatMessageResponse

logger = logging.getLogger(__name__)
from ...services.activity_service import ActivityService

router = APIRouter(prefix="/social", tags=["Social & Gamification"])

@router.get("/leaderboard/global", response_model=List[LeaderboardUser])
async def get_global_leaderboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = 10
):
    """Get global leaderboard sorted by points"""
    # 1. Get current user's friendships to show status
    friend_result = await db.execute(
        select(Friendship).where(
            or_(Friendship.sender_id == current_user.id, Friendship.receiver_id == current_user.id)
        )
    )
    friendships = friend_result.scalars().all()
    friendship_map = {}
    for f in friendships:
        if f.status == "accepted":
            other_id = f.receiver_id if f.sender_id == current_user.id else f.sender_id
            friendship_map[other_id] = "accepted"
        elif f.status == "pending":
            if f.sender_id == current_user.id:
                friendship_map[f.receiver_id] = "sent"
            else:
                friendship_map[f.sender_id] = "received"

    # 2. Get leaderboard
    result = await db.execute(
        select(User).order_by(User.points.desc()).limit(limit)
    )
    users = result.scalars().all()
    
    leaderboard = []
    for idx, user in enumerate(users, 1):
        # Calculate level from points: sqrt(points/100) + 1
        level = int((user.points / 100) ** 0.5) + 1 if user.points else 1
        
        status = friendship_map.get(user.id, "none")
        if user.id == current_user.id:
            status = "self"

        leaderboard.append(LeaderboardUser(
            id=user.id,
            username=user.username,
            points=user.points or 0,
            streak=user.streak or 0,
            level=level,
            profile_image=user.profile_image,
            rank=idx,
            friendship_status=status
        ))
    
    return leaderboard

@router.get("/leaderboard/friends", response_model=List[LeaderboardUser])
async def get_friends_leaderboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = 10
):
    """Get friends leaderboard sorted by points"""
    # 1. Get friend IDs (including self)
    result = await db.execute(
        select(Friendship)
        .where(
            or_(Friendship.sender_id == current_user.id, Friendship.receiver_id == current_user.id),
            Friendship.status == "accepted"
        )
    )
    friends = result.scalars().all()
    
    friend_ids = {current_user.id} # Set to avoid duplicates
    for f in friends:
        friend_ids.add(f.sender_id)
        friend_ids.add(f.receiver_id)
    
    # 2. Query users
    result = await db.execute(
        select(User).where(User.id.in_(friend_ids)).order_by(User.points.desc()).limit(limit)
    )
    users = result.scalars().all()
    
    leaderboard = []
    for idx, user in enumerate(users, 1):
        # Calculate level from points: sqrt(points/100) + 1
        level = int((user.points / 100) ** 0.5) + 1 if user.points else 1
        
        status = "accepted"
        if user.id == current_user.id:
            status = "self"

        leaderboard.append(LeaderboardUser(
            id=user.id,
            username=user.username,
            points=user.points or 0,
            streak=user.streak or 0,
            level=level,
            profile_image=user.profile_image,
            rank=idx,
            friendship_status=status
        ))
    
    return leaderboard

@router.get("/feed", response_model=List[ActivityFeedItem])
async def get_activity_feed(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = 20
):
    """Get activity feed of friends"""
    service = ActivityService(db)
    activities = await service.get_friend_feed(current_user.id, limit)
    return activities

@router.get("/friends", response_model=List[FriendResponse])
async def get_friends(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of friends for current user"""
    print(f"Fetching friends for user {current_user.id}")
    # Eager load sender and receiver to avoid N+1
    result = await db.execute(
        select(Friendship)
        .where(
            or_(Friendship.sender_id == current_user.id, Friendship.receiver_id == current_user.id),
            Friendship.status == "accepted"
        )
        .options(selectinload(Friendship.sender), selectinload(Friendship.receiver))
    )
    friends = result.scalars().all()
    
    result_list = []
    from ...websockets import manager
    
    for f in friends:
        # Determine which user is the friend
        friend_user = f.receiver if f.sender_id == current_user.id else f.sender
        
        status = "online" if friend_user.username in manager.active_connections else "offline"
        result_list.append(FriendResponse(
            id=friend_user.id,
            username=friend_user.username,
            points=friend_user.points or 0,
            profile_image=friend_user.profile_image,
            status=status
        ))
    return result_list

@router.get("/users/search", response_model=List[UserResponse])
async def search_users(
    q: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Search for users by username"""
    if not q or len(q) < 3:
        return []
    
    # 1. Get current user's friendships to show status
    friend_result = await db.execute(
        select(Friendship).where(
            or_(Friendship.sender_id == current_user.id, Friendship.receiver_id == current_user.id)
        )
    )
    friendships = friend_result.scalars().all()
    friendship_map = {}
    for f in friendships:
        if f.status == "accepted":
            other_id = f.receiver_id if f.sender_id == current_user.id else f.sender_id
            friendship_map[other_id] = "accepted"
        elif f.status == "pending":
            if f.sender_id == current_user.id:
                friendship_map[f.receiver_id] = "sent"
            else:
                friendship_map[f.sender_id] = "received"

    # 2. Search users
    # SQLite case-insensitive workaround
    result = await db.execute(
        select(User).where(
            User.username.ilike(f"%{q}%"), 
            User.id != current_user.id
        ).limit(10)
    )
    users = result.scalars().all()
    
    return [
        UserResponse(
            id=u.id,
            username=u.username,
            points=u.points or 0,
            profile_image=u.profile_image,
            friendship_status=friendship_map.get(u.id, "none"),
            created_at=u.created_at
        ) for u in users
    ]

@router.get("/friend-requests/received", response_model=List[FriendResponse])
async def get_received_requests(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get pending friend requests received by current user"""
    result = await db.execute(
        select(Friendship)
        .where(
            Friendship.receiver_id == current_user.id,
            Friendship.status == "pending"
        )
        .options(selectinload(Friendship.sender))
    )
    requests = result.scalars().all()
    
    return [
        FriendResponse(
            id=r.sender.id,
            username=r.sender.username,
            points=r.sender.points or 0,
            profile_image=r.sender.profile_image
        ) for r in requests
    ]

@router.post("/friend-request/{receiver_id}")
async def send_friend_request(
    receiver_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Send a friend request"""
    if receiver_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot friend yourself")
    
    # Check if user exists
    user_result = await db.execute(select(User).where(User.id == receiver_id))
    if not user_result.scalar_one_or_none():
         raise HTTPException(status_code=404, detail="User not found")

    result = await db.execute(
        select(Friendship).where(
            or_(
                and_(Friendship.sender_id == current_user.id, Friendship.receiver_id == receiver_id),
                and_(Friendship.sender_id == receiver_id, Friendship.receiver_id == current_user.id)
            )
        )
    )
    existing = result.scalars().first()
    
    if existing:
        if existing.status == "accepted":
             raise HTTPException(status_code=400, detail="Already friends")
        elif existing.status == "pending":
             raise HTTPException(status_code=400, detail="Friend request already pending")
        # If rejected, we might allow re-sending, but let's block for now or handle logic
        
    new_request = Friendship(sender_id=current_user.id, receiver_id=receiver_id, status="pending")
    db.add(new_request)
    await db.commit()
    
    # Notify receiver via WebSocket if online
    from ...websockets import manager
    import json
    # Fetch receiver username to send personal message
    receiver_result = await db.execute(select(User).where(User.id == receiver_id))
    receiver = receiver_result.scalar_one_or_none()
    if receiver:
        await manager.send_personal_message(json.dumps({
            "type": "friend_request",
            "from": current_user.username
        }), receiver.username)
        
    return {"status": "request sent"}

@router.post("/friend-request/{sender_id}/accept")
async def accept_friend_request(
    sender_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Accept a friend request"""
    result = await db.execute(
        select(Friendship).where(
            Friendship.sender_id == sender_id,
            Friendship.receiver_id == current_user.id,
            Friendship.status == "pending"
        )
    )
    friendship = result.scalars().first()
    
    if not friendship:
        raise HTTPException(status_code=404, detail="Friend request not found")
        
    friendship.status = "accepted"
    db.add(friendship)
    await db.commit()

    # Notify sender that request was accepted
    from ...websockets import manager
    import json
    sender_result = await db.execute(select(User).where(User.id == sender_id))
    sender = sender_result.scalar_one_or_none()
    if sender:
        await manager.send_personal_message(json.dumps({
            "type": "friend_accepted",
            "from": current_user.username
        }), sender.username)

    return {"status": "accepted"}

@router.post("/friend-request/{sender_id}/reject")
async def reject_friend_request(
    sender_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Reject a friend request"""
    result = await db.execute(
        select(Friendship).where(
            Friendship.sender_id == sender_id,
            Friendship.receiver_id == current_user.id,
            Friendship.status == "pending"
        )
    )
    friendship = result.scalars().first()
    
    if not friendship:
        raise HTTPException(status_code=404, detail="Friend request not found")
        
    await db.delete(friendship)
    await db.commit()
    return {"status": "rejected"}

@router.get("/chat/history/{friend_username}", response_model=List[ChatMessageResponse])
async def get_chat_history(
    friend_username: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = 50
):
    """Get chat history with a specific friend"""
    # Find friend user
    result = await db.execute(select(User).filter(User.username == friend_username))
    friend = result.scalars().first()
    if not friend:
        raise HTTPException(status_code=404, detail="Friend not found")
        
    # Query messages between current_user and friend
    result = await db.execute(
        select(ChatMessage)
        .where(
            or_(
                and_(ChatMessage.sender_id == current_user.id, ChatMessage.receiver_id == friend.id),
                and_(ChatMessage.sender_id == friend.id, ChatMessage.receiver_id == current_user.id)
            )
        )
        .order_by(ChatMessage.created_at.asc())
        .limit(limit)
    )
    messages = result.scalars().all()
    
    # Map messages to ChatMessageResponse format (message -> content, created_at -> timestamp)
    response_messages = []
    for m in messages:
        response_messages.append({
            "id": m.id,
            "sender_id": m.sender_id,
            "receiver_id": m.receiver_id,
            "content": m.message,
            "timestamp": m.created_at
        })
    
    # Mark received messages as read
    try:
        await db.execute(
            update(ChatMessage)
            .where(
                and_(
                    ChatMessage.sender_id == friend.id,
                    ChatMessage.receiver_id == current_user.id,
                    ChatMessage.is_read == 0
                )
            )
            .values(is_read=1)
        )
        await db.commit()
    except Exception as e:
        logger.error(f"Error updating chat history: {e}")
        await db.rollback()
        # We don't necessarily want to fail the whole request if marking as read fails
        # but it's better than a silent 500
    
    return response_messages

@router.post("/chat/read/{friend_username}")
async def mark_chat_as_read(
    friend_username: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark all messages from a specific friend as read"""
    print(f"DEBUG: Marking messages from {friend_username} as read for {current_user.username}")
    # Find friend user
    result = await db.execute(select(User).filter(User.username == friend_username))
    friend = result.scalars().first()
    if not friend:
        print(f"DEBUG: Friend {friend_username} not found")
        raise HTTPException(status_code=404, detail="Friend not found")
        
    # Mark received messages as read
    try:
        await db.execute(
            ChatMessage.__table__.update()
            .where(ChatMessage.sender_id == friend.id, ChatMessage.receiver_id == current_user.id, ChatMessage.is_read == 0)
            .values(is_read=1)
        )
        await db.commit()
        print(f"DEBUG: Successfully marked messages from {friend_username} as read")
    except Exception as e:
        print(f"DEBUG: Error marking messages as read: {str(e)}")
        await db.rollback()
        raise e
    
    return {"status": "success"}
