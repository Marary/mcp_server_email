import os
import pytz
import resend
from enum import Enum
from datetime import datetime, timedelta
from typing import Sequence
import json

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
from mcp.shared.exceptions import McpError

## Resend API Documentation: https://resend.com/docs/api-reference/emails/send-email

# 用于调试Server的日志文件
LOG_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), "mcp_email.log")
log_file = open(LOG_FILE, 'w', encoding='utf-8')

def write_log(message: str):
    """Write log to file"""
    log_file.write(f"{message}\n")
    log_file.flush()  # Ensure log is written promptly

"""Enum for email tools"""
class EmailTools(str, Enum):
    """
    :SEND_EMAIL : 发送邮件，指定收件人、主题和正文，可以设置延迟发送，可以设置抄送和密件抄送
    :MASS_EMAILING : 批量发送邮件，指定收件人列表、主题和正文，可以设置延迟发送
    :GET_EMAIL : 获取邮件信息，需要提供邮件ID
    :UPDATE_EMAIL : 更新邮件信息，需要提供邮件ID和更新的内容
    :CANCEL_EMAIL : 取消邮件发送，需要提供邮件ID，并且该邮件是延迟发送的
    """
    SEND_EMAIL = "send_email"
    MASS_EMAILING = "mass_emailing"
    GET_EMAIL = "get_email"
    UPDATE_EMAIL = "update_email"
    CANCEL_EMAIL = "cancel_email"


"""Convert time to format"""
def convert_time_to_format(time: str | None) -> str:
    """Converts the given time string to ISO 8601 format.
    Args:
        time (str | None): The time string in the format "YYYY-MM-DDTHH:MM:SS.ssssss".
    Returns:
        str: The time in ISO 8601 format, or the current time if the input time is None or invalid.
    Raises:
        ValueError: If the input time string is not in the correct format.
    """
    format = "%Y-%m-%dT%H:%M:%S.%f"
    try:
        # 获取当前时间的 ISO 8601 格式
        now = datetime.now().isoformat()
        # 加上5秒钟的延迟 因为就算是当前发送，也要考虑程序处理时间和请求时间
        now = (datetime.fromisoformat(now) + timedelta(seconds=10)).isoformat()
        if time is not None:
            # 确保 scheduled_at 是字符串类型
            if not isinstance(time, str):
                raise ValueError("The `scheduled_at` field must be a `string`.")
            
            # 将输入时间字符串转换为 datetime 对象
            timer = datetime.strptime(time, format).isoformat()
        else:
            # 如果没有提供时间，则使用当前时间
            timer = now
        
        # 如果输入时间小于当前时间，则使用当前时间
        if timer <= now:
            timer = now
            

        # 将时间转换为 UTC 时区
        local_tz = pytz.timezone("Asia/Shanghai")
        local_time = local_tz.localize(datetime.fromisoformat(timer))
        timer = local_time.astimezone(pytz.utc).isoformat()

    except ValueError as e:
        raise ValueError("Invalid time format. Expected YYYY-MM-DDTHH:MM:SS.ssssss") from e
    
    return timer

# 将字典转为字符串
def dict_to_str(d):
    return "\n".join([f"{key}: {value}" for key, value in d.items()])

def send_email(api_key:str, domain:str, to_email:str, subject:str, body:str, scheduled:str | None = None, cc:list[str] | None = None, bcc:list[str] | None = None):
    # 设置 Resend API Key
    resend.api_key = api_key

    # 检查 API Key 是否已设置
    if resend.api_key is None:
        raise McpError("RESEND_API_KEY is not set. Please provide a valid API Key.")

    if scheduled is not None:
        scheduled_at = convert_time_to_format(scheduled)
    else:
        scheduled_at = ""
   
    if cc is None:
        cc = []
    if bcc is None:
        bcc = []
    # 邮件参数
    params = {
        "from": domain, # 域名
        "to": [to_email],  # 确保收件人邮箱是有效的
        "subject": subject, # 主题
        "html": body, # 正文
        "scheduled_at": scheduled_at, # 延迟发送时间
        "cc": cc, # 抄送
        "bcc": bcc, # 密件抄送
    }

    try:
        result = resend.Emails.send(params)
        return result
    except Exception as e:  # 捕获所有异常
        raise McpError(f"Failed to send email: {e}")

def mass_sending(api_key:str, domain:str, to_email_list:list[str], subject:str, body:str, scheduled:str | None = None):
    # 设置 Resend API Key
    resend.api_key = api_key

    # 检查 API Key 是否已设置
    if resend.api_key is None:
        raise McpError("RESEND_API_KEY is not set. Please provide a valid API Key.")
    
    if scheduled is not None:
        scheduled_at = convert_time_to_format(scheduled)
    else:
        scheduled_at = ""

    # 邮件参数
    params = []

    for to_email in to_email_list:
        params.append({
            "from": domain,  # 确保这是一个有效的发件人邮箱
            "to": [to_email],  # 确保收件人邮箱是有效的
            "subject": subject,
            "html": body,
            "scheduled_at": scheduled_at,
        })
    
    try:
        result = resend.Batch.send(params)
        return result
    except Exception as e:  # 捕获所有异常
        raise McpError(f"Failed to send emails: {e}")
    
def get_email(api_key:str, email_id:str):
    # 设置 Resend API Key
    resend.api_key = api_key

    # 检查 API Key 是否已设置
    if resend.api_key is None:
        raise McpError("RESEND_API_KEY is not set. Please provide a valid API Key.")

    # 获取邮件信息
    try:
        result = resend.Emails.get(email_id)
        return result
    except Exception as e:  # 捕获所有异常
        raise McpError(f"Failed to get email: {e}")
    
def update_email(api_key:str, email_id:str, scheduled:str | None = None):
    # 设置 Resend API Key
    resend.api_key = api_key

    # 检查 API Key 是否已设置
    if resend.api_key is None:
        raise McpError("RESEND_API_KEY is not set. Please provide a valid API Key.")
    
    
    scheduled_at = convert_time_to_format(scheduled)

    # 查找不为 None 的参数
    params = {}
    params["id"] = email_id
    
    params["scheduled_at"] = scheduled_at

    try:
        result = resend.Emails.update(params)
        return result
    except Exception as e:  # 捕获所有异常
        raise McpError(f"Failed to update email: {e}")
    
def cancel_email(api_key:str, email_id:str):
    # 设置 Resend API Key
    resend.api_key = api_key

    # 检查 API Key 是否已设置
    if resend.api_key is None:
        raise McpError("RESEND_API_KEY is not set. Please provide a valid API Key.")

    # 取消邮件发送
    try:
        result = resend.Emails.cancel(email_id)
        return result
    except Exception as e:  # 捕获所有异常
        raise McpError(f"Failed to cancel email: {e}")


async def serve(api_key:str, domain:str):
    server = Server("mcp-email")

    @server.list_tools()
    async def lsit_tools() -> list[Tool]:
        """列出所有工具"""
        return [
            Tool(
                name=EmailTools.SEND_EMAIL.value,
                description="Send an email to a recipient with subject and body. You can set delay, cc and bcc.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "to_email": {
                            "type": "string",
                            "description": "Recipient email address.If not provided, the email will be not sent.",
                        },
                        "subject": {
                            "type": "string",
                            "description": "Email subject.Use this to set the subject of the email.If not provided, the email will be not sent.",
                        },
                        "body": {
                            "type": "string",
                            "description": "Email body.Use this to set the body of the email.If not provided, the email will be not sent.",
                        },
                        "scheduled_at": {
                            "type": "string",
                            "description": (
                                'Time is when the email will be sent. If not provided, the email will be sent immediately.Time format is "%Y-%m-%dT%H:%M:%S.%f".'      
                            ),
                        },
                        "cc": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": (
                                'List of CC email addresses. If not provided, no CC will be added.'
                            ),
                        },
                        "bcc": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": (
                                'List of BCC email addresses. If not provided, no BCC will be added.'
                            ),
                        },
                    },
                    "required": ["to_email", "subject", "body"],
                },
            ),
            Tool(
                name=EmailTools.MASS_EMAILING.value,
                description="Send an email to a list of recipients with subject and body. You can set delay.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "to_email_list": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": (
                                'List of recipient email addresses. If not provided, the email will be not sent.'
                            ),
                        },
                        "subject": {
                            "type": "string",
                            "description": (
                                'Email subject. Use this to set the subject of the email. If not provided, the email will be not sent.'
                            ),
                        },
                        "body": {
                            "type": "string",
                            "description": (
                                'Email body. Use this to set the body of the email. If not provided, the email will be not sent.'
                            ),
                        },
                        "scheduled_at": {
                            "type": "string",
                            "description": (
                                'Time is when the email will be sent. If not provided, the email will be sent immediately.format = "%Y-%m-%dT%H:%M:%S.%f".'
                            ),
                        },
                    },
                    "required": ["to_email_list", "subject", "body"],
                },
            ),
            Tool(
                name=EmailTools.GET_EMAIL.value,
                description="Get email information by email ID.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "email_id": {
                            "type": "string",
                            "description": (
                                'Email ID. Use this to get the email information. If not provided, you will not get the email information.'
                            ),
                        },
                    },
                    "required": ["email_id"],
                },
            ),
            Tool(
                name=EmailTools.UPDATE_EMAIL.value,
                description="Update email information by email ID.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "email_id": {
                            "type": "string",
                            "description": (
                                'Email ID. Use this to update the email information. If not provided, you will not update the email.'
                            ),
                        },
                        "scheduled_at": {
                            "type": "string",
                            "description": (
                                'Time is when the email will be sent. If not provided, the email scheduled_at will not update, use None.None means send immediately.'
                            ),
                        },
                    },
                    "required": ["email_id", "scheduled_at"],
                },
            ),
            Tool(
                name=EmailTools.CANCEL_EMAIL.value,
                description="Cancel email by email ID.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "email_id": {
                            "type": "string",
                            "description": (
                                'Email ID. Use this to cancel the email. If not provided, you will not cancel the email.'
                            ),
                        },
                    },
                    "required": ["email_id"],
                },

            )
        ]
    @server.call_tool()
    async def call_tool(
        name : str, arguments : dict
    ) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        """处理工具调用"""
        result = None
        try:
            match name:
                case EmailTools.SEND_EMAIL.value:
                    to_email = arguments.get("to_email")
                    subject = arguments.get("subject")
                    body = arguments.get("body")
                    scheduled_at = None
                    cc = []
                    bcc = []
                    if "scheduled_at" in arguments:
                        scheduled_at = arguments.get("scheduled_at")
                    if "cc" in arguments:
                        cc = arguments.get("cc")
                    if "bcc" in arguments:
                        bcc = arguments.get("bcc")

                    # 检查参数是否有效
                    if not to_email or not subject or not body:
                        raise ValueError("Invalid parameters. Please provide valid email parameters.")
                    # 调用发送邮件函数
                    result = send_email(api_key, domain, to_email, subject, body, scheduled_at, cc, bcc)
                    
                case EmailTools.MASS_EMAILING.value:
                    to_email_list = arguments.get("to_email_list")
                    subject = arguments.get("subject")
                    body = arguments.get("body")
                    scheduled_at = None
                    if "scheduled_at" in arguments:
                        scheduled_at = arguments.get("scheduled_at")

                    # 检查参数是否有效
                    if not to_email_list or not subject or not body:
                        raise ValueError("Invalid parameters. Please provide valid email parameters.")

                    # 调用批量发送邮件函数
                    result = mass_sending(api_key, domain, to_email_list, subject, body, scheduled_at)

                case EmailTools.GET_EMAIL.value:
                    email_id = arguments.get("email_id")

                    # 检查参数是否有效
                    if not email_id:
                        raise ValueError("Invalid parameters. Please provide valid email ID.")

                    # 调用获取邮件函数
                    result = get_email(api_key, email_id)

                case EmailTools.UPDATE_EMAIL.value:
                    email_id = arguments.get("email_id")
                    scheduled_at = None

                    if "scheduled_at" in arguments:
                        scheduled_at = arguments.get("scheduled_at")

                    # 检查参数是否有效
                    if not email_id:
                        raise ValueError("Invalid parameters. Please provide valid email ID.")

                    # 调用更新邮件函数
                    result = update_email(api_key, email_id, scheduled_at)

                case EmailTools.CANCEL_EMAIL.value:
                    email_id = arguments.get("email_id")

                    # 检查参数是否有效
                    if not email_id:
                        raise ValueError("Invalid parameters. Please provide valid email ID.")

                    # 调用取消邮件
                    result = cancel_email(api_key, email_id)
                case _:
                        raise ValueError("Invalid tool name. Please provide a valid tool name.")
            
            return [
                TextContent(type="text", text=json.dumps(result, indent=2))
            ]
            
        except Exception as e:
            raise ValueError(f"Error processing tool call: {str(e)}, {result}") 

    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options)
