import json
import os
from typing import Optional
from Prompting.exceptions.errors import PromptBuildError


class MbtiTraitBuilder:
    def __init__(self, instruction_file_path: Optional[str] = None):
        """
        프롬프트 빌드에 필요한 MBTI 유형 정보 문자열을 처리하는 클래스

        Args:
            instruction_file_path: MBTI 정보가 담긴 JSON 파일의 경로
        """
        # 호출 시 특별히 지정한 설명 파일이 없으면 기본 파일 채택
        if not instruction_file_path:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            instruction_file_path = os.path.join(base_dir, "mbti_type_instructions.json")

        with open(instruction_file_path, 'r', encoding="utf-8") as f:
            self.instructions = json.loads(f.read())

    def build_trait_summary(self, mbti: str) -> str:
        """
        MBTI 정보를 프롬프트용 문자열로 조립.
        데이터의 각 key-value를 개별 section으로 조립해 유연하게 문자열 구성.

        Args:
            mbti: MBTI 유형 문자열 (예: "INFP")

        Returns:
            Args로 전달한 MBTI의 성향 정보 문자열

        Raises:
            PromptBuildError: 해당 MBTI 유형에 대한 정보 검색에 실패할 경우
        """
        profile = self.instructions.get(mbti, {})
        if not profile:
            raise PromptBuildError()

        blocks = []
        for section, text in profile.items():
            section_title = self._convert_section_title(section)
            blocks.append(f"- {section_title}:\n{text.strip()}")

        return "\n\n".join(blocks)

    def _convert_section_title(self, key: str) -> str:

        """MBTI 정보 문자열의 Section별 제목 문자열 생성"""

        # 사전 설정이 있는 key 값은 사전 설정된 제목 문자열로 매핑
        mapping = {
            "introduction": "Overall Introduction",
            "strengths": "Strengths",
            "weakness": "Weaknesses",
        }
        return mapping.get(key, key.capitalize())  # 그외 key 값은 capitalize 적용해 Section 제목화
