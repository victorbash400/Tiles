import boto3
import uuid
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
import os
from decimal import Decimal
from botocore.exceptions import ClientError

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb', region_name=os.getenv('AWS_REGION', 'us-east-1'))

def convert_floats_to_decimal(data):
    """Convert float values to Decimal for DynamoDB compatibility"""
    if isinstance(data, dict):
        return {k: convert_floats_to_decimal(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_floats_to_decimal(item) for item in data]
    elif isinstance(data, float):
        return Decimal(str(data))
    else:
        return data

# Table names
USER_MEMORY_TABLE = f"tiles-user-memory-{os.getenv('STAGE', 'dev')}"
CHAT_SESSIONS_TABLE = f"tiles-chat-sessions-{os.getenv('STAGE', 'dev')}"
CHAT_MESSAGES_TABLE = f"tiles-chat-messages-{os.getenv('STAGE', 'dev')}"
PLAN_SESSIONS_TABLE = f"tiles-plan-sessions-{os.getenv('STAGE', 'dev')}"

def create_tables():
    """Create DynamoDB tables if they don't exist"""
    try:
        # User Memory Table
        try:
            dynamodb.create_table(
                TableName=USER_MEMORY_TABLE,
                KeySchema=[
                    {'AttributeName': 'id', 'KeyType': 'HASH'}
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'id', 'AttributeType': 'S'},
                    {'AttributeName': 'user_session', 'AttributeType': 'S'}
                ],
                BillingMode='PAY_PER_REQUEST',
                GlobalSecondaryIndexes=[
                    {
                        'IndexName': 'user_session-index',
                        'KeySchema': [
                            {'AttributeName': 'user_session', 'KeyType': 'HASH'}
                        ],
                        'Projection': {'ProjectionType': 'ALL'}
                    }
                ]
            )
        except ClientError as e:
            if e.response['Error']['Code'] != 'ResourceInUseException':
                raise

        # Chat Sessions Table
        try:
            dynamodb.create_table(
                TableName=CHAT_SESSIONS_TABLE,
                KeySchema=[
                    {'AttributeName': 'id', 'KeyType': 'HASH'}
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'id', 'AttributeType': 'S'},
                    {'AttributeName': 'session_id', 'AttributeType': 'S'}
                ],
                BillingMode='PAY_PER_REQUEST',
                GlobalSecondaryIndexes=[
                    {
                        'IndexName': 'session_id-index',
                        'KeySchema': [
                            {'AttributeName': 'session_id', 'KeyType': 'HASH'}
                        ],
                        'Projection': {'ProjectionType': 'ALL'}
                    }
                ]
            )
        except ClientError as e:
            if e.response['Error']['Code'] != 'ResourceInUseException':
                raise

        # Chat Messages Table
        try:
            dynamodb.create_table(
                TableName=CHAT_MESSAGES_TABLE,
                KeySchema=[
                    {'AttributeName': 'id', 'KeyType': 'HASH'}
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'id', 'AttributeType': 'S'},
                    {'AttributeName': 'chat_session_id', 'AttributeType': 'S'}
                ],
                BillingMode='PAY_PER_REQUEST',
                GlobalSecondaryIndexes=[
                    {
                        'IndexName': 'chat_session_id-index',
                        'KeySchema': [
                            {'AttributeName': 'chat_session_id', 'KeyType': 'HASH'}
                        ],
                        'Projection': {'ProjectionType': 'ALL'}
                    }
                ]
            )
        except ClientError as e:
            if e.response['Error']['Code'] != 'ResourceInUseException':
                raise

        # Plan Sessions Table
        try:
            dynamodb.create_table(
                TableName=PLAN_SESSIONS_TABLE,
                KeySchema=[
                    {'AttributeName': 'id', 'KeyType': 'HASH'}
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'id', 'AttributeType': 'S'},
                    {'AttributeName': 'chat_session_id', 'AttributeType': 'S'}
                ],
                BillingMode='PAY_PER_REQUEST',
                GlobalSecondaryIndexes=[
                    {
                        'IndexName': 'chat_session_id-index',
                        'KeySchema': [
                            {'AttributeName': 'chat_session_id', 'KeyType': 'HASH'}
                        ],
                        'Projection': {'ProjectionType': 'ALL'}
                    }
                ]
            )
        except ClientError as e:
            if e.response['Error']['Code'] != 'ResourceInUseException':
                raise

        print("✅ DynamoDB tables created successfully")

    except Exception as e:
        print(f"❌ Error creating DynamoDB tables: {str(e)}")
        raise

def clear_all_tables():
    """Clear all data from DynamoDB tables"""
    try:
        # Get table references
        user_memory_table = dynamodb.Table(USER_MEMORY_TABLE)
        chat_sessions_table = dynamodb.Table(CHAT_SESSIONS_TABLE)
        chat_messages_table = dynamodb.Table(CHAT_MESSAGES_TABLE)
        plan_sessions_table = dynamodb.Table(PLAN_SESSIONS_TABLE)
        
        tables = [
            (user_memory_table, "user_memory"),
            (chat_sessions_table, "chat_sessions"),
            (chat_messages_table, "chat_messages"),
            (plan_sessions_table, "plan_sessions")
        ]
        
        for table, table_name in tables:
            try:
                # Scan all items in the table
                response = table.scan()
                items = response.get('Items', [])
                
                # Delete all items
                with table.batch_writer() as batch:
                    for item in items:
                        batch.delete_item(Key={'id': item['id']})
                
                # Cleared items from table
                
            except Exception as e:
                print(f"❌ Error clearing {table_name} table: {str(e)}")
                
        print("🧹 Database cleanup completed")
        
    except Exception as e:
        print(f"❌ Error during database cleanup: {str(e)}")
        # Don't raise exception to avoid breaking startup

class DynamoDBSession:
    """Mock SQLAlchemy session for DynamoDB operations"""
    
    def __init__(self):
        self.user_memory_table = dynamodb.Table(USER_MEMORY_TABLE)
        self.chat_sessions_table = dynamodb.Table(CHAT_SESSIONS_TABLE)
        self.chat_messages_table = dynamodb.Table(CHAT_MESSAGES_TABLE)
        self.plan_sessions_table = dynamodb.Table(PLAN_SESSIONS_TABLE)

    def query(self, model_class):
        return DynamoDBQuery(model_class, self)

    def add(self, item):
        # Handle add operation based on item type
        if hasattr(item, '__tablename__'):
            table_name = item.__tablename__
            # Convert floats to Decimal for DynamoDB compatibility
            item_dict = convert_floats_to_decimal(item.to_dict())
            if table_name == 'user_memory':
                self.user_memory_table.put_item(Item=item_dict)
            elif table_name == 'chat_sessions':
                self.chat_sessions_table.put_item(Item=item_dict)
            elif table_name == 'chat_messages':
                self.chat_messages_table.put_item(Item=item_dict)
            elif table_name == 'plan_sessions':
                self.plan_sessions_table.put_item(Item=item_dict)

    def commit(self):
        pass  # DynamoDB operations are immediately consistent

    def rollback(self):
        pass  # Not needed for DynamoDB

    def close(self):
        pass  # Not needed for DynamoDB

class DynamoDBQuery:
    """Mock SQLAlchemy query for DynamoDB"""
    
    def __init__(self, model_class, session):
        self.model_class = model_class
        self.session = session
        self.filters = {}
        self.limit_count = None
        self.order_field = None
        self.order_desc = False

    def filter(self, condition):
        # Simple filter implementation
        if hasattr(condition, 'left') and hasattr(condition, 'right'):
            field = condition.left.name
            value = condition.right.value
            self.filters[field] = value
        elif isinstance(condition, dict):
            self.filters.update(condition)
        return self

    def first(self):
        results = self._execute_query()
        return results[0] if results else None

    def all(self):
        return self._execute_query()

    def limit(self, count):
        self.limit_count = count
        return self

    def order_by(self, field):
        if hasattr(field, 'desc'):
            self.order_field = field.expression.name
            self.order_desc = True
        else:
            self.order_field = field.name
            self.order_desc = False
        return self

    def _execute_query(self):
        table_name = self.model_class.__tablename__
        
        if table_name == 'user_memory':
            return self._query_user_memory()
        elif table_name == 'chat_sessions':
            return self._query_chat_sessions()
        elif table_name == 'chat_messages':
            return self._query_chat_messages()
        elif table_name == 'plan_sessions':
            return self._query_plan_sessions()
        
        return []

    def _query_user_memory(self):
        try:
            if 'user_session' in self.filters:
                response = self.session.user_memory_table.query(
                    IndexName='user_session-index',
                    KeyConditionExpression='user_session = :us',
                    ExpressionAttributeValues={':us': self.filters['user_session']}
                )
                return [UserMemory.from_dict(item) for item in response['Items']]
            else:
                response = self.session.user_memory_table.scan()
                return [UserMemory.from_dict(item) for item in response['Items']]
        except Exception as e:
            # Error querying user memory
            return []

    def _query_chat_sessions(self):
        try:
            if 'session_id' in self.filters:
                response = self.session.chat_sessions_table.query(
                    IndexName='session_id-index',
                    KeyConditionExpression='session_id = :sid',
                    ExpressionAttributeValues={':sid': self.filters['session_id']}
                )
                return [ChatSession.from_dict(item) for item in response['Items']]
            else:
                response = self.session.chat_sessions_table.scan()
                return [ChatSession.from_dict(item) for item in response['Items']]
        except Exception as e:
            # Error querying chat sessions
            return []

    def _query_chat_messages(self):
        try:
            if 'chat_session_id' in self.filters:
                response = self.session.chat_messages_table.query(
                    IndexName='chat_session_id-index',
                    KeyConditionExpression='chat_session_id = :csid',
                    ExpressionAttributeValues={':csid': self.filters['chat_session_id']}
                )
                return [ChatMessage.from_dict(item) for item in response['Items']]
            else:
                response = self.session.chat_messages_table.scan()
                return [ChatMessage.from_dict(item) for item in response['Items']]
        except Exception as e:
            # Error querying chat messages
            return []

    def _query_plan_sessions(self):
        try:
            if 'chat_session_id' in self.filters:
                response = self.session.plan_sessions_table.query(
                    IndexName='chat_session_id-index',
                    KeyConditionExpression='chat_session_id = :csid',
                    ExpressionAttributeValues={':csid': self.filters['chat_session_id']}
                )
                return [PlanSession.from_dict(item) for item in response['Items']]
            else:
                response = self.session.plan_sessions_table.scan()
                return [PlanSession.from_dict(item) for item in response['Items']]
        except Exception as e:
            # Error querying plan sessions
            return []

def get_db():
    """Get DynamoDB session (mock SQLAlchemy dependency)"""
    db = DynamoDBSession()
    try:
        yield db
    finally:
        db.close()

# Model classes for DynamoDB
class UserMemory:
    __tablename__ = 'user_memory'
    
    def __init__(self, id=None, user_session=None, preference_type=None, preference_value=None, 
                 confidence_score=1.0, context=None, created_at=None, updated_at=None):
        self.id = id or str(uuid.uuid4())
        self.user_session = user_session
        self.preference_type = preference_type
        self.preference_value = preference_value
        self.confidence_score = confidence_score
        self.context = context or {}
        self.created_at = created_at or datetime.utcnow().isoformat()
        self.updated_at = updated_at or datetime.utcnow().isoformat()

    def to_dict(self):
        return {
            'id': self.id,
            'user_session': self.user_session,
            'preference_type': self.preference_type,
            'preference_value': self.preference_value,
            'confidence_score': self.confidence_score,
            'context': self.context,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class ChatSession:
    __tablename__ = 'chat_sessions'
    
    def __init__(self, id=None, session_id=None, event_context=None, user_session=None, created_at=None):
        self.id = id or str(uuid.uuid4())
        self.session_id = session_id
        self.event_context = event_context or {}
        self.user_session = user_session
        self.created_at = created_at or datetime.utcnow().isoformat()

    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'event_context': self.event_context,
            'user_session': self.user_session,
            'created_at': self.created_at
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class ChatMessage:
    __tablename__ = 'chat_messages'
    
    def __init__(self, id=None, chat_session_id=None, content=None, role=None, 
                 ai_suggestions=None, timestamp=None, **kwargs):
        self.id = id or str(uuid.uuid4())
        self.chat_session_id = chat_session_id
        self.content = content
        self.role = role
        self.ai_suggestions = ai_suggestions or {}
        self.timestamp = timestamp or datetime.utcnow()

    def to_dict(self):
        return {
            'id': self.id,
            'chat_session_id': self.chat_session_id,
            'content': self.content,
            'role': self.role,
            'ai_suggestions': self.ai_suggestions,
            'timestamp': self.timestamp.isoformat() if isinstance(self.timestamp, datetime) else self.timestamp
        }

    @classmethod
    def from_dict(cls, data):
        # Convert timestamp string back to datetime if needed
        if isinstance(data.get('timestamp'), str):
            try:
                data['timestamp'] = datetime.fromisoformat(data['timestamp'])
            except:
                data['timestamp'] = datetime.utcnow()
        return cls(**data)

class PlanSession:
    __tablename__ = 'plan_sessions'
    
    def __init__(self, id=None, chat_session_id=None, plan_status="discovering", 
                 satisfaction_score=0.0, completion_confidence=0.0, user_goals=None, 
                 generated_content=None, refinement_history=None, created_at=None, 
                 last_state_change=None, **kwargs):
        self.id = id or str(uuid.uuid4())
        self.chat_session_id = chat_session_id
        self.plan_status = plan_status
        self.satisfaction_score = satisfaction_score
        self.completion_confidence = completion_confidence
        self.user_goals = user_goals or {}
        self.generated_content = generated_content or {}
        self.refinement_history = refinement_history or []
        self.created_at = created_at or datetime.utcnow().isoformat()
        self.last_state_change = last_state_change or datetime.utcnow().isoformat()

    def to_dict(self):
        return {
            'id': self.id,
            'chat_session_id': self.chat_session_id,
            'plan_status': self.plan_status,
            'satisfaction_score': self.satisfaction_score,
            'completion_confidence': self.completion_confidence,
            'user_goals': self.user_goals,
            'generated_content': self.generated_content,
            'refinement_history': self.refinement_history,
            'created_at': self.created_at,
            'last_state_change': self.last_state_change
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

# Helper functions for user memory
def store_user_preference(db, user_session: str, pref_type: str, pref_value: str, confidence: float = 1.0, context: dict = None):
    """Store or update a user preference"""
    # Check if preference already exists
    existing = db.query(UserMemory).filter({
        'user_session': user_session,
        'preference_type': pref_type,
        'preference_value': pref_value
    }).first()
    
    if existing:
        # Update confidence score (weighted average)
        existing.confidence_score = (existing.confidence_score + confidence) / 2
        existing.updated_at = datetime.utcnow().isoformat()
        if context:
            existing.context = context
        db.add(existing)
    else:
        # Create new preference
        new_pref = UserMemory(
            user_session=user_session,
            preference_type=pref_type,
            preference_value=pref_value,
            confidence_score=confidence,
            context=context
        )
        db.add(new_pref)
    
    db.commit()

def get_user_preferences(db, user_session: str, pref_type: str = None):
    """Retrieve user preferences, optionally filtered by type"""
    query = db.query(UserMemory).filter({'user_session': user_session})
    
    if pref_type:
        query = query.filter({'preference_type': pref_type})
    
    return query.all()

# Plan management functions
def get_or_create_plan_session(db, chat_session_id: str):
    """Get existing plan session or create new one"""
    plan_session = db.query(PlanSession).filter({'chat_session_id': chat_session_id}).first()
    
    if not plan_session:
        plan_session = PlanSession(
            chat_session_id=chat_session_id,
            plan_status="discovering",
            user_goals={},
            generated_content={},
            refinement_history=[]
        )
        db.add(plan_session)
        db.commit()
    
    return plan_session

def update_plan_state(db, plan_session, new_status: str, **kwargs):
    """Update plan session state with additional data"""
    plan_session.plan_status = new_status
    plan_session.last_state_change = datetime.utcnow().isoformat()
    
    # Update optional fields
    if 'satisfaction_score' in kwargs:
        plan_session.satisfaction_score = kwargs['satisfaction_score']
    if 'completion_confidence' in kwargs:
        plan_session.completion_confidence = kwargs['completion_confidence']
    if 'user_goals' in kwargs:
        plan_session.user_goals = kwargs['user_goals']
    if 'generated_content' in kwargs:
        plan_session.generated_content = kwargs['generated_content']
    if 'refinement_history' in kwargs:
        plan_session.refinement_history = kwargs['refinement_history']
    
    db.add(plan_session)
    db.commit()
    return plan_session

def get_plan_progress(db, chat_session_id: str):
    """Get plan progress summary"""
    plan_session = db.query(PlanSession).filter({'chat_session_id': chat_session_id}).first()
    
    if not plan_session:
        return {"status": "not_started", "progress": 0.0}
    
    # Calculate progress percentage
    progress_map = {
        "discovering": 0.1,
        "planning": 0.3,
        "generating": 0.6,
        "reviewing": 0.8,
        "refining": 0.9,
        "completed": 1.0
    }
    
    return {
        "status": plan_session.plan_status,
        "progress": progress_map.get(plan_session.plan_status, 0.0),
        "satisfaction": plan_session.satisfaction_score,
        "confidence": plan_session.completion_confidence,
        "description": f"Plan is in {plan_session.plan_status} state"
    }