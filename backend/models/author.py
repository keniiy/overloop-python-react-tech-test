from sqlalchemy import Column, Integer, String
from connector import BaseModel


class Author(BaseModel):
    __tablename__ = 'author'

    id = Column(
        Integer,
        name='id',
        nullable=False,
        primary_key=True,
        autoincrement=True
    )

    first_name = Column(
        String(100),
        name='first_name',
        nullable=False
    )

    last_name = Column(
        String(100),
        name='last_name',
        nullable=False
    )

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def __str__(self):
        return f"Author(id={self.id}, name='{self.full_name}')"
    
    def serialize(self):
        """Serialize model to dictionary"""
        data = self.asdict()
        data['full_name'] = self.full_name
        return data