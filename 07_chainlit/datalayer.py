import json
from datetime import datetime
from chainlit import PersistedUser
from chainlit.data import BaseDataLayer
from chainlit.element import ElementDict
from chainlit.step import StepDict
from chainlit.types import Feedback, ThreadDict, Pagination, ThreadFilter, PaginatedResponse, PageInfo

# Study only! Dosen't work corrcectly
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

    async def list_threads(self, pagination: Pagination, filters: ThreadFilter) -> PaginatedResponse[ThreadDict]:
        if not filters.userId:
            raise ValueError("userId is required")
        threads = [t for t in list(self.threads.values()) if t["userId"] == filters.userId]
        start = 0
        if pagination.cursor:
            for i, thread in enumerate(threads):
                if thread["id"] == pagination.cursor:
                    start = i + 1
                    break
        end = start + pagination.first
        paginated_threads = threads[start:end] or []
        has_next_page = len(threads) > end
        start_cursor = paginated_threads[0]["id"] if paginated_threads else None
        end_cursor = paginated_threads[-1]["id"] if paginated_threads else None

        result = PaginatedResponse(
            pageInfo=PageInfo(hasNextPage=has_next_page, startCursor=start_cursor, endCursor=end_cursor),
            data=paginated_threads
        )
        return result
    
    async def get_thread(self, thread_id: str) -> ThreadDict | None:
        thread = self.threads.get(thread_id)
        thread["steps"] = [st for st in self.steps.values() if st["threadId"] == thread_id]
        thread["elements"] = [el for el in self.elements.values() if el["threadId"] == thread_id]
        return thread
    
    async def update_thread(self, thread_id: str, name: str|None = None, user_id: str|None = None, metadata: dict|None = None, tags: list[str]|None = None):
        if thread_id in self.threads:
            if name:
                self.threads[thread_id]["name"] = name
            if user_id:
                self.threads[thread_id]["userId"] = user_id
            if metadata:
                self.threads[thread_id]["metadata"] = metadata
            if tags:
                self.threads[thread_id]["tags"] = tags
        else:
            data = {
                "id": thread_id,
                "createdAt": (
                    datetime.now().isoformat() + "Z" if metadata is None else None
                ),
                "name": (
                    name
                    if name is not None
                    else (metadata.get("name") if metadata and "name" in metadata else None)
                ),
                "userId": user_id,
                "userIdentifier": user_id,
                "tags": tags,
                "metadata": json.dumps(metadata) if metadata else None,
            }
            self.threads[thread_id] = data