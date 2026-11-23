# RoboDK·Python 자동 조립·적재 공정

RoboDK에서 현대 HH4 로봇과 OnRobot Gecko 그리퍼로 TubeType1·TubeType2 부품을 각 팔레트에서 집어 Jig에서 조립하고, 완제품을 세 번째 팔레트에 적재하는 공정 스크립트입니다. (2025.12, 2026.01 경북대학교 혁신아카데미 로봇분야 대상)

## 주요 함수
- `reset_station()`: 스테이션 초기화 후 테이블·Jig·팔레트·로봇·툴을 코드로 재구성
- `place_tubes_on_pallet_xy()`: 시작점(X0, Y0)과 간격(DX, DY)으로 3×4 격자에 부품 생성
- `pallet_grid_pose_from_reference()`: 기준 Pose를 팔레트 좌표계로 변환해 n번째 칸의 App/Grip/Drop 위치 계산
- `one_cycle_attachclosest()`: Pick → Jig → Pick → 조립 → 적재 → Home 한 사이클

## 실행
RoboDK에서 Python 프로그램을 추가하고 이 스크립트를 붙여넣어 실행합니다. 스크립트 상단의 `C:\RoboDK\Library\...` 경로가 실제 라이브러리 위치와 같아야 합니다.
