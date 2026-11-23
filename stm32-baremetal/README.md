# STM32F103 베어메탈 드라이버 개발

STM32F103(ARM Cortex-M3)을 HAL 라이브러리 없이 **레지스터를 직접 다뤄** 주변장치 드라이버를 구현한 C 코드입니다. 스타트업 코드(`crt0.s`), 링커 스크립트, Makefile로 직접 빌드합니다. (2025.10, 경북대학교 혁신아카데미 임베디드 과정)

## 실습 구성

| 단계 | 폴더 | 내용 |
|---|---|---|
| 빌드 환경 | `0001.COMPILE_TEST` | 크로스 컴파일·링크, 0x08003000 ROM 이미지 생성 |
| GPIO | `0401.LED_ON_LAB` ~ `0602.LED_DRIVER_LAB` | LED 제어, `volatile`·CMSIS 구조체 접근, 비트 연산 매크로, LED 드라이버 |
| 클럭 | `0701.CLOCK_CONFIG_EX` | RCC 클럭 트리 설정 |
| 키 입력 | `0801` ~ `0803` | 폴링 입력, 키 드라이버, 채터링 제거 |
| UART | `0901` ~ `0902` | 에코백, UART 드라이버·Printf |
| 타이머 | `1001` ~ `1003` | SysTick, 범용 타이머 드라이버, **PWM 부저 멜로디 재생**(TIM3 CH3, 음계별 ARR 계산·듀티 50%) |
| 인터럽트 | `1101` ~ `1106` | EXTI 인터럽트·이벤트, NVIC 우선순위·중첩, UART·타이머 인터럽트 |
| DMA | `1201` ~ `1202` | 소프트웨어 트리거·하드웨어 트리거 DMA 전송 |
| 통신·아날로그 | `1301` · `1401` · `1501` | I2C, SPI 인터페이스, ADC 변환 |
| 프로젝트 | `project1_motor_control` | UART 명령 기반 DC 모터 제어 + ADC 드라이버 |

## project1_motor_control

PC 터미널(UART 115200bps)에서 받은 명령으로 DC 모터를 제어합니다.

| 명령 | 동작 |
|---|---|
| `F` | 정회전 (CW) |
| `R` | 역회전 (CCW) |
| `S` | 정지 |
| 그 외 | `Command Error!` 출력 |

- 모터: GPIOA 2·3번 핀을 Push-Pull 출력으로 설정해 방향 신호 출력, 방향 전환 전 항상 정지(Hold)
- ADC 드라이버: 조도 센서(CdS, PB1 = ADC1 CH9)와 PA5(CH5) 채널, 239.5 사이클 샘플링, 소프트웨어 트리거 변환
- 키 드라이버: 같은 입력이 N회 연속될 때만 인정하는 방식으로 채터링 제거

```c
// 레지스터 직접 접근 예시 (adc.c)
Macro_Set_Bit(RCC->APB2ENR, 9);               // ADC1 클럭 ON
Macro_Write_Block(RCC->CFGR, 0x3, 0x2, 14);   // ADC 클럭 = PCLK2/6 = 12MHz
Macro_Write_Block(ADC1->SQR3, 0x1F, 9, 0);    // 1번 변환 채널 = CH9
Macro_Set_Bit(ADC1->CR2, 0);                  // ADC ON
```

## 폴더 구조와 빌드

- `common/`: 대부분의 실습에서 같은 파일(Makefile, `crt0.s`, 링커 스크립트, 비트 매크로 `macro.h`, `uart.c` 등)
- 각 실습 폴더: 그 실습에서 새로 작성하거나 바뀐 파일만 들어 있습니다. 같은 이름 파일이 있으면 실습 폴더 쪽이 우선입니다.

```bash
# 1) 실습 폴더에 common/ 파일 중 없는 것을 복사
cp -n common/* 1104.UART_IRQ_LAB/
# 2) ST 디바이스 헤더(stm32f10x.h)와 ARM CMSIS(core_cm3.c/h)를 같은 폴더에 추가
# 3) arm-none-eabi 툴체인 경로(Makefile의 TOOL_DIR) 확인 후 빌드
cd 1104.UART_IRQ_LAB && make
```

> `stm32f10x.h`(STMicroelectronics)와 `core_cm3.c/h`(ARM CMSIS)는 제조사 저작권 파일이라 포함하지 않았습니다. `stm32f10x_it.c`는 ST 템플릿 위에 직접 작성한 인터럽트 핸들러·폴트 리포트 코드가 들어 있어 원본 표기를 유지한 채 포함했습니다.
