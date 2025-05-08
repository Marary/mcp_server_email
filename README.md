# MCP邮件服务

### 该仓库是基于MCP协议和resend开发的发送邮件的服务，可以使用该服务进行发送邮件，包括群发，并且可以通过邮件id查询邮件，更新延迟发送的邮件，以及取消延迟发送的邮件(This repository is a mail-sending service developed based on the MCP protocol and Resend. It can be used to send emails, including mass emails. Additionally, it allows querying emails by ID, updating delayed emails, and canceling delayed emails.)

## 可以做什么(What can it do)
以下参数中，`cc`、`bcc`和`to_eamil_list`为list类型，其他参数为string类型(Among the following parameters, `cc`, `bcc`, and `to_email_list` are of list type, while other parameters are of string type)
- 发送邮件(Send emails) - 发送单封邮件(Send single email)
    - 必要参数(Required parameters):
        - 收件人(Recipient): `to_email`
        - 主题(Subject): `subject`
        - 内容(Content): `body`
    - 可选参数(Optional parameters):
        - 抄送(CC): `cc`
        - 密送(BCC): `bcc`
        - 延迟发送(Delayed sending): `scheduled_at`，格式为`YYYY-MM-DDTHH:MM:SS.ssssssZ`,例如`2025-10-01T12:00:00.000000Z`，表示在2023年10月1日12点发送邮件(Format is `YYYY-MM-DDTHH:MM:SS.ssssssZ`, for example, `2025-10-01T12:00:00.000000Z`, which means sending the email at 12 o'clock on October 1, 2025)

- 群发邮件(Mass email sending) - 发送多封邮件(Send multiple emails)
    - 必要参数(Required parameters):
        - 收件人列表(Recipient list): `to_email_list`
        - 主题(Subject): `subject`
        - 内容(Content): `body`
    - 可选参数(Optional parameters):
        - 延迟发送(Delayed sending): `scheduled_at`，格式为`YYYY-MM-DDTHH:MM:SS.ssssssZ`,例如`2025-10-01T12:00:00.000000Z`，表示在2023年10月1日12点发送邮件(Format is `YYYY-MM-DDTHH:MM:SS.ssssssZ`, for example, `2025-10-01T12:00:00.000000Z`, which means sending the email at 12 o'clock on October 1, 2025)

- 查询邮件(Email query) - 查询邮件详细信息(Query email details)
    - 必要参数(Required parameters):
        - 邮件ID(Email ID): `email_id`

- 更新延迟发送的邮件(Update delayed emails) - 更新延迟发送的邮件(Update delayed emails)
    - 必要参数(Required parameters):
        - 邮件ID(Email ID): `email_id`
        - 延迟发送时间(Delayed sending time): `scheduled_at`，格式为`YYYY-MM-DDTHH:MM:SS.ssssssZ`,例如`2025-10-01T12:00:00.000000Z`，表示在2023年10月1日12点发送邮件(Format is `YYYY-MM-DDTHH:MM:SS.ssssssZ`, for example, `2025-10-01T12:00:00.000000Z`, which means sending the email at 12 o'clock on October 1, 2025)

- 取消延迟发送的邮件(Cancel delayed emails) - 取消延迟发送的邮件(Cancel delayed emails)
    - 必要参数(Required parameters):
        - 邮件ID(Email ID): `email_id`

## 使用方法(Usage)
1. 首先，将代码克隆到本地(First, clone the code to your local machine)
```bash
git clone https://github.com/Marary/mcp_server_email.git
```
2. 进入代码目录(Enter the code directory)
```bash
cd mcp_server_email
```
3. 安装依赖项(Install dependencies)
```bash
pip install -r requirements.txt
```
4. 修改MCP客户端的配置文件，我以cline为例，修改cline_mcp_settings.json文件，添加以下内容(Modify the MCP client configuration file. I will take cline as an example. Modify the cline_mcp_settings.json file and add the following content):
```json
{
  "mcpServers": {
    "sendEmail": {
      "disabled": false,
      "timeout": 60,
      "command": "python",
      "args": [
        "YOUR_FILE_PATH\\main.py",
        "--api-key",
        "YOUR_API_KEY",
        "--domain",
        "YOUR_DOMAIN",
      ],
      "transportType": "stdio"
    }
  }
}
```
上面的YOUR_FILE_PATH替换为你克隆的代码的路径(Replace YOUR_FILE_PATH with the path of the cloned code), YOUR_API_KEY替换为你在resend上申请的api_key(Replace YOUR_API_KEY with the api_key you applied for on resend), YOUR_DOMAIN替换为你在resend上申请的域名(Replace YOUR_DOMAIN with the domain name you applied for on resend).

resend的api_key和域名设置方法请参考[resend的文档](https://resend.com/docs/getting-started/quickstart)。

5. 使用服务(Use the service)

配置好以上所有内容后，就可以使用服务了(After configuring all the above content, you can use the service).

## 示例(Example)
1. 请你发送给email@example.com一封主题为请假的邮件，内容为某某某今天发烧了，不能正常工作，想要请假一天，望批准，并且帮我修饰一下辞藻，同时抄送给email2@example.com。(Please send an email to email@example.com with the subject "Leave Request". The content should state that someone is feverish today and unable to work normally, requesting a one-day leave, and hoping for approval. Also, please embellish the wording a bit and send a copy to email2@example.com.)


