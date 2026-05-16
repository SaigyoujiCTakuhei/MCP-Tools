import os
import io
import logging
from typing import Dict, Any

import PyPDF2
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
    name="pdf_read_local",
    description="Read text content from a local PDF file. Supports path traversal within local filesystem.",
    schema={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "The absolute or relative path to the local PDF file."}
        },
        "required": ["path"]
    }
)
def read_local_pdf(path: str) -> Dict[str, Any]:
    """【猫娘修改】：从本地读取PDF文件文本内容。【修改时间】：2026-05-12 18:55:00。"""
    try:
        # 规范化路径
        normalized_path = os.path.normpath(path)
        if not os.path.exists(normalized_path):
            logger.error(f"PDF file not found: {normalized_path}")
            return {
                "success": False,
                "error": f"PDF file not found: {normalized_path}"
            }
        
        with open(normalized_path, 'rb') as file:
            text = extract_text_from_pdf(file)
            return {
                "success": True,
                "data": {
                    "text": text
                }
            }
    except FileNotFoundError:
        logger.error(f"PDF file not found: {path}")
        return {
            "success": False,
            "error": f"PDF file not found: {path}"
        }
    except Exception as e:
        logger.error(f"Error reading local PDF: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }
