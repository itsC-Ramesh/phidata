"""
pip install fal-client
"""

from os import getenv
from typing import Optional

from phi.agent import Agent
from phi.tools import Toolkit
from phi.utils.log import logger
from phi.model.content import Video, Image
from enum import Enum
from uuid import uuid4


try:
    import fal_client  # type: ignore
except ImportError:
    raise ImportError("`fal_client` not installed. Please install using `pip install fal-client`")


class ModelType(str, Enum):
    IMAGE = "image"
    VIDEO = "video"
    TEXT = "text"


class FalTools(Toolkit):
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "fal-ai/hunyuan-video",
        type: ModelType = ModelType.VIDEO,
    ):
        super().__init__(name="fal")

        self.api_key = api_key or getenv("FAL_API_KEY")
        self.model = model
        self.type = type
        if not self.api_key:
            logger.error("FAL_API_KEY not set. Please set the FAL_API_KEY environment variable.")
        self.seen_logs: set[str] = set()
        self.register(self.generate_media)

    def on_queue_update(self, update):
        if isinstance(update, fal_client.InProgress) and update.logs:
            for log in update.logs:
                message = log["message"]
                if message not in self.seen_logs:
                    logger.info(message)
                    self.seen_logs.add(message)

    def generate_media(
        self, agent: Agent, prompt: str, model: Optional[str] = None, type: Optional[ModelType] = None
    ) -> str:
        """
        Use this function to run a model with a given prompt.

        Args:
            prompt (str): A text description of the task.
            model (str): The model to use.
            type (ModelType): The type of the model to use. It can be either `image` or `video` or `text`.
        Returns:
            str: Return the result of the model.
        """
        try:
            data = []
            result = fal_client.subscribe(
                model or self.model,
                arguments={"prompt": prompt},
                with_logs=True,
                on_queue_update=self.on_queue_update,
            )
            if type == ModelType.VIDEO:
                video_url = result.get("video", {}).get("url", "")
                data.append({"url": video_url})
                agent.add_video(Video(id=str(uuid4()), url=video_url))
                return f"Media generated successfully at {video_url}"
            elif type == ModelType.IMAGE:
                image_url = result.get("image", {}).get("url", "")
                data.append({"url": image_url})
                agent.add_image(Image(id=str(uuid4()), url=image_url))
                return f"Media generated successfully at {image_url}"
            else:
                raise Exception("Model not supported")
        except Exception as e:
            logger.error(f"Failed to run model: {e}")
            return f"Error: {e}"