from sqlalchemy import Column, Integer, String, ForeignKey, Text

from app.db.session import Base


class FlowStep(Base):
    __tablename__ = "flow_steps"

    id = Column(Integer, primary_key=True, index=True)
    flow_id = Column(Integer, ForeignKey("flows.id"), nullable=False, index=True)
    order_index = Column(Integer, nullable=False)
    type = Column(String(100), nullable=False)  # message, wait, etc.
    config = Column(Text, nullable=True)  # JSON string
