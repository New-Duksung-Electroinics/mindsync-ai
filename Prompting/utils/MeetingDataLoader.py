"""
회의 채팅 기록을 로드하고 처리하는 클래스

DB에서 불러온 회의 데이터를 받아 회의 주제, 발언자 정보, 안건별 발언 내역 등을 관리
주요 기능:
    - Gemini API 프롬프트 첨부용 채팅 내역 텍스트 구성
    - 토큰 수 제한에 맞춰 텍스트를 분할
"""
from collections import Counter
import itertools
import re
from Prompting.usecases.meeting_context import ChatLog, UserInfo


class MeetingDataLoader:
    def __init__(self, topic: str, agendas: dict, host: str, participants: list[UserInfo], chat_logs: list[ChatLog]):
        """
        MeetingDataLoader 클래스 생성자
        """
        self.topic = topic          # 회의 주제
        self.agendas = agendas      # 회의 안건들(번호-주제 쌍)
        self.host = host            # 회의 개최자(이메일)
        self.chats = chat_logs   # 안건별 발언 내용
        self.speaker_id_to_name = self._generate_speaker_name_map(participants)  # 발언자 ID-이름 매핑 생성
        self.ai_mbti = self.find_ai_name(participants)


    def find_ai_name(self, participants):
        """
        이메일 주소에서 @ai.com 패턴을 가진 AI 봇을 검사하여 이름 반환(MBTI)
        """
        pattern = r".*@ai\.com"  # @ai.com 패턴
        ai_name = ''
        for p in participants:
            email = p.email
            if re.search(pattern, email):
                ai_name = p.name
                break
        if ai_name != '':
            return ai_name
        else:
            return None


    def _generate_speaker_name_map(self, speakers):
        """
        발언자 ID와 이름 매핑을 생성. 동명이인 구분 처리 로직을 포함함.

        :param speakers: 발언자 목록, str list
        :return: 발언자-ID 이름 매핑, dict
        """
        org_id_to_name = {}
        for s in speakers:
            org_id_to_name[s.email] = s.name  # ID-이름 매핑(동명이인 구분되지 않은 원본)
        names = org_id_to_name.values()  # 이름 목록 추출
        counters = {name: itertools.count() for name in names}  # 동명이인 확인을 위한 카운터
        identified_names = self._append_name_identifier(names, counters)  # 동명이인 알파벳 식별자 추가
        id_to_name = dict(zip(org_id_to_name.keys(), identified_names))  # 동명이인이 식별된 ID-이름 매핑 생성
        return id_to_name

    def _append_name_identifier(self, names, counters):
        """
        동명이인이 있을 시 식별자를 추가 (식별자는 A, B, C 등 알파벳 대문자)

        :param names: 이름 목록, list
        :param counters: 동명이인 카운터, dict
        :return: 식별자가 추가된 이름 목록, list
        """
        name_counts = Counter(names)    # 이름별 등장 횟수 계산
        result = []
        for name in names:
            if name_counts[name] > 1:  # 동명이인이 존재하면
                result.append(name + chr(ord('A') + next(counters[name])))  # 식별자 추가 (A, B, C, ...)
            else:  # 동명이인이 없으면
                result.append(name)
        return result

    def process_chat_history_for_prompt(self, count_tokens_callback=None, token_alloc=None):
        """
        Gemini API 프롬프트 생성을 위한 텍스트를 구성. 토큰 수 제한을 고려하여 텍스트를 분할 가능(분할 단위는 안건별로)

        예를 들어, 총 6개의 안건에 대한 대화 내역이 있는데, 제한 토큰 수로 한 번에 보내지 못한다면,
        안건 1~3번까지를 포함하는 텍스트와 4~6번 내역을 포함하는 텍스트가 분할되어 리스트에 담김.

        :param count_tokens_callback: 토큰 수 계산 콜백 함수 (선택 사항), funtion
        :param token_alloc: (채팅 내역을 표현하는 데) 할당된 최대 토큰 수 (선택 사항), int
        :return: 프롬프트 첨부용 채팅 내역 텍스트, list
        """
        topic_str = f"회의 주제: {self.topic}\n"  # 회의 주제 문자열
        chat_string_list = self._get_sub_topic_chat_list()   # 안건별 발언 목록
        if count_tokens_callback and token_alloc:   # 토큰 수 제한에 따른 분할 처리
            return self._split_data_within_token_allocation(topic_str, chat_string_list,
                                                           count_tokens_callback, token_alloc)
        else:  # 토큰 수 제한이 없는 경우 전체 텍스트 반환
            return [topic_str + '\n'.join(chat_string_list)]

    def _split_data_within_token_allocation(self, topic_str, target_list, count_tokens_callback, token_alloc):
        """
        할당된 토큰 수 내에서 텍스트 분할. 재귀 호출 활용.

        :param topic_str: 회의 주제 문자열
        :param target_list: 분할할 텍스트 목록(=안건별 발언 목록)
        :param count_tokens_callback: 토큰 수 계산 콜백 함수, funtion
        :param token_alloc: (채팅 내역을 표현하는 데) 할당된 최대 토큰 수, int
        :return: (분할된) 프롬프트 첨부용 채팅 내역 텍스트, list
        """
        input_string = topic_str + '\n'.join(target_list)  # 전체 텍스트
        if count_tokens_callback(input_string) > token_alloc:  # 토큰 수 초과 시
            if len(target_list) == 1:  # 단일 요소도 초과하면 예외 처리(미구현)
                return input_string  # 조건 상 케이스 존재할 확률 0에 가까우므로 일단 예외 처리 미구현

            mid = len(target_list) // 2  # 중간 지점 계산
            left = self._split_data_within_token_allocation(topic_str,
                                                           target_list[:mid], count_tokens_callback, token_alloc)  # 왼쪽 부분 분할
            right = self._split_data_within_token_allocation(topic_str,
                                                            target_list[mid:], count_tokens_callback, token_alloc)  # 오른쪽 부분 분할
            return left + right  # 분할된 텍스트를 하나의 리스트에 담기
        else:
            return [input_string]   # 전체 텍스트 반환

    def _get_sub_topic_chat_list(self):
        """
        안건별 발언 목록 생성.
        """
        lines = {}
        for chat in self.chats:
            agenda_id = chat.agenda_id  # 안건 번호
            if agenda_id not in lines:
                sub_topic = self.agendas.get(agenda_id, '')  # 안건 제목
                sub_topic_str = f"안건 {agenda_id}. {sub_topic}"  # 안건 제목 문자열
                lines[agenda_id] = [sub_topic_str]

            speaker_id = chat.sender  # 발언자 ID
            msg = chat.message  # 발언 내용

            if self.host == speaker_id:  # 진행자 여부
                speaker_role = "(진행자)"
            elif speaker_id == f"{str(self.ai_mbti).lower()}@ai.com":  # ai 여부
                speaker_role = "(YOU)"
            else:
                speaker_role = ""
            speaker_name_str = self.speaker_id_to_name[speaker_id] + speaker_role  # 발언자 이름 (진행자 표기 포함)
            chat_str = f"{speaker_name_str}: {msg}"  # 발언 문자열
            lines[agenda_id].append(chat_str)

        chat_string_list = []
        for agenda_id in lines:
            sub_topic_chat = '\n'.join(lines[agenda_id])
            chat_string_list.append(sub_topic_chat)

        return chat_string_list