import io
import logging
from typing import Dict, Any

import PyPDF2
import requests
from Lib.base.base import tool

def get_logger(name: str):
    """【猫娘修改】：获取日志记录器。【修改时间】：2026-05-12 18:55:00。"""
    logger = logging.getLogger(name)
    return logger

logger = get_logger(__name__)

def extract_text_from_pdf(pdf_file) -> str:
    """【猫娘修改】：从PDF文件对象中提取文本内容。【修改时间】：2026-05-12 18:55:00。"""
    try:
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        logger.error(f"Failed to extract text from PDF: {str(e)}")
        raise ValueError(f"Failed to extract text from PDF: {str(e)}")

@tool(
    name="pdf_read_url",
    description="Read text content from a PDF URL. Downloads the PDF to memory and extracts text.",
    schema={
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "The URL of the PDF file to download and read."}
        },
        "required": ["url"]
    }
)
def read_pdf_url(url: str) -> Dict[str, Any]:
    """【猫娘修改】：从URL读取PDF文件文本内容。【修改时间】：2026-05-12 18:55:00。"""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        if 'application/pdf' not in response.headers.get('Content-Type', '').lower():
            return {
                "success": False,
                "error": f"URL does not point to a PDF file. Content-Type: {response.headers.get('Content-Type')}"
            }

        pdf_file = io.BytesIO(response.content)
        text = extract_text_from_pdf(pdf_file)
        return {
            "success": True,
            "data": {
                "text": text
            }
        }
    except requests.RequestException as e:
        logger.error(f"Failed to fetch PDF from URL: {str(e)}")
        return {
            "success": False,
            "error": f"Failed to fetch PDF from URL: {str(e)}"
        }
    except Exception as e:
        logger.error(f"Error processing PDF from URL: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }
