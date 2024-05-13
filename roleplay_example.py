# -*- coding: utf-8 -*-
# @Date: 2024/5/13
# @Author: zhongchao
# @FileName: roleplay_example.py
import json
import re
from textwrap import dedent
from typing import Generator

from dotenv import load_dotenv
from zhipuai import ZhipuAI

load_dotenv()
from api import API_KEY, get_characterglm_response, verify_api_key_not_empty
from data_types import CharacterMeta, ImageMsg, MsgList, TextMsg, TextMsgList


def get_chatglm_response_via_sdk(messages: TextMsgList, model: str='glm-4', **kwargs) -> Generator[str, None, None]:
    """ 通过sdk调用chatglm """
    verify_api_key_not_empty()
    client = ZhipuAI(api_key=API_KEY) # 请填写您自己的APIKey
    response = client.chat.completions.create(
        model=model,  # 填写需要调用的模型名称
        messages=messages,
        stream=True,
        **kwargs
    )
    for chunk in response:
        yield chunk.choices[0].delta.content


def generate_roles_info(text_path: str, roles: str):
    """根据小说文本片段生成角色人设"""
    with open(text_path, 'r', encoding='utf-8') as f:
        data = f.read()
    system_prompt = f"""
    你是一个资深编剧，你的任务是阅读下列文本，为用户挑选的多个人物（以逗号分隔）分别生成人设描写。若文本中不包含外貌特征，身世背景和人物间关系，请你推测缺失的内容并生成人设描写。
    要求如下:
    1. 每个人物必须包含这三个部分的内容：外貌特征，身世背景和人物间关系，不要生成任何多余的内容。
    2. 每个人物的描写不要少于50字，也不要超过100字。
    3. 不能包含敏感词，人物形象需得体。
    4. 尽量用短语描写，而不是完整的句子。
    5. 返回结果为json格式，例如：{{"人物A": "人设A", "人物B": "人设B"}}

    文本如下：
    {data}
    """
    resp = get_chatglm_response_via_sdk(
        messages=[
            {'role': 'system', 'content': dedent(system_prompt).strip()},
            {'role': 'user', 'content': roles.strip()},
        ],
        temperature=0.1,
    )
    resp_txt = ''.join(resp)
    try:
        start_idx = resp_txt.find('{')
        end_idx = resp_txt.find('}')
        roles_info = json.loads(resp_txt[start_idx:end_idx+1])
        print(resp_txt[start_idx:end_idx+1])
    except Exception as e:
        print(resp_txt)
        raise e
    for role in roles.split(','):
        with open(f'corpus/{role}.info', 'w', encoding='utf-8') as f:
            f.write(roles_info[role])
    return roles_info


def roleplay(role_a: str, role_b: str, start_msg: str, rounds: int = 10, stopwords: str = ''):
    """角色扮演对话生成"""
    stop_pattern = re.compile(stopwords) if stopwords else None
    with open(f'corpus/{role_a}.info', 'r', encoding='utf-8') as fa, \
        open(f'corpus/{role_b}.info', 'r', encoding='utf-8') as fb:
        info_a = fa.read()
        info_b = fb.read()
    meta_a = {'user_name': role_a, 'user_info': info_a, 'bot_name': role_b, 'bot_info': info_b}
    meta_b = {
        'user_name': meta_a['bot_name'], 
        'user_info': meta_a['bot_info'], 
        'bot_name': meta_a['user_name'], 
        'bot_info': meta_a['user_info']
    }
    messages_a = [{'role': 'user', 'content': start_msg}]
    messages_b = [{'role': 'assistant', 'content': start_msg}]
    for _ in range(rounds):
        b_says = ''.join(get_characterglm_response(messages=messages_a, meta=meta_a))
        messages_a.append({'role': 'assistant', 'content': b_says})
        messages_b.append({'role': 'user', 'content': b_says})
        a_says = ''.join(get_characterglm_response(messages=messages_b, meta=meta_b))
        messages_a.append({'role': 'user', 'content': a_says})
        messages_b.append({'role': 'assistant', 'content': a_says})
        if stop_pattern and stop_pattern.search(a_says):
            break

    messages = []
    for msg in messages_a:
        new_msg = {'role': role_a if msg['role'] == 'user' else role_b, 'content': msg['content']}
        messages.append(new_msg)
        print(f"【{new_msg['role']}】\t{new_msg['content']}")

    with open(f'corpus/{role_a}_to_{role_b}.json', 'w', encoding='utf-8') as f:
        json.dump(messages, f, ensure_ascii=False)
    with open(f'corpus/{role_a}_to_{role_b}.md', 'w', encoding='utf-8') as f:
        f.write('```\n')
        for msg in messages:
            f.write(f"【{msg['role']}】\t{msg['content']}\n")
        f.write('```')


if __name__ == '__main__':
    # generate_roles_info('corpus/西游记第二回片段.txt', '孙悟空,菩提祖师')
    roleplay('孙悟空', '菩提祖师', start_msg='师父！', rounds=10, stopwords='谢谢')
