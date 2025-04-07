from collections import Counter
import itertools
import re
from Prompting.usecases.meeting_context import MeetingContext, UserInfo, ChatLog
from Prompting.exceptions.errors import PromptBuildError
from typing import Optional, Iterator, Callable


class MeetingHistoryBuilder:
    def __init__(self, context: MeetingContext):
        """
        프롬프트 빌드에 필요한 회의 Context 문자열을 생성하고 처리하는 클래스

        주요 기능:
         - Gemini API 프롬프트 첨부용 회의 Context 텍스트 구성
         - 토큰 수 제한에 맞춰 텍스트를 분할
        """
        self.topic: str = context.topic  # 회의 주제
        self.agendas: dict[str, str] = context.agendas  # 회의 안건들(번호-주제 쌍)
        self.host: str = context.host  # 회의 개최자(이메일)
        self.participants: list[UserInfo] = context.participants  # 회의 참여자 리스트
        self.chats: list[ChatLog] = context.chats  # 채팅 기록 리스트
        self.bot: Optional[UserInfo] = self._get_bot_info()  # AI 봇 정보
        self.email_to_name: dict[str, str] = self._generate_speaker_name_map()  # 발언자 이메일-이름 매핑 생성


    def build_prompt_chunks(
            self,
            count_tokens_callback: Optional[Callable[[str], int]] = None,
            token_alloc: Optional[int] = None) -> list[str]:
        """
        프롬프트에 첨부하기 위한 회의 Context 텍스트를 토큰 수 제한을 고려하여 분할해 리스트에 담아 반환

        Args:
            count_tokens_callback: 토큰 수 계산 콜백 함수 (선택 사항)
            token_alloc: Context에 할당된 최대 토큰 수 (선택 사항)

        Returns:
            프롬프트 첨부용 회의 Context 리스트
        """

        topic_str = f"회의 주제: {self.topic}\n"
        context_string_list = self._get_context_string_list()  # 안건별 context 문자열 리스트

        # 토큰 수 제한에 따른 분할 처리
        if count_tokens_callback and token_alloc:
            return self._split_data_within_token_allocation(
                topic_str, context_string_list, count_tokens_callback, token_alloc
            )
        else:  # 토큰 수 제한이 없는 경우 전체 텍스트 반환
            return [topic_str + '\n'.join(context_string_list)]


    def _get_bot_info(self) -> Optional[UserInfo]:
        """
        회의 참여자 목록에서 AI 봇을 찾아내 봇의 정보(UserInfo)를 반환
        """
        pattern = r".*@ai\.com"
        for p in self.participants:
            if re.search(pattern, p.email):
                return p
        return None


    def _generate_speaker_name_map(self) -> dict[str, str]:
        """
        동명이인이 식별된 회의 참여자 [이메일]-[이름] 매핑을 생성해 반환
        """
        org_id_to_name = {p.email: p.name for p in self.participants}     # 동명이인 식별 전 이메일-이름 매핑
        names = list(org_id_to_name.values())
        counters = {name: itertools.count() for name in names}            # 동명이인 확인을 위한 카운터 변수
        identified_names = self._append_name_identifier(names, counters)  # 동명이인은 알파벳 식별자 추가
        return dict(zip(org_id_to_name.keys(), identified_names))   # 동명이인이 식별된 이메일-이름 매핑 생성

    def _append_name_identifier(self, names: list[str], counters: dict[str, Iterator[int]]) -> list[str]:
        """
        이름 리스트에서 동명이인을 찾아내, 식별자(A, B, C...)를 추가한 이름 리스트를 반환

        Args:
            names: 이름 리스트
            counters: [이름]-[동명이인 수 카운팅을 위한 iterator 객체] 매핑

        Returns:
            동명이인에 식별자가 붙은 이름 리스트
        """
        name_counts = Counter(names)    # 이름별 등장 횟수 계산
        result = []
        for name in names:
            if name_counts[name] > 1:  # 동명이인이 존재하면
                result.append(name + chr(ord('A') + next(counters[name])))  # 식별자 추가 (A, B, C, ...)
            else:  # 동명이인이 없으면
                result.append(name)
        return result

    def _get_context_string_list(self):
        """
        채팅 기록을 기반으로 안건별 채팅 내역을 표현한 Context 문자열을 구성하고,
        안건 순서대로 정렬된 문자열 리스트를 반환
        """
        context_dict: dict = {}  # 안건별 context(문자열 리스트)를 관리할 딕셔너리
        for chat in self.chats:
            agenda_id = chat.agenda_id

            # 채팅이 속한 안건 ID를 기반으로 안건명 구해 제목 텍스트 설정
            if agenda_id not in context_dict:
                sub_topic = self.agendas.get(agenda_id, '')
                title = f"안건 {agenda_id}. {sub_topic}"
                context_dict[agenda_id] = [title]

            # 채팅 송신자의 역할 알아내기
            if chat.sender == self.host:  # 진행자 여부 검사
                speaker_role = "(진행자)"
            elif chat.sender == self.bot.email:  # ai 봇 여부 검사
                speaker_role = "(YOU)"
            else:
                speaker_role = ""

            speaker_name_str = self.email_to_name[chat.sender] + speaker_role
            chat_str = f"{speaker_name_str}: {chat.message}"

            context_dict[agenda_id].append(chat_str)  # 해당 안건의 context에 채팅 문자열을 추가

        # 안건별 context(문자열 리스트)를 하나의 문자열로 조인하여 리스트에 담아 반환
        return ['\n'.join(context_dict[agenda_id]) for agenda_id in sorted(context_dict.keys())]

    def _split_data_within_token_allocation(
            self, topic: str, target: list[str],
            count_tokens_callback: Callable[[str], int], token_alloc: int) -> list[str]:
        """
        재귀 호출 기반으로 할당된 토큰 수 내에서 텍스트를 분할해 리스트로 반환

        Args:
            topic_str: 회의 주제
            target_list: 안건별 Context 문자열 리스트
            count_tokens_callback: 토큰 수 계산 콜백 함수 (선택 사항)
            token_alloc: Context에 할당된 최대 토큰 수 (선택 사항)

        Returns:
            토큰 수 제한에 맞게 분할된 회의 Context 리스트
        """
        input_string = topic + '\n'.join(target)
        if count_tokens_callback(input_string) > token_alloc:  # 토큰 수 제한 초과 시
            if len(target) == 1:
                raise PromptBuildError()    # 단일 요소도 제한 초과하면 예외 처리(발생 확률 매우 희박)

            # 반으로 분할해 토큰 수 제한에 걸리면 다시 분할하도록 재귀 호출
            mid = len(target) // 2
            left = self._split_data_within_token_allocation(
                topic, target[:mid], count_tokens_callback, token_alloc
            )
            right = self._split_data_within_token_allocation(
                topic, target[mid:], count_tokens_callback, token_alloc
            )
            return left + right     # 분할 완료
        else:
            return [input_string]   # 토큰 수 제한 초과하지 않으면 전체 텍스트 반환
