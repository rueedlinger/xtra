import binascii
import logging.config
import os
from typing import Any, List

import yaml
from fastapi import FastAPI, UploadFile, Request
from fastapi.openapi.utils import get_openapi
from starlette.responses import JSONResponse

from xtra.model import TextExtract, TableExtract
from xtra.pdf import PdfTextExtractor, PdfTableExtractor, PdfOcrExtractor, PdfMetaDataExtractor

app = FastAPI()

log_conf_file = "log_conf.yaml"
if 'XTRA_LOG_CONF' in os.environ:
    log_conf_file = os.environ['XTRA_LOG_CONF']

with open(log_conf_file, 'rt') as f:
    config = yaml.safe_load(f.read())
logging.config.dictConfig(config)

# get root logger
logger = logging.getLogger("xtra.api")


@app.exception_handler(binascii.Error)
async def unicorn_exception_handler(request: Request, ex: binascii.Error):
    return JSONResponse(
        status_code=400,
        content={"message": f"bas46 error, {ex}"},
    )


@app.exception_handler(Exception)
async def unicorn_exception_handler(request: Request, ex: binascii.Error):
    return JSONResponse(
        status_code=500,
        content={"message": f"{ex}"},
    )


"""
@app.get("/")
async def redirect_typer():
    return RedirectResponse("/docs")
"""


@app.post("/pdf/text", response_model=List[TextExtract])
async def extract_text_from_pdf(
        file: UploadFile,
) -> Any:
    logger.debug(f"extract text from pdf file='{file.filename}'")
    pdf = PdfTextExtractor()
    return pdf.extract_text(data=await file.read())


@app.post("/pdf/ocr", response_model=List[TextExtract])
async def extract_text_with_ocr_from_pdf(
        file: UploadFile,
) -> Any:
    logger.debug(f"extract text with ocr from pdf file='{file.filename}'")
    pdf = PdfOcrExtractor()
    return pdf.extract_text(data=await file.read())


@app.post("/pdf/table", response_model=List[TableExtract])
async def extract_table_from_pdf(
        file: UploadFile,
) -> Any:
    logger.debug(f"extract table from pdf file='{file.filename}'")
    pdf = PdfTableExtractor()
    return pdf.extract_table(data=await file.read())


@app.post("/pdf/meta", response_model=List[dict])
async def extract_meta_data_from_pdf(
        file: UploadFile,
) -> Any:
    logger.debug(f"extract meta data from pdf file='{file.filename}'")
    pdf = PdfMetaDataExtractor()
    return pdf.extract_metadata(data=await file.read())


"""

@app.post("/base64/encode", response_model=Document)
async def encode_file_to_base64(file: UploadFile) -> Any:
    logger.debug(
        f"base64 encode: filename='{file.filename}', size='{file.size}', content_type='{file.content_type}'"
    )
    b64 = Base64()
    return b64.encode(data=await file.read(), filename=file.filename)
"""


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="xtra",
        version="0.1.0",
        summary="API's for extracting structured data and convert PDF files",
        description="Here's a longer description of the custom **OpenAPI** schema",
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
