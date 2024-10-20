import requests
import time

codemaoapi = "https://api.codemao.cn/web/forums/posts/{id}/{info}"
codemaouser = "https://shequ.codemao.cn/user/{userid}"
savepath = "saved_pages/{id}.html"


# 此处的 'info' 为 'details'(帖子内容)/'replies'(回复)

def get_forum_info(id, info='details', feedback=False):
    x = requests.get(codemaoapi.format(id=id, info=info))

    if feedback:
        print("{id}: {ok}".format(id=id, ok=x.ok))

    if x.ok:
        # 处理编码问题

        if feedback:
            print("{info}: {contents}".format(info=info, contents=x.json()).encode('gbk', 'ignore').decode('gbk',
                                                                                                           'ignore'))
        return x.json()

    else:
        return {}


def get_time(time_num):
    return time.strftime("%Y/%m/%d %H:%M", time.localtime(time_num))


def generate_user_link(user):
    return "<a href=\"{ulink}\">{username}<a>".format(ulink=codemaouser.format(userid=user["id"]),
                                                      username=(user["nickname"] + " (" + str(user["id"]) + ")"))


def generate_head(details):
    head_string = "<p>Board name: {board}</p>\n".format(board=details["board_name"])

    return head_string


def generate_head_comment(details):
    head_string = "{ulink}\n<pre>&#9;Updated at {time}</pre>\n<div id=\"wrap\"><p>{content}</p></div>\n".format(
        ulink=generate_user_link(details["user"]),
        content=details["content"], time=get_time(details["updated_at"]))

    return generate_head(details) + head_string


def generate_comments_of_comment(details):
    head_string = "<div id=\"wrap\"><pre>&#9;{ulink}: {content}</pre></div>\n".format(
        ulink=generate_user_link(details["user"]),
        content=details["content"])
    return head_string


def generate_comment(details):
    head_string = "{ulink}\n<pre>&#9;Updated at {time}</pre>\n<div id=\"wrap\"><p>{content}</p></div>\n".format(
        ulink=generate_user_link(details["user"]),
        content=details["content"], time=get_time(details["updated_at"]))

    connents_of_comment = details["earliest_comments"]
    for i in connents_of_comment:
        add = str(generate_comments_of_comment(i))
        if add != 'None':
            head_string = head_string + add

    return head_string


def generate_all_comments(replies):
    items = replies["items"]
    string = ""
    for i in items:
        add = str(generate_comment(i))
        if add != 'None':
            string = string + add

    return string


def save_forum_info(id, num=-1):  # 不保存头像，因为作者不会

    repstr = "replies?page={page}&limit=5"  # 读取 5条/次 回帖

    template = '''<!-->Created by ForumExplorer<!-->
<!DOCTYPE HTML>
<html>
<head>
<title>{title} -- Created by ForumExplorer</title>
</head>
<body>
{style}


{head}
<p>---以下为回帖消息---</p>
{comments}

</body>
</html>
'''

    style = """<style type="text/css">
	#wrap{
		width: 800px;
		white-space: normal; 
		word-break: break-all;
	}
</style>"""

    # 读取头部
    head = get_forum_info(id, 'details')
    head_str = ""
    title = "标题"
    if head:
        head_str = generate_head_comment(head).encode('gbk', 'ignore').decode('gbk', 'ignore')

        title = head["title"]

    if num == -1 and head:
        replies_num = head["n_replies"] // 5
    elif num == -1:
        replies_num = 1
    else:
        replies_num = num // 5

    replies_str = ""

    for i in range(1, replies_num + 1):
        replies = get_forum_info(id, repstr.format(page=i))

        if replies:
            replies_str = replies_str + generate_all_comments(replies).encode('gbk', 'ignore').decode('gbk', 'ignore')
        # print(replies_str)

    stringx = template.format(title=title, head=head_str, comments=replies_str, style=style)
    # print(stringx)

    with open(file=savepath.format(id=id), encoding="utf-8", mode="w") as file:
        file.write(stringx)

    print("帖子 {id} 已保存至 {savepath}".format(id=id, savepath=savepath.format(id=id)))


print("Fe 加载完成")
n = input('请输入帖子ID')
m = input('请输入消息数量')
m = int(m)
save_forum_info(n, m)
