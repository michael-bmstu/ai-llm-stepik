import json
from datetime import datetime
import chainlit as cl
from chainlit import PersistedUser, User
from chainlit.data import BaseDataLayer
from chainlit.element import ElementDict
from chainlit.step import StepDict
from chainlit.types import Feedback, ThreadDict, Pagination, ThreadFilter, PaginatedResponse, PageInfo


class CustomDataLayer(BaseDataLayer):
    async def build_debug_url(self) -> str:
        return ""
    
    def __init__(self):
        self.users = dict[str, PersistedUser] = {}
        self.threads = dict[str, ThreadDict] = {}
        self.elements = dict[str, ElementDict] = {}
        self.steps = dict[str, StepDict] = {}
        self.feedback = dict[str, Feedback] = {}
    
    async def get_user(self, identifier: str) -> PersistedUser | None:
        return self.users.get(identifier)
    
    async def create_user(self, user) -> PersistedUser:
        persisted_user = PersistedUser(**user.__dict__, id=user.identifier, createdAt=datetime.now().date().strftime("%Y-%m-%d"))
        self.users[user.identifier] = persisted_user
        return persisted_user
    
    async def upsert_feedback(self, feedback) -> str:
        self.feedback[feedback.id] = feedback
        return feedback.id

    async def delete_feedback(self, feedback_id) -> bool:
        if feedback_id in self.feedback:
            del self.feedback[feedback_id]
            return True
        return False
    
    async def create_element(self, element_dict: ElementDict) -> None:
        self.elements[element_dict["id"]] = element_dict
    
    async def get_element(self, thread_id: str, element_id: str) -> ElementDict | None:
        return self.elements.get(element_id)
    
    async def delete_element(self, element_id:str, thread_id: str|None = None) -> None:
        if element_id in self.elements:
            del self.elements[element_id]

    async def create_step(self, step_dict: StepDict) -> None:
        self.steps[step_dict["id"]] = step_dict

    async def update_step(self, step_dict: StepDict) -> None:
        self.steps[step_dict["id"]] = step_dict

    async def delete_step(self, step_id: str) -> None:
        if step_id in self.steps:
            del self.steps[step_id]
    
    async def get_thread_author(self, thread_id: str) -> str:
        if thread_id in self.threads:
            author = self.threads[thread_id]["userId"]
        else:
            author = "Unknown"
        return author

    async def delete_thread(self, thread_id: str) -> None:
        if thread_id in self.threads:
            del self.threads[thread_id]