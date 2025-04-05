"""
MBTI 유형별 정보를 제공하는 클래스

JSON 형식의 MBTI 유형별 정보를 로드하고, 주어진 MBTI 유형에 대한 종합적인 소개, 강점, 약점에 대한 문자열을 제공.
Gemini API 프롬프트 생성을 위한 MBTI 관련 정보를 구성하는데 활용하는 것이 목적.
"""
import json
import os

class MbtiInstructor:
    def __init__(self, instruction_file_path=None):
        """
        MbtiInstructor 클래스 생성자.
        JSON 파일에서 MBTI 유형별 정보를 로드하여 내부 데이터 구조에 저장.

        :param instruction_file_path: MBTI 정보가 담긴 JSON 파일의 경로, str
        """
        if not instruction_file_path:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            instruction_file_path = os.path.join(base_dir, "./mbti_type_instructions.json")

        with open(instruction_file_path, 'r', encoding="utf-8") as f:  # MBTI 정보가 담긴 JSON 파일 읽기
            file_string = f.read()  # 파일 내용 읽기
        self.data = json.loads(file_string)  # JSON 문자열 파싱하여 데이터 로드

    def process_mbti_info_for_prompt(self, mbti):
        """
        Gemini API 프롬프트 생성을 위한 MBTI 정보를 문자열로 구성.

        :param mbti: MBTI 유형 (예: "ISTJ", "ENFP")
        :return: MBTI 유형에 대한 소개, 강점, 약점을 포함하는 문자열
        """
        introduction = "- Overall Introduction: \n" + self.get_introduction(mbti)  # MBTI 소개
        strengths = "- Strengths: \n" + self.get_strengths(mbti)  # MBTI 강점
        weakness = "- Weaknesses: \n" + self.get_weakness(mbti)  # MBTI 약점

        return '\n'.join([introduction, strengths, weakness])  # 문자열 결합하여 반환

    def get_introduction(self, mbti):
        """
        주어진 MBTI 유형에 대한 소개를 반환.

        :param mbti: MBTI 유형
        :return: MBTI 소개 문자열
        """
        return self.data.get(mbti, {}).get("introduction", "")

    def get_strengths(self, mbti):
        """
        주어진 MBTI 유형에 대한 약점을 반환.

        :param mbti: MBTI 유형
        :return: MBTI 약점 문자열
        """
        return self.data.get(mbti, {}).get("strengths", "")

    def get_weakness(self, mbti):
        """
        주어진 MBTI 유형에 대한 약점을 반환.

        :param mbti: MBTI 유형
        :return: MBTI 약점 문자열
        """
        return self.data.get(mbti, {}).get("weakness", "")
