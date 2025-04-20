from fastapi import APIRouter
from starlette.requests import Request

from src.core.log import logger
from src.core.settings import settings
from src.core.util import CatState
from src.llm.ollama_util import init_ollama_llm

router = APIRouter()


@logger.catch
@router.get(
    "/llm/model",
    tags=['llm'],
    summary="Show model name",
    description="Ollama. Show model name",
)
async def get_model(
        request: Request,
):
    result: dict = {
        'settings.llm_model': settings.llm_model,
        'settings.llm_url': settings.llm_url,
    }
    return result


@logger.catch
@router.put(
    "/llm/model",
    tags=['llm'],
    summary="Change llm model",
    description="Ollama. Change model",
)
async def set_model(
        request: Request,
        llm_model: str,
):
    logger.info(msg := f"Setting  llm model: {llm_model} ...")
    previous_model: str = settings.llm_model
    settings.llm_model = llm_model
    cat_state: CatState = request.app.state.cat
    cat_state.llm_client = init_ollama_llm()

    result: dict = {
        'llm_client.model': cat_state.llm_client.model,
        'settings.llm_model': settings.llm_model,
        'settings.llm_url': settings.llm_url,
        'previous_llm_model': previous_model,
    }
    logger.info(f"{msg} done")
    return result


@logger.catch
@router.get(
    "/llm/prompt",
    tags=['llm'],
    summary="Show prompt",
    description="Ollama. Show current prompt",
)
async def get_model(
        request: Request,
):
    return settings.llm_prompt_template


@logger.catch
@router.put(
    "/llm/prompt",
    tags=['llm'],
    summary="Change llm prompt",
    description="Change prompt template",
)
async def set_prompt(
        request: Request,
        prompt_template: str,
):
    logger.info(msg := f"Setting prompt template: {prompt_template} ...")
    previous_prompt: str = settings.llm_prompt_template
    settings.llm_prompt_template = prompt_template

    result: dict = {
        'settings.llm_prompt_template': settings.llm_prompt_template,
        'previous_prompt_template': previous_prompt,
    }
    logger.info(f"{msg} done")
    return result

